"""Interface gráfica PySide6 para a Automação Conveniar Email.

Como a janela está organizada:
- SelectionRow seleciona a planilha de pedidos.
- TabelaPedidos exibe os dados carregados e o status em tempo real.
- A thread de processamento fala com a tela apenas via sinais.
"""
from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import NamedTuple

import openpyxl
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QFileDialog, QFrame,
    QGraphicsDropShadowEffect, QHBoxLayout, QHeaderView, QLabel,
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from config import USER_EMAIL
from core.conveniar_bot import baixar_arquivos_pedido
from core.send_email import enviar_email
from version import VERSION

# ── Paleta idêntica ao padrão corporativo ────────────────────────────────────
BG  = '#203447'
TEXT = '#efede5'
ACTION = '#e94c1f'
COR_DIVISOR_ESCURO = '#415364'
COR_ICONE = '#7a8791'
COR_SELECIONADO = '#317458'

ESTILO_FUNDO_ICONE  = 'background:#e9eef0; border-radius:12px;'
ESTILO_FUNDO_ICONE_OK = 'background:#e5f4ed; border-radius:12px;'
ESTILO_BOTAO_LINHA = '''QPushButton {background:#ffffff; border:1px solid #d9dddc;
    border-radius:9px; color:#344a5b; font-family:"Segoe UI"; font-size:11px;
    font-weight:600; padding:0 12px;}
    QPushButton:hover {background:#f1f3f1; border-color:#b5bec3;}'''
ESTILO_INICIAR_ATIVO = f'''QPushButton {{background:{ACTION}; color:white; border:none;
    border-radius:9px; font:600 11px "Segoe UI"; padding:0 19px;}}
    QPushButton:hover {{background:#d74118;}}'''
ESTILO_INICIAR_INATIVO = '''QPushButton {background:#d8dad9; color:#92999b; border:none;
    border-radius:9px; font:600 11px "Segoe UI"; padding:0 19px;}'''

# ── Status ────────────────────────────────────────────────────────────────────
ST_PENDENTE  = 'Pendente'
ST_BAIXANDO  = 'Baixando...'
ST_ENVIANDO  = 'Enviando...'
ST_ENVIADO   = 'Enviado'
ST_ERRO      = 'Erro'

_COR_ST = {
    ST_PENDENTE: ('#f1f1ed', '#8c929a'),
    ST_BAIXANDO: ('#fff8e1', '#c47f00'),
    ST_ENVIANDO: ('#e8f0fb', '#2563a8'),
    ST_ENVIADO:  ('#e5f4ed', '#317458'),
    ST_ERRO:     ('#fde8e4', '#c0351a'),
}


class Pedido(NamedTuple):
    numero_pedido: str
    email: str
    nome_projeto: str


# ── Componentes visuais (padrão corporativo) ──────────────────────────────────

class Icon(QWidget):
    def __init__(self, kind, color=COR_ICONE, size=24, parent=None):
        super().__init__(parent)
        self.kind, self.color = kind, color
        self.setFixedSize(size, size)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(self.width() / 24, self.height() / 24)
        pen = QPen(QColor(self.color), 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen); p.setBrush(Qt.NoBrush)
        if self.kind in ('folder', 'save'):
            self._pasta(p, seta=self.kind == 'save')
        elif self.kind == 'file':
            self._arquivo(p)
        elif self.kind == 'check':
            pen.setWidthF(2); p.setPen(pen); self._check(p)
        p.end()

    @staticmethod
    def _ln(p, x1, y1, x2, y2):
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _pasta(self, p, seta):
        path = QPainterPath()
        path.moveTo(3.75, 16.25); path.lineTo(3.75, 6.75)
        path.cubicTo(3.75, 5.65, 4.65, 4.75, 5.75, 4.75)
        path.lineTo(9.11, 4.75); path.lineTo(11.91, 7.75); path.lineTo(18.25, 7.75)
        path.cubicTo(19.35, 7.75, 20.25, 8.65, 20.25, 9.75); path.lineTo(20.25, 16.25)
        path.cubicTo(20.25, 18, 19, 19.25, 17.25, 19.25); path.lineTo(6.75, 19.25)
        path.cubicTo(5, 19.25, 3.75, 18, 3.75, 16.25); p.drawPath(path)
        if seta:
            self._ln(p, 12, 10.5, 12, 15.5)
            self._ln(p, 10, 13.5, 12, 15.5)
            self._ln(p, 14, 13.5, 12, 15.5)

    def _arquivo(self, p):
        path = QPainterPath()
        path.moveTo(7, 3.75); path.lineTo(13.17, 3.75); path.lineTo(18, 8.58)
        path.lineTo(18, 20.25); path.lineTo(7, 20.25)
        path.cubicTo(5.7, 20.25, 5, 19.4, 5, 18.25)
        path.lineTo(5, 5.75); path.cubicTo(5, 4.6, 5.8, 3.75, 7, 3.75); p.drawPath(path)
        self._ln(p, 13.5, 4, 13.5, 8.5); self._ln(p, 13.5, 8.5, 18, 8.5)
        self._ln(p, 8.5, 13, 15.25, 13); self._ln(p, 8.5, 16.5, 13.25, 16.5)

    @staticmethod
    def _check(p):
        path = QPainterPath()
        path.moveTo(6.75, 12.25); path.lineTo(10, 15.5); path.lineTo(17.25, 8.25)
        p.drawPath(path)


