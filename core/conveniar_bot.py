"""
Automação Selenium para o portal Conveniar (facto.conveniar.com.br).

Fluxo completo por pedido:
  1. Login
  2. Clica "Todos", desmarca Empenho/Contrato e Folha Pagamento
  3. Limpa filtros de data, preenche número do pedido, clica Consultar
  4. Aguarda loader, confirma resultado, extrai nome do projeto
  5. Clica Editar para abrir o pedido
  6. Clica Recibo → Salvar em PDF → aguarda loader → fecha modal → aguarda loader
  7. Rola até gvDocumentos, encontra linha com "Comprovante de Pagamento" no nome
  8. Dispara __doPostBack via JS para baixar → aguarda loader + download
  9. Retorna ([recibo, comprovante], nome_projeto)
"""
import logging
import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import (
    CHROME_BINARY, CHROMEDRIVER_PATH,
    CONVENIAR_SENHA, CONVENIAR_URL, CONVENIAR_USUARIO, PASTA_DOWNLOADS,
)

logger = logging.getLogger(__name__)

_TIMEOUT = 30

_URL_CONSULTA = "/Fundacao/Forms/Convenio/ConsultaPedidoPagamento.aspx"

_ID_USUARIO       = "ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_UserName"
_ID_SENHA         = "ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_Password"
_ID_BTN_LOGIN     = "ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_btnLogin"
_ID_BTN_TODOS     = "ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_lbtTodos"
_ID_CHK_EMPENHO   = "ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_chkEmpenhoContrato"
_ID_CHK_FOLHA     = "ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_chkFolhaPagamento"
_ID_DATA_INI      = "ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_txtDataInicial"
_ID_DATA_FIM      = "ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_txtDataFinal"
_ID_DATA_VENC_INI = "ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_txtDataVencimentoInicial"
_ID_DATA_VENC_FIM = "ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_txtDataVencimentoFinal"
_ID_NUM_PEDIDO    = "ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_txtNumPedido"
_ID_BTN_CONSULTAR = "ctl00_ContentPlaceHolder1_ConsultaPedidoPagamentoUserControl2_btnConsultar"
_ID_LOADER        = "imgLoad"
_ID_BTN_RECIBO    = "ctl00_ContentPlaceHolder1_btnRecibo"
_ID_BTN_SALVAR_PDF = "ctl00_TelaImpressaoUserControl_btnSalvarPDF"
_ID_GV_DOCUMENTOS = (
    "ctl00_ContentPlaceHolder1_PagamentoPessoaFisicaUserControl"
    "_ArquivoPedidoUserControl1_gvDocumentos"
)

_COL_NOME_PROJETO = 6   # coluna "Nome do Projeto" na linha de resultado
_COL_NOME_ARQUIVO = 3   # coluna "Nome Arquivo" no gvDocumentos


def _criar_driver(pasta_download: str) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()

    # Só define binary_location se um caminho portátil foi configurado.
    # Sem isso, o Selenium usa o Chrome instalado normalmente no sistema.
    if CHROME_BINARY:
        chrome_path = Path(CHROME_BINARY)
        if not chrome_path.exists():
            raise FileNotFoundError(
                f"Chrome não encontrado em: {chrome_path}\n"
                "Verifique CHROME_BINARY no .env ou remova a variável para usar o Chrome do sistema."
            )
        options.binary_location = str(chrome_path)
        logger.info("Usando Chrome portátil: %s", chrome_path)
    else:
        logger.info("Usando Chrome instalado no sistema (CHROME_BINARY não configurado)")

    prefs = {
        "download.default_directory": os.path.abspath(pasta_download),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
    }
    options.add_experimental_option("prefs", prefs)
    # options.add_argument("--headless=new")

    # Só define executable_path se um chromedriver portátil foi configurado.
    # Sem isso, o Selenium Manager baixa e gerencia o chromedriver automaticamente.
    if CHROMEDRIVER_PATH:
        driver_path = Path(CHROMEDRIVER_PATH)
        if not driver_path.exists():
            raise FileNotFoundError(
                f"ChromeDriver não encontrado em: {driver_path}\n"
                "Verifique CHROMEDRIVER_PATH no .env ou remova a variável para usar o Selenium Manager."
            )
        service = Service(executable_path=str(driver_path))
        logger.info("Usando ChromeDriver portátil: %s", driver_path)
    else:
        service = Service()
        logger.info("ChromeDriver gerenciado automaticamente pelo Selenium Manager")

    return webdriver.Chrome(service=service, options=options)


