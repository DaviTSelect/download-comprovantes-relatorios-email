"""Atualizador automático — verifica o GitHub Releases e substitui o .exe silenciosamente.

Fluxo:
  1. App abre → thread de fundo chama ``verificar_e_instalar()``
  2. Se há versão nova: baixa, valida SHA-256, agenda troca via PowerShell e fecha o app
  3. PowerShell aguarda o processo encerrar, faz o swap e reinicia o novo .exe

Adaptado do template corporativo (spec 06_ATUALIZACAO).
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

from version import REPOSITORY, VERSION

logger = logging.getLogger(__name__)

NOME_EXE    = "AutomacaoConveniarEmail.exe"
_USER_AGENT = "AutomacaoConveniarEmail-updater/1.0"

# Script PowerShell: aguarda o processo fechar, troca o EXE e reinicia.
_SCRIPT_TROCA = r'''param([string]$Origem, [string]$Destino, [int]$PIDAntigo)
$ErrorActionPreference = 'Stop'
try { Wait-Process -Id $PIDAntigo -ErrorAction SilentlyContinue } catch {}
$Backup = "$Destino.bak"
if (Test-Path -LiteralPath $Backup) {
    if (-not (Test-Path -LiteralPath $Destino)) {
        Move-Item -LiteralPath $Backup -Destination $Destino
    }
    throw "Backup preexistente; atualização cancelada para preservar a recuperação."
}
for ($tentativa = 0; $tentativa -lt 60; $tentativa++) {
    $NovoNoDestino = $false
    try {
        if (Test-Path -LiteralPath $Destino) { Move-Item -LiteralPath $Destino -Destination $Backup }
        Move-Item -LiteralPath $Origem -Destination $Destino
        $NovoNoDestino = $true
        $ProcessoNovo = Start-Process -FilePath $Destino -WindowStyle Normal -PassThru
        Start-Sleep -Seconds 3
        $ProcessoNovo.Refresh()
        if ($ProcessoNovo.HasExited) { throw "Novo executável encerrou durante a verificação inicial." }
        if (Test-Path -LiteralPath $Backup) { Remove-Item -LiteralPath $Backup -Force -ErrorAction SilentlyContinue }
        exit 0
    } catch {
        if ($NovoNoDestino -and (Test-Path -LiteralPath $Destino)) {
            Remove-Item -LiteralPath $Destino -Force
        }
        if (-not (Test-Path -LiteralPath $Destino) -and (Test-Path -LiteralPath $Backup)) {
            Move-Item -LiteralPath $Backup -Destination $Destino
        }
        Start-Sleep -Seconds 1
    }
}
if (-not (Test-Path -LiteralPath $Destino) -and (Test-Path -LiteralPath $Backup)) {
    Move-Item -LiteralPath $Backup -Destination $Destino
}
if (Test-Path -LiteralPath $Destino) { Start-Process -FilePath $Destino -WindowStyle Normal }
exit 1
'''


def _versao(tag: str) -> tuple[int, ...]:
    v = tag.removeprefix("v")
    if not v or any(not p.isdigit() for p in v.split(".")):
        raise ValueError(f"Versão inválida: {tag!r}. Use formato numérico, ex.: v1.2.3")
    return tuple(int(p) for p in v.split("."))


def pode_instalar() -> bool:
    """Retorna True apenas quando rodando como .exe PyInstaller no Windows."""
    return sys.platform == "win32" and bool(getattr(sys, "frozen", False))


def buscar_release() -> dict:
    url = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": _USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.load(resp)


def tem_versao_nova(release: dict) -> bool:
    return _versao(release["tag_name"]) > _versao(VERSION)


def _obter_hash_sha256(assets: list[dict]) -> str:
    """Obtém o SHA-256 do asset do EXE.

    Tenta em ordem:
      1. Campo ``digest`` do asset (formato ``sha256:<hex>``) — GitHub API v2022-11-28+
      2. Asset separado ``<NOME_EXE>.sha256`` — gerado pelo workflow de release
    """
    asset_exe = next((a for a in assets if a["name"] == NOME_EXE), None)
    if asset_exe:
        digest = asset_exe.get("digest", "")
        if isinstance(digest, str) and digest.startswith("sha256:"):
            h = digest.removeprefix("sha256:").lower()
            if len(h) == 64 and all(c in "0123456789abcdef" for c in h):
                return h

    nome_sha = NOME_EXE.replace(".exe", ".sha256")
    asset_sha = next(
        (a for a in assets if a["name"] in (nome_sha, NOME_EXE + ".sha256")), None
    )
    if asset_sha:
        req = urllib.request.Request(
            asset_sha["browser_download_url"], headers={"User-Agent": _USER_AGENT}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            conteudo = resp.read().decode().strip().split()[0].lower()
            if len(conteudo) == 64 and all(c in "0123456789abcdef" for c in conteudo):
                return conteudo

    raise RuntimeError(
        "SHA-256 não encontrado para o asset — verifique o workflow de release."
    )


def instalar(release: dict) -> None:
    """Baixa o novo .exe, valida SHA-256 e agenda a troca via PowerShell."""
    assets = release.get("assets", [])
    asset_exe = next((a for a in assets if a["name"] == NOME_EXE), None)
    if asset_exe is None:
        raise RuntimeError(f"Release não contém o asset '{NOME_EXE}'")

    hash_esperado = _obter_hash_sha256(assets)

    exe_atual = Path(sys.executable).resolve()
    if exe_atual.name.lower() != NOME_EXE.lower():
        raise RuntimeError(f"Executável instalado deve se chamar '{NOME_EXE}'")

    pasta = Path(tempfile.mkdtemp(prefix="app_update_"))
    baixado = pasta / NOME_EXE
    _baixar_exe(asset_exe["browser_download_url"], baixado, hash_esperado)
    _agendar_troca(pasta, baixado, exe_atual)


def _baixar_exe(url: str, destino: Path, hash_esperado: str) -> None:
    h = hashlib.sha256()
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp, open(destino, "wb") as f:
            while bloco := resp.read(1_048_576):
                f.write(bloco)
                h.update(bloco)
        if h.hexdigest() != hash_esperado:
            raise RuntimeError("SHA-256 do arquivo baixado não confere — download corrompido")
    except Exception:
        destino.unlink(missing_ok=True)
        raise


def _agendar_troca(pasta: Path, baixado: Path, exe_atual: Path) -> None:
    script = pasta / "trocar.ps1"
    script.write_text(_SCRIPT_TROCA, encoding="utf-8-sig")
    subprocess.Popen(
        [
            "powershell.exe", "-NoProfile", "-NonInteractive",
            "-ExecutionPolicy", "Bypass",
            "-File", str(script),
            "-Origem", str(baixado),
            "-Destino", str(exe_atual),
            "-PIDAntigo", str(os.getpid()),
        ],
        creationflags=subprocess.CREATE_NO_WINDOW,
        close_fds=True,
        env={**os.environ, "PYINSTALLER_RESET_ENVIRONMENT": "1"},
    )


def verificar_e_instalar() -> str:
    """Verifica e instala atualização silenciosamente. Chamar em thread de fundo.

    Retornos:
    - ``"atualizado"``      — já está na versão mais recente
    - ``"atualizando"``     — download feito; app deve fechar para a troca ocorrer
    - ``"nova_versao:vX"``  — versão nova mas rodando como script (sem .exe), só loga
    - ``"sem_conexao"``     — sem internet; não bloqueia o usuário
    - ``"erro:<msg>"``      — falha inesperada; registrada em log
    """
    try:
        release = buscar_release()
        if not tem_versao_nova(release):
            logger.debug("Auto-update: já na versão mais recente (%s)", VERSION)
            return "atualizado"
        nova = release["tag_name"]
        logger.info("Auto-update: nova versão disponível %s → %s", VERSION, nova)
        if pode_instalar():
            instalar(release)
            logger.info("Auto-update: troca agendada, encerrando para aplicar %s", nova)
            return "atualizando"
        logger.info("Auto-update: versão %s disponível (modo script, sem troca)", nova)
        return f"nova_versao:{nova}"
    except OSError:
        logger.debug("Auto-update: sem conexão, verificação ignorada")
        return "sem_conexao"
    except Exception as exc:
        logger.warning("Auto-update falhou: %s", exc)
        return f"erro:{exc}"