def _rotulo(text, size, color, weight=QFont.Normal, wrap=False):
    w = QLabel(text)
    f = QFont('Segoe UI', size); f.setWeight(weight)
    w.setFont(f)
    w.setStyleSheet(f'color:{color}; background:transparent;')
    w.setWordWrap(wrap)
    return w


def _divisor(color):
    d = QFrame(); d.setFixedHeight(1)
    d.setStyleSheet(f'background:{color}; border:none;')
    return d


class SelectionRow(QFrame):
    def __init__(self, number, title, desc, btn_text, icon_kind, callback):
        super().__init__()
        self.btn_text = btn_text; self.icon_kind = icon_kind
        self.setObjectName('selRow')
        self.setStyleSheet('#selRow {background:transparent; border:none;}')
        self.setMinimumHeight(110)
        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 18, 16, 18); outer.setSpacing(12)
        self.icon_box = QFrame()
        self.icon_box.setFixedSize(43, 43)
        self.icon_box.setStyleSheet(ESTILO_FUNDO_ICONE)
        self.icon_lay = QHBoxLayout(self.icon_box)
        self.icon_lay.setContentsMargins(0, 0, 0, 0)
        self.icon_lay.addWidget(Icon(icon_kind))
        outer.addWidget(self.icon_box, 0, Qt.AlignTop)
        outer.addLayout(self._textos(number, title, desc), 1)
        self.btn = QPushButton(btn_text)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setMinimumWidth(126); self.btn.setFixedHeight(39)
        self.btn.setStyleSheet(ESTILO_BOTAO_LINHA)
        self.btn.clicked.connect(callback)
        outer.addWidget(self.btn, 0, Qt.AlignVCenter)

    def _textos(self, number, title, desc):
        col = QVBoxLayout(); col.setSpacing(0); col.setContentsMargins(0, 1, 0, 0)
        head = QHBoxLayout(); head.setSpacing(9); head.setContentsMargins(0, 0, 0, 0)
        head.addWidget(_rotulo('ETAPA ' + number, 9, '#7b8791', QFont.Bold))
        self.badge = _rotulo('SELECIONADO', 8, COR_SELECIONADO, QFont.Bold)
        self.badge.setStyleSheet(f'color:{COR_SELECIONADO}; background:#e5f4ed; border-radius:9px; padding:3px 8px;')
        self.badge.hide(); head.addWidget(self.badge); head.addStretch()
        col.addLayout(head); col.addSpacing(6)
        col.addWidget(_rotulo(title, 12, BG, QFont.DemiBold)); col.addSpacing(5)
        col.addWidget(_rotulo(desc, 10, '#6d7780', wrap=True))
        self.valor = _rotulo('', 10, '#344b5e', QFont.Medium); self.valor.hide()
        col.addSpacing(4); col.addWidget(self.valor); col.addStretch()
        return col

    def definir_valor(self, value):
        ok = bool(value)
        self.badge.setVisible(ok)
        self.valor.setText(value); self.valor.setToolTip(value); self.valor.setVisible(ok)
        self.btn.setText('Alterar' if ok else self.btn_text)
        old = self.icon_lay.takeAt(0)
        if old and old.widget(): old.widget().deleteLater()
        self.icon_lay.addWidget(Icon('check' if ok else self.icon_kind,
                                     COR_SELECIONADO if ok else COR_ICONE))
        self.icon_box.setStyleSheet(ESTILO_FUNDO_ICONE_OK if ok else ESTILO_FUNDO_ICONE)