def _aguardar_loader(wait: WebDriverWait) -> None:
    """Aguarda o spinner #imgLoad sumir. Chamado após TODA interação com o portal."""
    wait.until(EC.invisibility_of_element_located((By.ID, _ID_LOADER)))


def _clicar_js(driver: webdriver.Chrome, elemento) -> None:
    """Clica via JavaScript. Preferido para evitar interceptações do ASP.NET."""
    driver.execute_script("arguments[0].click();", elemento)



def _desmarcar_se_marcado(driver: webdriver.Chrome, id_checkbox: str) -> None:
    chk = driver.find_element(By.ID, id_checkbox)
    if chk.is_selected():
        _clicar_js(driver, chk)


def _limpar_campo(driver: webdriver.Chrome, id_campo: str) -> None:
    campo = driver.find_element(By.ID, id_campo)
    driver.execute_script("arguments[0].value = '';", campo)


def _confirmar_resultado_e_extrair_projeto(
    driver: webdriver.Chrome, wait: WebDriverWait, numero_pedido: str
) -> str:
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[id*='_lbtEditar']")))

    campos_cod = driver.find_elements(By.CSS_SELECTOR, "input[id*='_CodPedido']")
    if not campos_cod:
        raise ValueError(f"Nenhum resultado encontrado para o pedido {numero_pedido}")

    cod_encontrado = campos_cod[0].get_attribute("value")
    if cod_encontrado != str(numero_pedido):
        logger.warning("Pedido buscado: %s | Resultado: %s", numero_pedido, cod_encontrado)

    nome_projeto = ""
    linhas = driver.find_elements(By.CSS_SELECTOR, "tr.gridRow")
    if linhas:
        colunas = linhas[0].find_elements(By.TAG_NAME, "td")
        if len(colunas) > _COL_NOME_PROJETO:
            nome_projeto = colunas[_COL_NOME_PROJETO].text.strip()

    logger.info("Pedido %s confirmado | projeto: %s", numero_pedido, nome_projeto)
    return nome_projeto


def _fechar_modal(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    # O botão de fechar é um <a>, não <button>
    btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.ui-dialog-titlebar-close"))
    )
    btn.click()
    _aguardar_loader(wait)
    logger.info("Modal fechado")


def _aguardar_arquivo_novo(pasta: str, qtd_antes: int, timeout: int = 60) -> Path:
    pasta_path = Path(pasta)
    for _ in range(timeout):
        arquivos = [
            f for f in pasta_path.iterdir()
            if f.is_file() and f.suffix not in (".crdownload", ".tmp")
        ]
        if len(arquivos) > qtd_antes:
            return max(arquivos, key=lambda f: f.stat().st_mtime)
        # Verifica .tmp que pode ser o PDF com nome UUID (Chrome sem Content-Disposition)
        tmps = [f for f in pasta_path.iterdir() if f.is_file() and f.suffix == ".tmp"]
        if tmps:
            tmp = max(tmps, key=lambda f: f.stat().st_mtime)
            pdf = tmp.with_suffix(".pdf")
            tmp.rename(pdf)
            logger.info("Arquivo renomeado de .tmp para .pdf: %s", pdf.name)
            return pdf
        time.sleep(1)
    raise TimeoutError(f"Nenhum arquivo novo em {pasta} após {timeout}s")


def _pdf_integro(caminho: Path) -> bool:
    """Verifica header %PDF e footer %%EOF — detecta downloads truncados/corrompidos."""
    try:
        tamanho = caminho.stat().st_size
        if tamanho < 100:
            return False
        with open(caminho, "rb") as f:
            if f.read(4) != b"%PDF":
                return False
            f.seek(max(0, tamanho - 1024))
            return b"%%EOF" in f.read()
    except OSError:
        return False


def _qtd_arquivos(pasta: str) -> int:
    return len([
        f for f in Path(pasta).iterdir()
        if f.is_file() and f.suffix not in (".crdownload", ".tmp")
    ])


def _baixar_recibo(
    driver: webdriver.Chrome, wait: WebDriverWait, pasta_pedido: str
) -> str:
    """Clica em Recibo → aguarda modal abrir (até 5 tentativas) → Salvar em PDF."""
    # Aguarda o botão estar clicável antes da primeira tentativa
    wait.until(EC.element_to_be_clickable((By.ID, _ID_BTN_RECIBO)))

    # Re-busca o botão a cada tentativa para evitar referência stale.
    # Verifica visibilidade do próprio div.modal-TelaImpressao, não do btnSalvarPDF
    # que existe no DOM mesmo com o modal fechado.
    for tentativa in range(1, 6):
        btn_recibo = driver.find_element(By.ID, _ID_BTN_RECIBO)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_recibo)
        # ActionChains simula clique de mouse real — mais confiável em UpdatePanels
        ActionChains(driver).move_to_element(btn_recibo).click().perform()
        time.sleep(0.5)   # aguarda o postback ASP.NET iniciar antes de checar o loader
        _aguardar_loader(wait)
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div.modal-TelaImpressao")
                )
            )
            logger.info("Modal de recibo aberto (tentativa %d)", tentativa)
            break
        except Exception:
            logger.warning("Modal de recibo não abriu (tentativa %d/5)", tentativa)
    else:
        raise TimeoutError("Modal de recibo não abriu após 5 tentativas")

    # Aguarda o overlay interno do modal (nyroModalBg) sumir antes de clicar em Salvar PDF
    wait.until(EC.invisibility_of_element_located((By.ID, "nyroModalBg")))
    qtd = _qtd_arquivos(pasta_pedido)
    btn_pdf = wait.until(EC.visibility_of_element_located((By.ID, _ID_BTN_SALVAR_PDF)))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_pdf)
    driver.execute_script("arguments[0].click();", btn_pdf)
    _aguardar_loader(wait)

    recibo = _aguardar_arquivo_novo(pasta_pedido, qtd)
    logger.info("Recibo baixado: %s", recibo.name)

    _fechar_modal(driver, wait)
    return str(recibo)


def _baixar_comprovante(
    driver: webdriver.Chrome, wait: WebDriverWait, pasta_pedido: str
) -> str:
    """
    Rola até gvDocumentos, encontra a linha cujo nome de arquivo contém
    'Comprovante de Pagamento' e baixa via __doPostBack JS.
    """
    # Rola até a tabela de documentos
    tabela = wait.until(EC.presence_of_element_located((By.ID, _ID_GV_DOCUMENTOS)))
    driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", tabela)
    _aguardar_loader(wait)

    linhas = driver.find_elements(
        By.CSS_SELECTOR,
        f"#{_ID_GV_DOCUMENTOS} tr.gridRow, #{_ID_GV_DOCUMENTOS} tr.gridAlternateRow"
    )

    for linha in linhas:
        colunas = linha.find_elements(By.TAG_NAME, "td")
        if len(colunas) <= _COL_NOME_ARQUIVO:
            continue
        nome_arquivo = colunas[_COL_NOME_ARQUIVO].text.strip()
        if "Comprovante de Pagamento" not in nome_arquivo:
            continue

        btn_baixar = linha.find_element(By.CSS_SELECTOR, "a[id*='_lbtBaixar']")

        qtd = _qtd_arquivos(pasta_pedido)

        # Clique normal: o browser executa o javascript:__doPostBack(...) do href
        # fora do contexto strict do execute_script (que falha no Chrome 146+).
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_baixar)
        btn_baixar.click()
        _aguardar_loader(wait)
        comprovante = _aguardar_arquivo_novo(pasta_pedido, qtd)
        logger.info("Comprovante baixado: %s", comprovante.name)
        return str(comprovante)

    raise ValueError("Nenhuma linha com 'Comprovante de Pagamento' encontrada em gvDocumentos")