class TabelaPedidos(QFrame):
    """Tabela com os pedidos e a coluna de status atualizada em tempo real."""

    COLS = ['Nº Pedido', 'E-mail', 'Nome do Projeto', 'Status']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background:transparent; border:none;')
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 4, 16, 8); lay.setSpacing(6)
        lay.addWidget(_rotulo('Pedidos carregados', 10, BG, QFont.DemiBold))

        self.tbl = QTableWidget(0, len(self.COLS))
        self.tbl.setHorizontalHeaderLabels(self.COLS)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.horizontalHeader().setHighlightSections(False)
        self.tbl.setShowGrid(False)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setMinimumHeight(140)
        self.tbl.setMaximumHeight(280)
        self.tbl.setStyleSheet('''
            QTableWidget {background:#f8f7f3; border:1px solid #dde1df;
                border-radius:8px; font-family:"Segoe UI"; font-size:10px;}
            QTableWidget::item {padding:5px 10px; color:#344a5b; border:none;}
            QTableWidget::item:selected {background:#e3ede9; color:#203447;}
            QTableWidget::item:alternate {background:#f1f1ed;}
            QHeaderView::section {background:#edecea; color:#68747d; font-weight:600;
                font-size:9px; font-family:"Segoe UI"; padding:5px 10px;
                border:none; border-bottom:1px solid #dde1df;}
        ''')
        hdr = self.tbl.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        lay.addWidget(self.tbl)

    def carregar(self, pedidos: list[Pedido]) -> None:
        self.tbl.setRowCount(0)
        for pedido in pedidos:
            r = self.tbl.rowCount()
            self.tbl.insertRow(r)
            self.tbl.setRowHeight(r, 34)
            self.tbl.setItem(r, 0, QTableWidgetItem(pedido.numero_pedido))
            self.tbl.setItem(r, 1, QTableWidgetItem(pedido.email))
            self.tbl.setItem(r, 2, QTableWidgetItem(pedido.nome_projeto))
            self._set_status(r, ST_PENDENTE)

    def atualizar_status(self, row: int, status: str) -> None:
        self._set_status(row, status)

    def _set_status(self, row: int, status: str) -> None:
        item = QTableWidgetItem(status)
        item.setTextAlignment(Qt.AlignCenter)
        bg, fg = _COR_ST.get(status, ('#f1f1ed', '#8c929a'))
        item.setBackground(QColor(bg)); item.setForeground(QColor(fg))
        f = QFont('Segoe UI', 9); f.setWeight(QFont.Medium); item.setFont(f)
        self.tbl.setItem(row, 3, item)


# ── Janela principal ──────────────────────────────────────────────────────────