def baixar_arquivos_pedido(numero_pedido: str) -> tuple[list[str], str]:
    """
    Acessa o Conveniar, busca o pedido e baixa:
      1. Recibo (gerado via botão Recibo → Salvar em PDF)
      2. Comprovante de Pagamento (linha do gvDocumentos)

    Retorna (lista_arquivos, nome_projeto).
    """
    # Substitui / e \ por - para evitar subpastas indesejadas (ex: 77059/2025 → 77059-2025)
    pasta_nome = str(numero_pedido).replace("/", "-").replace("\\", "-")
    pasta_pedido = str(PASTA_DOWNLOADS / pasta_nome)
    os.makedirs(pasta_pedido, exist_ok=True)

    # Se os dois arquivos já existirem e estiverem íntegros, pula o download
    recibo_existente      = Path(pasta_pedido) / "Recibo de Pagamento.pdf"
    comprovante_existente = Path(pasta_pedido) / "Comprovante de Pagamento.pdf"
    if recibo_existente.exists() and comprovante_existente.exists():
        if _pdf_integro(recibo_existente) and _pdf_integro(comprovante_existente):
            logger.info("Pedido %s — arquivos íntegros já existem, download ignorado", numero_pedido)
            return [str(recibo_existente), str(comprovante_existente)], ""
        logger.warning(
            "Pedido %s — arquivo(s) corrompido(s), removendo para re-download", numero_pedido
        )
        recibo_existente.unlink(missing_ok=True)
        comprovante_existente.unlink(missing_ok=True)

    driver = _criar_driver(pasta_pedido)
    wait = WebDriverWait(driver, _TIMEOUT)

    try:
        # 1. Login
        url_consulta = CONVENIAR_URL.rstrip("/") + _URL_CONSULTA
        driver.get(url_consulta)
        logger.info("Acessando: %s", url_consulta)

        wait.until(EC.presence_of_element_located((By.ID, _ID_USUARIO)))
        driver.find_element(By.ID, _ID_USUARIO).send_keys(CONVENIAR_USUARIO)
        driver.find_element(By.ID, _ID_SENHA).send_keys(CONVENIAR_SENHA)
        _clicar_js(driver, driver.find_element(By.ID, _ID_BTN_LOGIN))
        _aguardar_loader(wait)
        logger.info("Login efetuado")

        # 2. Configuração dos filtros
        wait.until(EC.presence_of_element_located((By.ID, _ID_BTN_TODOS)))
        _aguardar_loader(wait)

        _clicar_js(driver, driver.find_element(By.ID, _ID_BTN_TODOS))
        _aguardar_loader(wait)

        _desmarcar_se_marcado(driver, _ID_CHK_EMPENHO)
        _desmarcar_se_marcado(driver, _ID_CHK_FOLHA)

        for id_campo in (_ID_DATA_INI, _ID_DATA_FIM, _ID_DATA_VENC_INI, _ID_DATA_VENC_FIM):
            _limpar_campo(driver, id_campo)

        # 3. Consulta pelo número do pedido
        campo_pedido = driver.find_element(By.ID, _ID_NUM_PEDIDO)
        driver.execute_script("arguments[0].value = '';", campo_pedido)
        campo_pedido.send_keys(str(numero_pedido))
        _clicar_js(driver, driver.find_element(By.ID, _ID_BTN_CONSULTAR))
        _aguardar_loader(wait)
        logger.info("Consulta concluída para pedido %s", numero_pedido)

        # 4. Confirma resultado e extrai nome do projeto
        nome_projeto = _confirmar_resultado_e_extrair_projeto(driver, wait, numero_pedido)

        # 5. Abre o pedido via Editar (abre em nova aba)
        aba_consulta = driver.current_window_handle
        btn_editar = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[id*='_lbtEditar']"))
        )
        _clicar_js(driver, btn_editar)

        # Aguarda a segunda aba abrir e muda para ela
        wait.until(lambda d: len(d.window_handles) > 1)
        aba_pedido = [h for h in driver.window_handles if h != aba_consulta][0]
        driver.switch_to.window(aba_pedido)

        # Aguarda a página carregar completamente antes de qualquer interação
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        _aguardar_loader(wait)
        logger.info("Pedido %s aberto na segunda aba", numero_pedido)

        # 6. Baixa o recibo e renomeia para nome legível
        recibo_tmp = Path(_baixar_recibo(driver, wait, pasta_pedido))
        recibo_path = recibo_tmp.rename(recibo_tmp.parent / "Recibo de Pagamento.pdf")
        logger.info("Recibo renomeado para: Recibo de Pagamento.pdf")
        if not _pdf_integro(recibo_path):
            recibo_path.unlink(missing_ok=True)
            raise ValueError(f"Recibo corrompido para o pedido {numero_pedido} — download será repetido na próxima execução")
        _aguardar_loader(wait)  # garante que a página assentou após fechar o modal

        # 7. Baixa o comprovante e renomeia para nome legível
        comprovante_tmp = Path(_baixar_comprovante(driver, wait, pasta_pedido))
        comprovante_path = comprovante_tmp.rename(comprovante_tmp.parent / "Comprovante de Pagamento.pdf")
        logger.info("Comprovante renomeado para: Comprovante de Pagamento.pdf")
        if not _pdf_integro(comprovante_path):
            comprovante_path.unlink(missing_ok=True)
            raise ValueError(f"Comprovante corrompido para o pedido {numero_pedido} — download será repetido na próxima execução")

        # Fecha a aba do pedido e volta para a aba de consulta
        driver.close()
        driver.switch_to.window(aba_consulta)
        logger.info("Voltou para a aba de consulta")

        arquivos = [str(recibo_path), str(comprovante_path)]
        logger.info("Pedido %s concluído — %d arquivo(s) íntegros", numero_pedido, len(arquivos))
        return arquivos, nome_projeto

    except Exception:
        logger.exception("Erro ao processar pedido %s", numero_pedido)
        raise
    finally:
        driver.quit()