class App(QWidget):
    sinal_baixando        = Signal(int)        # row → Baixando...
    sinal_enviando        = Signal(int)        # row → Enviando...
    sinal_pedido_concluido = Signal(int)       # row → Enviado
    sinal_pedido_falhou   = Signal(int, str)   # row, msg → Erro
    sinal_tarefa_concluida = Signal(int, int)  # total, sucessos
    sinal_tarefa_falhou   = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'Automação Conveniar Email — v{VERSION}')
        self.resize(1180, 720)
        self.setMinimumSize(880, 640)
        self.planilha_path = ''
        self.pedidos: list[Pedido] = []
        self.started = False
        self.setStyleSheet(f'background:{BG};')

        root = QVBoxLayout(self)
        root.setContentsMargins(48, 24, 48, 26); root.setSpacing(0)
        self._cabecalho(root)
        center = QHBoxLayout(); center.setSpacing(65)
        center.addLayout(self._painel_esquerdo(), 5)
        center.addWidget(self._cartao(), 9)
        root.addLayout(center, 1)
        self._rodape(root)

        self.sinal_baixando.connect(lambda r: self.tabela_widget.atualizar_status(r, ST_BAIXANDO))
        self.sinal_enviando.connect(lambda r: self.tabela_widget.atualizar_status(r, ST_ENVIANDO))
        self.sinal_pedido_concluido.connect(self._ao_concluir_pedido)
        self.sinal_pedido_falhou.connect(self._ao_falhar_pedido)
        self.sinal_tarefa_concluida.connect(self._ao_concluir_tudo)
        self.sinal_tarefa_falhou.connect(self._ao_falhar_tudo)
        self._atualizar_estado()

    # ── Montagem ──────────────────────────────────────────────────────────────

    def _cabecalho(self, root):
        hdr = QHBoxLayout()
        left = QVBoxLayout(); left.setSpacing(5)
        left.addWidget(_rotulo('G E S T Ã O   O P E R A C I O N A L', 9, '#85929c', QFont.Bold))
        left.addWidget(_rotulo('Automação Conveniar Email', 14, TEXT, QFont.DemiBold))
        hdr.addLayout(left); hdr.addStretch()
        hdr.addWidget(_rotulo(f'v{VERSION}', 10, '#7a8791', QFont.Medium))
        root.addLayout(hdr)
        root.addSpacing(20)
        root.addWidget(_divisor(COR_DIVISOR_ESCURO))

    def _painel_esquerdo(self):
        left = QVBoxLayout(); left.setContentsMargins(0, 0, 0, 0); left.setSpacing(0)
        left.addStretch()
        left.addWidget(_rotulo('A U T O M A Ç Ã O   C O N V E N I A R', 9, ACTION, QFont.Bold))
        left.addSpacing(20)
        left.addWidget(_rotulo('Envie comprovantes\nautomaticamente.', 29, TEXT, QFont.DemiBold, True))
        left.addSpacing(22)
        intro = _rotulo(
            'Carregue a planilha com os pedidos. O sistema irá buscar o recibo e o '
            'comprovante de pagamento no Conveniar e enviar para cada destinatário.',
            12, '#a5afb6', wrap=True,
        )
        intro.setMinimumWidth(270); intro.setMaximumWidth(365)
        left.addWidget(intro)
        left.addSpacing(37)
        left.addWidget(_divisor(COR_DIVISOR_ESCURO))
        left.addSpacing(24)
        sec = QHBoxLayout(); sec.setSpacing(14)
        circle = QFrame(); circle.setFixedSize(34, 34)
        circle.setStyleSheet('background:#304658; border-radius:17px;')
        cl = QHBoxLayout(circle); cl.setContentsMargins(5, 5, 5, 5)
        cl.addWidget(Icon('file', '#a6b4bd', 20))
        sec.addWidget(circle, 0, Qt.AlignTop)
        sec.addWidget(_rotulo('Seus arquivos são processados localmente e não são compartilhados.', 10, '#8998a3', wrap=True), 1)
        left.addLayout(sec)
        left.addStretch()
        return left

    def _cartao(self):
        card = QFrame(); card.setObjectName('card')
        card.setStyleSheet('#card {background:#f8f7f3; border-radius:18px;}')
        sombra = QGraphicsDropShadowEffect(card)
        sombra.setBlurRadius(52); sombra.setOffset(0, 22)
        sombra.setColor(QColor(6, 18, 28, 80)); card.setGraphicsEffect(sombra)
        lay = QVBoxLayout(card); lay.setSpacing(0); lay.setContentsMargins(0, 0, 0, 0)
        self._titulo_cartao(lay)
        lay.addWidget(_divisor('#dde1df'))
        self._corpo_cartao(lay)
        self._rodape_cartao(lay)
        return card

    def _titulo_cartao(self, lay):
        top = QHBoxLayout(); top.setContentsMargins(30, 20, 30, 16)
        titles = QVBoxLayout(); titles.setSpacing(5)
        titles.addWidget(_rotulo('Configurar automação', 14, BG, QFont.DemiBold))
        self.subtitle = _rotulo('Selecione a planilha para começar', 10, '#7a838a')
        titles.addWidget(self.subtitle)
        top.addLayout(titles); top.addStretch()
        self.badge_total = _rotulo('0 pedidos', 9, '#68747d', QFont.Bold)
        self.badge_total.setStyleSheet('color:#68747d; background:transparent; border:1px solid #d9dddc; border-radius:12px; padding:7px 12px;')
        top.addWidget(self.badge_total)
        lay.addLayout(top)

    def _corpo_cartao(self, lay):
        self.row_planilha = SelectionRow(
            '01', 'Planilha de pedidos',
            'Selecione o arquivo .xlsx com as colunas: numero_pedido, email, nome_projeto.',
            'Selecionar planilha', 'save', self.escolher_planilha,
        )
        lay.addWidget(self.row_planilha)
        self.div_tabela = _divisor('#e3e5e2')
        self.div_tabela.hide()
        lay.addWidget(self.div_tabela)
        self.tabela_widget = TabelaPedidos()
        self.tabela_widget.hide()
        lay.addWidget(self.tabela_widget)
        lay.addStretch()

    def _rodape_cartao(self, lay):
        footer = QFrame()
        footer.setStyleSheet('background:#f1f1ed; border-bottom-left-radius:18px; border-bottom-right-radius:18px;')
        fl = QHBoxLayout(footer); fl.setContentsMargins(30, 20, 30, 20)
        texts = QVBoxLayout(); texts.setSpacing(5)
        self.ready_title = _rotulo('Aguardando planilha', 10, '#344a5b', QFont.DemiBold)
        self.ready_hint  = _rotulo('Selecione a planilha com os pedidos para continuar.', 9, '#838c91', wrap=True)
        texts.addWidget(self.ready_title); texts.addWidget(self.ready_hint)
        fl.addLayout(texts, 1)
        self.start = QPushButton('Aguardando planilha')
        self.start.setFixedHeight(46); self.start.setMinimumWidth(190)
        self.start.setCursor(Qt.PointingHandCursor)
        self.start.clicked.connect(self.iniciar_tarefa)
        fl.addWidget(self.start)
        lay.addWidget(footer)

    def _rodape(self, root):
        root.addWidget(_divisor(COR_DIVISOR_ESCURO)); root.addSpacing(17)
        bot = QHBoxLayout()
        bot.addWidget(_rotulo('Automação Conveniar Email', 9, '#83919c'))
        bot.addStretch()
        bot.addWidget(_rotulo('Ambiente seguro · Facto', 9, '#83919c'))
        root.addLayout(bot)

    # ── Seleção e carga ───────────────────────────────────────────────────────

    def escolher_planilha(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Selecionar planilha de pedidos', '', 'Planilhas Excel (*.xlsx)'
        )
        if not path:
            return
        try:
            pedidos = _ler_planilha(Path(path))
        except Exception as exc:
            QMessageBox.critical(self, 'Erro ao ler planilha', str(exc))
            return
        if not pedidos:
            QMessageBox.warning(self, 'Planilha vazia', 'Nenhum pedido encontrado na planilha.')
            return
        self.planilha_path = path
        self.pedidos = pedidos
        self.row_planilha.definir_valor(Path(path).name)
        self.tabela_widget.carregar(pedidos)
        self.tabela_widget.show(); self.div_tabela.show()
        self._atualizar_estado()

    def _atualizar_estado(self):
        n = len(self.pedidos)
        pronto = n > 0 and not self.started
        self.badge_total.setText(f'{n} pedido{"s" if n != 1 else ""}')
        self.subtitle.setText(
            f'{n} pedido{"s" if n!=1 else ""} carregado{"s" if n!=1 else ""}. Revise e inicie.'
            if n else 'Selecione a planilha para começar'
        )
        if self.started:
            fase = getattr(self, '_fase', 'download')
            if fase == 'envio':
                self.ready_title.setText('Fase 2 — Enviando e-mails')
                self.ready_hint.setText('Todos os arquivos baixados. Enviando e-mails...')
                self.start.setText('◌  Enviando...')
            else:
                self.ready_title.setText('Fase 1 — Baixando arquivos')
                self.ready_hint.setText('Buscando recibos e comprovantes no Conveniar...')
                self.start.setText('◌  Baixando...')
        else:
            self.ready_title.setText('Tudo pronto para iniciar' if pronto else 'Aguardando planilha')
            self.ready_hint.setText('Revise os pedidos e clique em Iniciar.' if pronto
                                    else 'Selecione a planilha com os pedidos para continuar.')
            self.start.setText('Iniciar automação   →' if pronto else 'Aguardando planilha')
        self.start.setEnabled(pronto)
        self.start.setStyleSheet(ESTILO_INICIAR_ATIVO if pronto else ESTILO_INICIAR_INATIVO)

    # ── Processamento ─────────────────────────────────────────────────────────

    def iniciar_tarefa(self):
        if not self.pedidos or self.started:
            return
        self.started = True
        self._fase = 'download'
        self._atualizar_estado()
        threading.Thread(target=self._executar, args=(list(self.pedidos),), daemon=True).start()

    def _executar(self, pedidos: list[Pedido]) -> None:
        # ── Passo 1: baixar todos os arquivos ────────────────────────────────
        pendentes: list[tuple[int, str, list[str], str] | None] = []
        for i, pedido in enumerate(pedidos):
            self.sinal_baixando.emit(i)
            try:
                arquivos, nome_projeto = baixar_arquivos_pedido(pedido.numero_pedido)
                nome = nome_projeto or pedido.nome_projeto
                pendentes.append((i, pedido.email, arquivos, nome))
            except Exception as exc:
                self.sinal_pedido_falhou.emit(i, str(exc))
                pendentes.append(None)

        # ── Passo 2: enviar todos os e-mails ─────────────────────────────────
        self._fase = 'envio'
        self.sinal_tarefa_concluida.emit(-1, -1)   # sinaliza troca de fase para o label
        sucesso = 0
        for item in pendentes:
            if item is None:
                continue
            i, email, arquivos, nome = item
            self.sinal_enviando.emit(i)
            try:
                enviar_email(email, nome, arquivos, USER_EMAIL)
                self.sinal_pedido_concluido.emit(i)
                sucesso += 1
            except Exception as exc:
                self.sinal_pedido_falhou.emit(i, str(exc))

        self.sinal_tarefa_concluida.emit(len(pedidos), sucesso)

    def _ao_concluir_pedido(self, row: int):
        self.tabela_widget.atualizar_status(row, ST_ENVIADO)

    def _ao_falhar_pedido(self, row: int, _msg: str):
        self.tabela_widget.atualizar_status(row, ST_ERRO)

    def _ao_concluir_tudo(self, total: int, sucesso: int):
        # total == -1 é sinal interno de troca de fase (download → envio)
        if total == -1:
            self._atualizar_estado()
            return
        self.started = False
        self._fase = 'download'
        self._atualizar_estado()
        erros = total - sucesso
        titulo = 'Automação concluída'
        msg = f'{sucesso} pedido(s) enviado(s) com sucesso.'
        if erros:
            msg += f'\n{erros} pedido(s) com erro — verifique logs/app.log para detalhes.'
        QMessageBox.information(self, titulo, msg)

    def _ao_falhar_tudo(self, msg: str):
        self.started = False
        self._atualizar_estado()
        QMessageBox.critical(self, 'Falha crítica', msg)

    def closeEvent(self, event):
        if self.started:
            resp = QMessageBox.question(
                self, 'Fechar',
                'Uma automação está em andamento. Fechar agora pode deixar pedidos incompletos.\n\nFechar mesmo assim?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
            )
            if resp == QMessageBox.No:
                event.ignore(); return
        event.accept()


# ── Leitura da planilha ───────────────────────────────────────────────────────

def _ler_planilha(path: Path) -> list[Pedido]:
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    pedidos = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        numero  = str(row[0]).strip()
        email   = str(row[1]).strip() if len(row) > 1 and row[1] else ''
        projeto = str(row[2]).strip() if len(row) > 2 and row[2] else ''
        if numero and email:
            pedidos.append(Pedido(numero, email, projeto))
    return pedidos


# ── Ponto de entrada ──────────────────────────────────────────────────────────

def abrir_janela() -> int:
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = App()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(abrir_janela())
