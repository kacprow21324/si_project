"""
Aplikacja desktopowa - Optymalizator Portfela Inwestycyjnego
Zakładki: Dane rynkowe | Losowe | Harmony Search | Najlepsze rozwiązanie | O programie i dane
"""

import sys
import io
import json
import random
from datetime import datetime
from contextlib import redirect_stdout

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QSpinBox,
    QDoubleSpinBox, QGroupBox, QTabWidget, QHeaderView, QFrame,
    QTextEdit, QSizePolicy, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

from database import load_stocks
from harmony_search import HarmonySearchConfig
from random_solution import random_solution

DEFAULT_SECTOR_LIMITS = {
    "Technology": 3,
    "Energy": 2,
    "Healthcare": 3,
    "Financials": 3,
    "Consumer Defensive": 3,
    "Consumer Cyclical": 3,
    "Industrials": 3,
    "Basic Materials": 2,
    "Real Estate": 2,
    "Utilities": 2,
    "Communication Services": 2,
}

# ── Color palette (navy + white) ────────────────────────────────────────────
BG_DARK     = "#f4f7fb"
BG_PANEL    = "#ffffff"
BG_CARD     = "#eaf0f7"
BG_INPUT    = "#ffffff"
GOLD        = "#123b67"
GOLD_DARK   = "#0f2f52"
GREEN       = "#2e6b67"
GREEN_DARK  = "#245553"
GREEN_SOFT  = "#3a7c78"
RED         = "#8a3a3a"
BLUE        = "#1c4a82"
PURPLE      = "#465a78"
WHITE       = "#0c1b33"
GREY        = "#55637a"
BORDER      = "#cdd7e5"
ACCENT      = "#123b67"
ACCENT_SOFT = "#1d538f"
PURE_WHITE  = "#ffffff"

SECTOR_COLORS = {
    "Technology":             "#1f4d7a",
    "Healthcare":             "#2f6f6a",
    "Financials":             "#3b5b8a",
    "Consumer Cyclical":      "#6b5b3d",
    "Industrials":            "#4a5d73",
    "Consumer Defensive":     "#5b6b84",
    "Energy":                 "#7a4a3a",
    "Utilities":              "#4c5f7a",
    "Real Estate":            "#6b4a5b",
    "Communication Services": "#3c6a8a",
    "Basic Materials":        "#6b6b4a",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {BG_DARK};
    color: {WHITE};
    font-family: 'Segoe UI', 'Calibri', sans-serif;
    font-size: 14px;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    background-color: {BG_PANEL};
    border-radius: 10px;
    margin: 6px;
}}

QTabBar::tab {{
    background-color: {BG_CARD};
    color: {GREY};
    padding: 8px 16px;
    border: 1px solid {BORDER};
    border-bottom: none;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
    margin-right: 4px;
    border-radius: 8px 8px 0 0;
}}

QTabBar::tab:selected {{
    background-color: {BG_PANEL};
    color: {GOLD};
    border-top: 3px solid {GOLD};
}}

QTabBar::tab:hover:!selected {{
    background-color: {ACCENT_SOFT};
    color: {PURE_WHITE};
}}

QGroupBox {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    margin-top: 18px;
    padding: 16px;
    font-size: 12px;
    font-weight: 700;
    color: {GREY};
    letter-spacing: 1px;
    text-transform: uppercase;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {GREY};
    background: {BG_PANEL};
}}

QTableWidget {{
    background-color: {BG_PANEL};
    alternate-background-color: {BG_CARD};
    color: {WHITE};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 8px;
    font-size: 13px;
    selection-background-color: {ACCENT_SOFT};
    selection-color: {PURE_WHITE};
    outline: none;
}}

QTableWidget::item {{
    padding: 8px 10px;
    border: none;
}}

QHeaderView::section {{
    background-color: {BG_CARD};
    color: {GREY};
    padding: 7px 9px;
    border: none;
    border-right: 1px solid {BORDER};
    border-bottom: 2px solid {GOLD_DARK};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}

QScrollBar:vertical {{
    background: {BG_DARK};
    width: 10px;
    border: none;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: {ACCENT};
    min-height: 30px;
    border-radius: 5px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QPushButton {{
    background-color: {ACCENT};
    color: {PURE_WHITE};
    border: 1px solid {ACCENT};
    padding: 9px 18px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
    border-radius: 8px;
    text-transform: uppercase;
}}

QPushButton:hover {{
    background-color: {ACCENT_SOFT};
    border-color: {ACCENT_SOFT};
}}

QPushButton:pressed {{
    background-color: {GOLD_DARK};
    border-color: {GOLD_DARK};
}}

QPushButton:disabled {{
    background-color: {BG_CARD};
    color: {GREY};
    border-color: {BORDER};
}}

QPushButton#btn_green {{
    background-color: {GREEN_DARK};
    border-color: {GREEN_DARK};
    color: {PURE_WHITE};
}}

QPushButton#btn_green:hover {{
    background-color: {GREEN_SOFT};
    border-color: {GREEN_SOFT};
}}

QPushButton#btn_blue {{
    background-color: {BG_PANEL};
    color: {ACCENT};
    border: 1px solid {ACCENT};
}}

QPushButton#btn_blue:hover {{
    background-color: {ACCENT};
    color: {PURE_WHITE};
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {BG_INPUT};
    color: {WHITE};
    border: 1px solid {BORDER};
    padding: 7px 10px;
    font-size: 13px;
    font-weight: 600;
    font-family: 'Consolas', 'Courier New', monospace;
    min-width: 130px;
    border-radius: 6px;
    selection-background-color: {ACCENT_SOFT};
    selection-color: {PURE_WHITE};
}}

QAbstractSpinBox::lineEdit {{
    color: {WHITE};
    background: transparent;
    selection-background-color: {ACCENT_SOFT};
    selection-color: {PURE_WHITE};
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {ACCENT};
    background-color: {BG_PANEL};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background-color: {BG_CARD};
    width: 22px;
    border: none;
}}

QLabel {{ color: {WHITE}; background: transparent; }}

QTextEdit {{
    background-color: {BG_PANEL};
    color: {WHITE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    selection-background-color: {ACCENT_SOFT};
}}

QStatusBar {{
    background-color: {BG_PANEL};
    color: {GREY};
    border-top: 1px solid {BORDER};
    font-size: 12px;
    padding: 6px 14px;
}}

QScrollArea {{ border: none; background: transparent; }}
"""


def lbl(text, size=14, bold=False, color=WHITE, align=None, wrap=False):
    l = QLabel(text)
    f = QFont("Segoe UI", size)
    f.setBold(bold)
    l.setFont(f)
    l.setStyleSheet(f"color: {color}; background: transparent;")
    if align:
        l.setAlignment(align)
    l.setWordWrap(wrap)
    return l


def metric_card(title, value="—", value_color=GREEN, subtitle=""):
    """Tworzy kompaktowa karte metryki."""
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background: {BG_PANEL};
            border: 1px solid {BORDER};
            border-left: 4px solid {value_color};
            border-radius: 10px;
        }}
    """)
    lay = QVBoxLayout(card)
    lay.setContentsMargins(12, 10, 12, 10)
    lay.setSpacing(3)

    t = QLabel(title)
    t.setStyleSheet(f"color: {GREY}; font-size: 10px; letter-spacing: 0.6px; background: transparent;")
    t.setFont(QFont("Segoe UI", 10, QFont.Bold))
    t.setWordWrap(True)

    v = QLabel(value)
    v.setStyleSheet(f"color: {value_color}; font-size: 20px; font-weight: 700; background: transparent;")
    v.setFont(QFont("Segoe UI", 17, QFont.Bold))
    v.setObjectName("value_label")

    lay.addWidget(t)
    lay.addWidget(v)
    if subtitle:
        s = QLabel(subtitle)
        s.setStyleSheet(f"color: {GREY}; font-size: 10px; background: transparent;")
        lay.addWidget(s)

    return card


def get_card_value_label(card):
    return card.findChild(QLabel, "value_label")


def separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {BORDER};")
    return line


def wrap_scroll(widget):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setWidget(widget)
    return scroll


class WorkerThread(QThread):
    """Wątek roboczy dla długotrwałych operacji."""
    finished = pyqtSignal(object, str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = self.func(*self.args, **self.kwargs)
        self.finished.emit(result, stream.getvalue())


class SectorBar(QWidget):
    """Prosty wizualny pasek sektorów."""
    def __init__(self, sector_counts, parent=None):
        super().__init__(parent)
        self.sector_counts = sector_counts
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        total = sum(sector_counts.values())
        for sector, count in sorted(sector_counts.items(), key=lambda x: -x[1]):
            color = SECTOR_COLORS.get(sector, GREY)
            pct = count / total * 100
            chip = QLabel(f"{sector[:3].upper()} ×{count}")
            chip.setStyleSheet(f"""
                background-color: {color}22;
                color: {color};
                border: 1px solid {color}66;
                border-radius: 10px;
                padding: 3px 8px;
                font-size: 10px;
                font-weight: 700;
            """)
            chip.setAlignment(Qt.AlignCenter)
            lay.addWidget(chip)
        lay.addStretch()


class StockPortfolioApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.stocks = load_stocks()
        self.config = None
        self.hspar_config = None
        self._random_result = None
        self._hs_result = None
        self._hspar_result = None
        self._best_result = None
        self._ticker_pos = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Optymalizator portfela dywidendowego")
        self.resize(1400, 900)
        self.setMinimumSize(1100, 720)
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_ticker_bar())

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.setContentsMargins(8, 8, 8, 8)
        self.tabs.tabBar().setElideMode(Qt.ElideRight)
        self.tabs.addTab(wrap_scroll(self._build_market_tab()),  "DANE RYNKOWE")
        self.tabs.addTab(wrap_scroll(self._build_random_tab()),  "LOSOWE")
        self.tabs.addTab(wrap_scroll(self._build_hs_tab()),      "HARMONY SEARCH")
        self.tabs.addTab(wrap_scroll(self._build_best_tab()),    "NAJLEPSZE ROZWIĄZANIE")
        self.tabs.addTab(wrap_scroll(self._build_about_tab()),   "O PROGRAMIE I DANE")
        root.addWidget(self.tabs)

        sb = self.statusBar()
        sb.showMessage(f"SYSTEM GOTOWY  |  {len(self.stocks):,} akcji załadowanych")

        self._ticker_timer = QTimer()
        self._ticker_timer.timeout.connect(self._scroll_ticker)
        self._ticker_timer.start(80)
        self._update_about_tab()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        h = QFrame()
        h.setFixedHeight(80)
        h.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {BG_PANEL}, stop:0.5 {BG_CARD}, stop:1 {BG_PANEL});
                border-bottom: 2px solid {ACCENT};
            }}
        """)
        lay = QHBoxLayout(h)
        lay.setContentsMargins(24, 0, 24, 0)

        title = QLabel("OPTYMALIZATOR PORTFELA DYWIDENDOWEGO")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {ACCENT}; letter-spacing: 1.5px; background: transparent;")

        sub = QLabel("Algorytm Harmony Search | Problem plecakowy 0-1")
        sub.setFont(QFont("Segoe UI", 12))
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color: {GREY}; letter-spacing: 1.5px; background: transparent;")

        self.header_budget = QLabel("BUDŻET:  $100,000")
        self.header_budget.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.header_budget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.header_budget.setStyleSheet(f"color: {GREEN_SOFT}; background: transparent;")

        lay.addWidget(title, 3)
        lay.addWidget(sub, 3)
        lay.addWidget(self.header_budget, 2)
        return h

    def _build_ticker_bar(self):
        bar = QFrame()
        bar.setFixedHeight(32)
        bar.setStyleSheet(f"background-color: {BG_CARD}; border-bottom: 1px solid {BORDER};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(8, 0, 8, 0)

        self._ticker_label = QLabel()
        self._ticker_label.setStyleSheet(
            f"color: {ACCENT}; font-family: 'Consolas'; font-size: 12px; background: transparent;"
        )
        self._ticker_string = "   |   ".join(
            f"{s['ticker']}  ${s['share_price']:.2f}  {s['dividend_yield']:.2f}%"
            for s in self.stocks[:80]
        ) + "   |   "
        lay.addWidget(self._ticker_label)
        return bar

    def _scroll_ticker(self):
        s = self._ticker_string
        pos = self._ticker_pos % len(s)
        chunk = (s + s)[pos:pos + 180]
        self._ticker_label.setText(chunk)
        self._ticker_pos += 1

    # ── Market Data Tab ───────────────────────────────────────────────────────

    def _build_market_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        sectors = {}
        total_div = total_cost = 0
        for s in self.stocks:
            sectors[s["sector"]] = sectors.get(s["sector"], 0) + 1
            total_div += s["annual_lot_dividend"]
            total_cost += s["lot_cost"]
        avg_yield = total_div / total_cost * 100 if total_cost else 0

        cards_grid = QGridLayout()
        cards_grid.setSpacing(8)
        cards = [
            metric_card("Akcje", f"{len(self.stocks):,}", GOLD),
            metric_card("Sektory", str(len(sectors)), BLUE),
            metric_card("Śr. koszt lotu", f"${total_cost/len(self.stocks):,.0f}", GREEN_SOFT),
            metric_card("Śr. roczna dywidenda", f"${total_div/len(self.stocks):,.2f}", GREEN),
            metric_card("Śr. stopa dywidendy", f"{avg_yield:.2f}%", GOLD),
        ]
        for i, card in enumerate(cards):
            cards_grid.addWidget(card, i // 3, i % 3)
        lay.addLayout(cards_grid)

        lbl_title = lbl("DANE RYNKOWE  —  WSZYSTKIE INSTRUMENTY", 14, bold=True, color=GREY)
        lbl_title.setStyleSheet(f"color: {GREY}; letter-spacing: 2px; padding: 4px 0;")
        lay.addWidget(lbl_title)

        self.market_table = QTableWidget()
        self._populate_market_table()
        self.market_table.setMinimumHeight(320)
        self.market_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addWidget(self.market_table)
        return w

    def _populate_market_table(self):
        headers = ["TICKER", "SEKTOR", "CENA", "LOT", "KOSZT LOTU", "DYWIDENDA/ROK", "YIELD %"]
        self.market_table.setColumnCount(len(headers))
        self.market_table.setHorizontalHeaderLabels(headers)
        self.market_table.setRowCount(len(self.stocks))
        self.market_table.setAlternatingRowColors(True)
        self.market_table.verticalHeader().setVisible(False)
        self.market_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.market_table.setEditTriggers(QTableWidget.NoEditTriggers)

        for row, s in enumerate(self.stocks):
            yc = GREEN if s["dividend_yield"] >= 3.0 else (GOLD if s["dividend_yield"] >= 1.5 else WHITE)
            sc = SECTOR_COLORS.get(s["sector"], GREY)
            for col, (text, color, align) in enumerate([
                (s["ticker"],                          GOLD,  Qt.AlignLeft | Qt.AlignVCenter),
                (s["sector"],                          sc,    Qt.AlignLeft | Qt.AlignVCenter),
                (f"${s['share_price']:.2f}",           WHITE, Qt.AlignRight | Qt.AlignVCenter),
                (str(s["lot_size"]),                   GREY,  Qt.AlignCenter),
                (f"${s['lot_cost']:,.2f}",             WHITE, Qt.AlignRight | Qt.AlignVCenter),
                (f"${s['annual_lot_dividend']:.2f}",   GREEN, Qt.AlignRight | Qt.AlignVCenter),
                (f"{s['dividend_yield']:.2f}%",        yc,   Qt.AlignRight | Qt.AlignVCenter),
            ]):
                item = QTableWidgetItem(text)
                item.setForeground(QColor(color))
                item.setTextAlignment(align)
                self.market_table.setItem(row, col, item)

        hdr = self.market_table.horizontalHeader()
        for i in range(len(headers)):
            hdr.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hdr.setStretchLastSection(True)

    # ── Random Solution Tab ───────────────────────────────────────────────────

    def _build_random_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        # Controls
        ctrl = QGroupBox("Parametry losowego rozwiązania")
        ctrl_lay = QGridLayout(ctrl)
        ctrl_lay.setSpacing(12)
        ctrl_lay.setColumnStretch(1, 1)

        budget_group = QVBoxLayout()
        budget_group.addWidget(lbl("Budżet ($)", 10, bold=True, color=GREY))
        self.rand_budget = QSpinBox()
        self.rand_budget.setRange(10000, 1000000)
        self.rand_budget.setValue(100000)
        self.rand_budget.setSingleStep(10000)
        self.rand_budget.setPrefix("$ ")
        self.rand_budget.valueChanged.connect(
            lambda v: self.header_budget.setText(f"BUDŻET:  ${v:,}")
        )
        budget_group.addWidget(self.rand_budget)
        ctrl_lay.addLayout(budget_group, 0, 0)

        info_lbl = lbl("Każde uruchomienie daje inne losowe rozwiązanie.", 13, color=GREY, wrap=True)
        ctrl_lay.addWidget(info_lbl, 0, 1)

        self.rand_btn = QPushButton("GENERUJ LOSOWE ROZWIĄZANIE")
        self.rand_btn.setFixedHeight(48)
        self.rand_btn.clicked.connect(self.run_random_solution)
        ctrl_lay.addWidget(self.rand_btn, 0, 2)

        lay.addWidget(ctrl)

        # Result metrics row
        rand_cards = QHBoxLayout()
        rand_cards.setSpacing(8)
        self._rand_card_cost     = metric_card("Koszt portfela",   "—", BLUE)
        self._rand_card_div      = metric_card("Roczna dywidenda", "—", GREEN)
        self._rand_card_yield    = metric_card("Stopa dywidendy",  "—", GOLD)
        self._rand_card_stocks   = metric_card("Liczba akcji",     "—", WHITE)
        for c in [self._rand_card_cost, self._rand_card_div, self._rand_card_yield, self._rand_card_stocks]:
            rand_cards.addWidget(c)
        lay.addLayout(rand_cards)

        # Result table
        lbl_r = lbl("WYBRANE AKCJE — LOSOWE ROZWIĄZANIE", 13, bold=True, color=GREY)
        lbl_r.setStyleSheet(f"color: {GREY}; letter-spacing: 2px; padding: 4px 0;")
        lay.addWidget(lbl_r)

        self.rand_table = QTableWidget()
        self.rand_table.setColumnCount(6)
        self.rand_table.setHorizontalHeaderLabels(
            ["TICKER", "SEKTOR", "CENA", "KOSZT LOTU", "DYWIDENDA/ROK", "YIELD %"]
        )
        self.rand_table.setAlternatingRowColors(True)
        self.rand_table.verticalHeader().setVisible(False)
        self.rand_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rand_table.setSelectionBehavior(QTableWidget.SelectRows)
        hdr = self.rand_table.horizontalHeader()
        for i in range(6):
            hdr.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hdr.setStretchLastSection(True)
        self.rand_table.setMinimumHeight(260)
        self.rand_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addWidget(self.rand_table)

        return w

    # ── Harmony Search Tab ────────────────────────────────────────────────────

    def _build_hs_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        # Parameters
        params_group = QGroupBox("Parametry algorytmu Harmony Search")
        pg_lay = QGridLayout(params_group)
        pg_lay.setSpacing(12)
        pg_lay.setColumnStretch(2, 1)

        def param_row_hs(row, label_text, widget_obj, hint):
            pg_lay.addWidget(lbl(label_text, 13, bold=True, color=GREY), row, 0)
            pg_lay.addWidget(widget_obj, row, 1)
            h = lbl(hint, 12, color=GOLD_DARK, wrap=True)
            pg_lay.addWidget(h, row, 2)

        self.hs_budget = QSpinBox()
        self.hs_budget.setRange(10000, 1000000)
        self.hs_budget.setValue(100000)
        self.hs_budget.setSingleStep(10000)
        self.hs_budget.setPrefix("$ ")
        self.hs_budget.valueChanged.connect(
            lambda v: self.header_budget.setText(f"BUDŻET:  ${v:,}")
        )
        self.hs_budget.valueChanged.connect(self._update_about_tab)
        param_row_hs(0, "Budżet (Budget)", self.hs_budget, "Maksymalny kapitał inwestycyjny")

        self.hs_hms = QSpinBox()
        self.hs_hms.setRange(5, 200)
        self.hs_hms.setValue(10)
        param_row_hs(1, "HMS — Harmony Memory Size", self.hs_hms, "Rozmiar pamięci harmonii  [5–200]")

        self.hs_hmcr = QDoubleSpinBox()
        self.hs_hmcr.setRange(0.0, 1.0)
        self.hs_hmcr.setValue(0.7)
        self.hs_hmcr.setSingleStep(0.05)
        self.hs_hmcr.setDecimals(2)
        param_row_hs(2, "HMCR — Memory Considering Rate", self.hs_hmcr,
                     "Prawdopodobieństwo wyboru z pamięci  [0–1]")

        self.hs_par = QDoubleSpinBox()
        self.hs_par.setRange(0.0, 1.0)
        self.hs_par.setValue(0.15)
        self.hs_par.setSingleStep(0.05)
        self.hs_par.setDecimals(2)
        param_row_hs(3, "PAR — Pitch Adjusting Rate", self.hs_par,
                     "Prawdopodobieństwo dostrojenia wektora  [0–1]")

        self.hs_iter = QSpinBox()
        self.hs_iter.setRange(100, 100000)
        self.hs_iter.setValue(10000)
        self.hs_iter.setSingleStep(100)
        param_row_hs(4, "N — Liczba iteracji", self.hs_iter, "Liczba krokow optymalizacji  [100–100000]")

        lay.addWidget(params_group)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.hs_init_btn = QPushButton("INICJALIZUJ PAMIĘĆ HARMONII")
        self.hs_init_btn.setFixedHeight(46)
        self.hs_init_btn.clicked.connect(self.hs_initialize)
        btn_row.addWidget(self.hs_init_btn)

        self.hs_run_btn = QPushButton("URUCHOM HARMONY SEARCH")
        self.hs_run_btn.setFixedHeight(46)
        self.hs_run_btn.setEnabled(False)
        self.hs_run_btn.setObjectName("btn_green")
        self.hs_run_btn.clicked.connect(self.hs_run)
        btn_row.addWidget(self.hs_run_btn)

        self.hs_export_btn = QPushButton("EKSPORTUJ JSON")
        self.hs_export_btn.setFixedHeight(46)
        self.hs_export_btn.setObjectName("btn_blue")
        self.hs_export_btn.setEnabled(False)
        self.hs_export_btn.clicked.connect(self.hs_export)
        btn_row.addWidget(self.hs_export_btn)

        lay.addLayout(btn_row)

        # Progress / status
        self.hs_status = QLabel("Oczekiwanie na inicjalizację...")
        self.hs_status.setStyleSheet(
            f"color: {GREY}; background: {BG_CARD}; border: 1px solid {BORDER}; "
            f"border-radius: 6px; padding: 10px 14px; font-size: 12px;"
        )
        lay.addWidget(self.hs_status)

        # Metrics
        hs_cards = QHBoxLayout()
        hs_cards.setSpacing(8)
        self._hs_card_best   = metric_card("Najlepsza dywidenda", "—", GREEN)
        self._hs_card_worst  = metric_card("Najgorsza harmonia",  "—", RED)
        self._hs_card_avg    = metric_card("Średnia pamięci",     "—", GOLD)
        self._hs_card_cost   = metric_card("Koszt portfela",      "—", BLUE)
        self._hs_card_stocks = metric_card("Liczba akcji",        "—", WHITE)
        for c in [self._hs_card_best, self._hs_card_worst, self._hs_card_avg,
                  self._hs_card_cost, self._hs_card_stocks]:
            hs_cards.addWidget(c)
        lay.addLayout(hs_cards)

        # Result table
        lbl_hs = lbl("NAJLEPSZA HARMONIA — WYBRANE AKCJE", 13, bold=True, color=GREY)
        lbl_hs.setStyleSheet(f"color: {GREY}; letter-spacing: 2px; padding: 4px 0;")
        lay.addWidget(lbl_hs)

        self.hs_table = QTableWidget()
        self.hs_table.setColumnCount(6)
        self.hs_table.setHorizontalHeaderLabels(
            ["TICKER", "SEKTOR", "CENA", "KOSZT LOTU", "DYWIDENDA/ROK", "YIELD %"]
        )
        self.hs_table.setAlternatingRowColors(True)
        self.hs_table.verticalHeader().setVisible(False)
        self.hs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.hs_table.setSelectionBehavior(QTableWidget.SelectRows)
        hdr2 = self.hs_table.horizontalHeader()
        for i in range(6):
            hdr2.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hdr2.setStretchLastSection(True)

        # Log
        log_grp = QGroupBox("Logi algorytmu")
        log_lay = QVBoxLayout(log_grp)
        self.hs_log = QTextEdit()
        self.hs_log.setReadOnly(True)
        self.hs_log.setMinimumHeight(320)
        self.hs_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.hs_log.setPlaceholderText("Tu pojawią się logi z działania Harmony Search...")
        log_clear = QPushButton("WYCZYŚĆ LOGI")
        log_clear.setFixedHeight(34)
        log_clear.clicked.connect(self.hs_log.clear)
        log_lay.addWidget(self.hs_log)
        log_lay.addWidget(log_clear)

        self.hs_table.setMinimumHeight(280)
        self.hs_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addWidget(self.hs_table, 4)
        lay.addWidget(log_grp, 2)

        return w

    # ── Best Solution Tab ───────────────────────────────────────────────────

    def _build_best_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        title = lbl("NAJLEPSZE ZNALEZIONE ROZWIĄZANIE", 13, bold=True, color=GOLD)
        title.setStyleSheet(f"color: {GOLD}; letter-spacing: 2px; padding: 4px 0;")
        lay.addWidget(title)

        self.best_hint = lbl(
            "Uruchom losowe lub Harmony Search, aby zobaczyć najlepszy portfel.",
            12, color=GREY, wrap=True
        )
        lay.addWidget(self.best_hint)

        cards_grid = QGridLayout()
        cards_grid.setSpacing(8)
        self._best_card_div = metric_card("Roczna dywidenda", "—", GREEN)
        self._best_card_cost = metric_card("Koszt portfela", "—", GOLD)
        self._best_card_yield = metric_card("Stopa dywidendy", "—", GREEN_SOFT)
        self._best_card_stocks = metric_card("Liczba akcji", "—", PURPLE)
        best_cards = [
            self._best_card_div,
            self._best_card_cost,
            self._best_card_yield,
            self._best_card_stocks,
        ]
        for i, card in enumerate(best_cards):
            cards_grid.addWidget(card, i // 2, i % 2)
        lay.addLayout(cards_grid)

        self.best_status = QLabel("Brak danych. Uruchom metodę optymalizacji.")
        self.best_status.setStyleSheet(
            f"color: {GREY}; background: {BG_CARD}; border: 1px solid {BORDER}; "
            f"border-radius: 6px; padding: 10px 12px; font-size: 12px;"
        )
        lay.addWidget(self.best_status)

        table_group = QGroupBox("Wybrane akcje")
        table_lay = QVBoxLayout(table_group)
        self.best_table = QTableWidget()
        self.best_table.setColumnCount(6)
        self.best_table.setHorizontalHeaderLabels(
            ["TICKER", "SEKTOR", "CENA", "KOSZT LOTU", "DYWIDENDA/ROK", "YIELD %"]
        )
        self.best_table.setAlternatingRowColors(True)
        self.best_table.verticalHeader().setVisible(False)
        self.best_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.best_table.setSelectionBehavior(QTableWidget.SelectRows)
        hdr = self.best_table.horizontalHeader()
        for i in range(6):
            hdr.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hdr.setStretchLastSection(True)
        self.best_table.setMinimumHeight(260)
        self.best_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table_lay.addWidget(self.best_table)
        lay.addWidget(table_group, 3)

        sector_group = QGroupBox("Podział sektorowy")
        sector_lay = QVBoxLayout(sector_group)
        self.best_sector_table = QTableWidget()
        self.best_sector_table.setColumnCount(2)
        self.best_sector_table.setHorizontalHeaderLabels(["SEKTOR", "LICZBA AKCJI"])
        self.best_sector_table.setAlternatingRowColors(True)
        self.best_sector_table.verticalHeader().setVisible(False)
        self.best_sector_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.best_sector_table.setSelectionBehavior(QTableWidget.SelectRows)
        hdr2 = self.best_sector_table.horizontalHeader()
        hdr2.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr2.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.best_sector_table.setMinimumHeight(160)
        sector_lay.addWidget(self.best_sector_table)
        lay.addWidget(sector_group, 1)

        return w

    # ── About Tab ───────────────────────────────────────────────────────────

    def _build_about_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(12)

        about_group = QGroupBox("O programie")
        about_lay = QVBoxLayout(about_group)
        about_text = (
            "Optymalizator portfela dywidendowego wyszukuje zestaw akcji, który "
            "maksymalizuje roczną dywidendę przy zachowaniu limitów sektorowych "
            "oraz budżetu inwestycyjnego. Wykorzystuje on algorytm Harmony Search "
            "do przeszukiwania przestrzeni rozwiązań problemu plecakowego 0-1."
        )
        about_lbl = lbl(about_text, 12, color=GREY, wrap=True)
        about_lay.addWidget(about_lbl)
        lay.addWidget(about_group)

        params_group = QGroupBox("Parametry optymalizacji")
        params_lay = QVBoxLayout(params_group)

        budget_row = QHBoxLayout()
        budget_row.addWidget(lbl("Budżet inwestycyjny:", 12, bold=True, color=GREY))
        self.about_budget_value = lbl("$0", 12, bold=True, color=GOLD)
        budget_row.addStretch()
        budget_row.addWidget(self.about_budget_value)
        params_lay.addLayout(budget_row)

        self.about_limits_table = QTableWidget()
        self.about_limits_table.setColumnCount(2)
        self.about_limits_table.setHorizontalHeaderLabels(["SEKTOR", "LIMIT AKCJI"])
        self.about_limits_table.setAlternatingRowColors(True)
        self.about_limits_table.verticalHeader().setVisible(False)
        self.about_limits_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.about_limits_table.setSelectionBehavior(QTableWidget.SelectRows)
        hdr = self.about_limits_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        params_lay.addWidget(self.about_limits_table)
        lay.addWidget(params_group)

        return w

    # ── HS + PAR Mutations Tab ────────────────────────────────────────────────

    def _build_hspar_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        # Parameters
        params_group = QGroupBox("Parametry algorytmu Harmony Search z mutacjami PAR")
        pg_lay = QGridLayout(params_group)
        pg_lay.setSpacing(12)
        pg_lay.setColumnStretch(2, 1)

        def param_row(row, label_text, widget_obj, hint):
            pg_lay.addWidget(lbl(label_text, 14, bold=True, color=GREY), row, 0)
            pg_lay.addWidget(widget_obj, row, 1)
            pg_lay.addWidget(lbl(hint, 13, color=GOLD_DARK), row, 2)

        self.hspar_budget = QSpinBox()
        self.hspar_budget.setRange(10000, 1000000)
        self.hspar_budget.setValue(100000)
        self.hspar_budget.setSingleStep(10000)
        self.hspar_budget.setPrefix("$ ")
        param_row(0, "Budżet (Budget)", self.hspar_budget, "Maksymalny kapitał inwestycyjny")

        self.hspar_hms = QSpinBox()
        self.hspar_hms.setRange(5, 200)
        self.hspar_hms.setValue(10)
        param_row(1, "HMS — Harmony Memory Size", self.hspar_hms, "Rozmiar pamięci harmonii  [5–200]")

        self.hspar_hmcr = QDoubleSpinBox()
        self.hspar_hmcr.setRange(0.0, 1.0)
        self.hspar_hmcr.setValue(0.7)
        self.hspar_hmcr.setSingleStep(0.05)
        self.hspar_hmcr.setDecimals(2)
        param_row(2, "HMCR — Memory Considering Rate", self.hspar_hmcr,
                  "Prawdopodobieństwo wyboru z pamięci  [0–1]")

        self.hspar_par = QDoubleSpinBox()
        self.hspar_par.setRange(0.1, 0.3)
        self.hspar_par.setValue(0.15)
        self.hspar_par.setSingleStep(0.05)
        self.hspar_par.setDecimals(2)
        param_row(3, "PAR — Pitch Adjusting Rate (mutacja)", self.hspar_par,
                  "Prawdopodobieństwo zamiany akcji w harmonii  [0.1–0.3]")

        self.hspar_iter = QSpinBox()
        self.hspar_iter.setRange(100, 100000)
        self.hspar_iter.setValue(10000)
        self.hspar_iter.setSingleStep(100)
        param_row(4, "N — Liczba iteracji", self.hspar_iter, "Liczba krokow optymalizacji  [100–100000]")

        lay.addWidget(params_group)

        # PAR explanation box
        par_info = QGroupBox("Jak działają mutacje PAR w tym algorytmie?")
        par_info_lay = QVBoxLayout(par_info)
        par_text = lbl(
            "Po wylosowaniu harmonii z pamięci (krok HMCR), dla każdej wybranej akcji losujemy r2 ∈ [0,1).\n"
            "Jeśli r2 < PAR → akcja zostaje podmieniona na losową akcję spoza bieżącej harmonii\n"
            "(z zachowaniem limitów sektorowych i budżetu). To mała lokalna zmiana — swap jednej akcji.\n"
            "PAR ∈ [0.1, 0.3] oznacza że ok. 10–30% akcji w harmonii może zostać zamutowanych.",
            11, color=GREY
        )
        par_text.setWordWrap(True)
        par_info_lay.addWidget(par_text)
        lay.addWidget(par_info)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.hspar_init_btn = QPushButton("INICJALIZUJ PAMIĘĆ")
        self.hspar_init_btn.setFixedHeight(46)
        self.hspar_init_btn.clicked.connect(self.hspar_initialize)
        btn_row.addWidget(self.hspar_init_btn)

        self.hspar_run_btn = QPushButton("URUCHOM HS + MUTACJE PAR")
        self.hspar_run_btn.setFixedHeight(46)
        self.hspar_run_btn.setEnabled(False)
        self.hspar_run_btn.setObjectName("btn_green")
        self.hspar_run_btn.clicked.connect(self.hspar_run)
        btn_row.addWidget(self.hspar_run_btn)

        lay.addLayout(btn_row)

        # Status
        self.hspar_status = QLabel("Oczekiwanie na inicjalizację...")
        self.hspar_status.setStyleSheet(
            f"color: {GREY}; background: {BG_CARD}; border: 1px solid {BORDER}; "
            f"border-radius: 6px; padding: 10px 14px; font-size: 12px;"
        )
        lay.addWidget(self.hspar_status)

        # Metrics
        hspar_cards = QHBoxLayout()
        hspar_cards.setSpacing(8)
        self._hspar_card_best   = metric_card("Najlepsza dywidenda", "—", GREEN)
        self._hspar_card_worst  = metric_card("Najgorsza harmonia",  "—", RED)
        self._hspar_card_avg    = metric_card("Średnia pamięci",     "—", GOLD)
        self._hspar_card_cost   = metric_card("Koszt portfela",      "—", BLUE)
        self._hspar_card_mut    = metric_card("Mutacji wykonanych",  "—", PURPLE)
        for c in [self._hspar_card_best, self._hspar_card_worst, self._hspar_card_avg,
                  self._hspar_card_cost, self._hspar_card_mut]:
            hspar_cards.addWidget(c)
        lay.addLayout(hspar_cards)

        lbl_t = lbl("NAJLEPSZA HARMONIA Z MUTACJAMI — WYBRANE AKCJE", 13, bold=True, color=GREY)
        lbl_t.setStyleSheet(f"color: {GREY}; letter-spacing: 2px; padding: 4px 0;")
        lay.addWidget(lbl_t)

        self.hspar_table = QTableWidget()
        self.hspar_table.setColumnCount(6)
        self.hspar_table.setHorizontalHeaderLabels(
            ["TICKER", "SEKTOR", "CENA", "KOSZT LOTU", "DYWIDENDA/ROK", "YIELD %"]
        )
        self.hspar_table.setAlternatingRowColors(True)
        self.hspar_table.verticalHeader().setVisible(False)
        self.hspar_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.hspar_table.setSelectionBehavior(QTableWidget.SelectRows)
        hdr3 = self.hspar_table.horizontalHeader()
        for i in range(6):
            hdr3.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hdr3.setStretchLastSection(True)

        log_grp = QGroupBox("Logi algorytmu (z informacją o mutacjach)")
        log_lay = QVBoxLayout(log_grp)
        self.hspar_log = QTextEdit()
        self.hspar_log.setReadOnly(True)
        self.hspar_log.setMinimumHeight(320)
        self.hspar_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.hspar_log.setPlaceholderText("Tu pojawią się logi — w tym informacje kiedy PAR wykonał mutację...")
        log_clear = QPushButton("WYCZYŚĆ LOGI")
        log_clear.setFixedHeight(34)
        log_clear.clicked.connect(self.hspar_log.clear)
        log_lay.addWidget(self.hspar_log)
        log_lay.addWidget(log_clear)

        self.hspar_table.setMinimumHeight(280)
        self.hspar_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addWidget(self.hspar_table, 4)
        lay.addWidget(log_grp, 2)

        return w

    # ── Logic: HS + PAR ───────────────────────────────────────────────────────

    def hspar_initialize(self):
        self.hspar_config = HarmonySearchConfig(
            budget=self.hspar_budget.value(),
            HMS=self.hspar_hms.value(),
            HMCR=self.hspar_hmcr.value(),
            PAR=self.hspar_par.value(),
            iterations=self.hspar_iter.value(),
            seed=None  # brak seeda — losowa inicjalizacja
        )

        self.hspar_status.setText("Inicjalizacja pamięci harmonii...")
        self.hspar_status.setStyleSheet(
            f"color: {GOLD_DARK}; background: {BG_CARD}; border: 1px solid {GOLD_DARK}; "
            f"border-radius: 6px; padding: 10px 14px;"
        )
        QApplication.processEvents()

        stream = io.StringIO()
        with redirect_stdout(stream):
            harmony_memory, scores = self.hspar_config.initialize_harmony_memory()
        if stream.getvalue().strip():
            self.hspar_log.append("=== INICJALIZACJA PAMIĘCI ===")
            self.hspar_log.append(stream.getvalue().rstrip())

        best, worst, avg = max(scores), min(scores), sum(scores) / len(scores)
        get_card_value_label(self._hspar_card_best).setText(f"${best:,.2f}")
        get_card_value_label(self._hspar_card_worst).setText(f"${worst:,.2f}")
        get_card_value_label(self._hspar_card_avg).setText(f"${avg:,.2f}")

        self.hspar_status.setText(
            f"Pamięć zainicjalizowana  |  HMS={self.hspar_config.HMS}  |  Best: ${best:,.2f}"
        )
        self.hspar_status.setStyleSheet(
            f"color: {GREEN_DARK}; background: #e9f4f1; border: 1px solid {GREEN_SOFT}; "
            f"border-radius: 6px; padding: 10px 14px;"
        )
        self.hspar_run_btn.setEnabled(True)

    def hspar_run(self):
        if not self.hspar_config or not self.hspar_config.harmony_memory:
            return

        self.hspar_status.setText("Uruchamianie HS z mutacjami PAR...")
        self.hspar_status.setStyleSheet(
            f"color: {GOLD_DARK}; background: {BG_CARD}; border: 1px solid {GOLD_DARK}; "
            f"border-radius: 6px; padding: 10px 14px;"
        )
        self.hspar_run_btn.setEnabled(False)
        self.hspar_init_btn.setEnabled(False)
        QApplication.processEvents()

        cfg = self.hspar_config
        PAR = cfg.PAR
        stocks = cfg.stocks
        sector_limits = cfg.sector_limits
        budget = cfg.budget
        mutation_count = 0

        self.hspar_log.append("=== PRZEBIEG HS + MUTACJE PAR ===")

        for iteration in range(1, cfg.iterations + 1):
            # Krok 1: improwizacja HMCR
            new_harmony, draw, source = cfg._improvise_new_harmony()

            # Krok 2: PAR — mutacja (swap) dla każdej akcji w harmonii
            if source == "HM" and new_harmony:
                mutated_harmony = list(new_harmony)
                current_set = set(mutated_harmony)
                sector_counts = {}
                total_cost = sum(stocks[i]["lot_cost"] for i in mutated_harmony)
                for i in mutated_harmony:
                    s = stocks[i]["sector"]
                    sector_counts[s] = sector_counts.get(s, 0) + 1

                for pos, idx in enumerate(mutated_harmony):
                    r2 = random.random()
                    if r2 < PAR:
                        # Znajdź kandydatów do zamiany: inne akcje, nie w bieżącej harmonii
                        old_stock = stocks[idx]
                        old_sector = old_stock["sector"]
                        cost_without = total_cost - old_stock["lot_cost"]

                        candidates = [
                            i for i in range(len(stocks))
                            if i not in current_set
                            and stocks[i]["lot_cost"] + cost_without <= budget
                            and (
                                stocks[i]["sector"] != old_sector
                                or sector_counts.get(stocks[i]["sector"], 0) < sector_limits.get(stocks[i]["sector"], 99)
                            )
                        ]

                        if candidates:
                            new_idx = random.choice(candidates)
                            # Aktualizuj zbiór i liczniki
                            current_set.discard(idx)
                            current_set.add(new_idx)
                            old_sec = stocks[idx]["sector"]
                            new_sec = stocks[new_idx]["sector"]
                            sector_counts[old_sec] = sector_counts.get(old_sec, 1) - 1
                            sector_counts[new_sec] = sector_counts.get(new_sec, 0) + 1
                            total_cost = cost_without + stocks[new_idx]["lot_cost"]
                            mutated_harmony[pos] = new_idx
                            mutation_count += 1
                            if iteration <= 20 or iteration % 20 == 0:
                                self.hspar_log.append(
                                    f"  iter {iteration:>4} | PAR mutacja: "
                                    f"{stocks[idx]['ticker']} → {stocks[new_idx]['ticker']} "
                                    f"(r2={r2:.3f} < PAR={PAR:.2f})"
                                )

                new_harmony = mutated_harmony

            new_score = cfg._evaluate_harmony(new_harmony)

            worst_score = min(cfg.harmony_scores)
            worst_idx = cfg.harmony_scores.index(worst_score)
            if new_score > worst_score:
                cfg.harmony_memory[worst_idx] = new_harmony
                cfg.harmony_scores[worst_idx] = new_score

        best_score = max(cfg.harmony_scores)
        best_idx = cfg.harmony_scores.index(best_score)
        best_harmony = cfg.harmony_memory[best_idx]

        selected_stocks = [stocks[i] for i in best_harmony]
        total_cost = sum(s["lot_cost"] for s in selected_stocks)
        total_div = sum(s["annual_lot_dividend"] for s in selected_stocks)
        div_yield = (total_div / total_cost * 100) if total_cost else 0

        self._hspar_result = {
            "selected_stocks": selected_stocks,
            "total_cost": total_cost,
            "total_dividend": total_div,
            "total_dividend_yield": div_yield,
            "num_stocks": len(selected_stocks),
            "sector_counts": {}
        }
        for s in selected_stocks:
            self._hspar_result["sector_counts"][s["sector"]] = \
                self._hspar_result["sector_counts"].get(s["sector"], 0) + 1

        scores = cfg.harmony_scores
        get_card_value_label(self._hspar_card_best).setText(f"${best_score:,.2f}")
        get_card_value_label(self._hspar_card_worst).setText(f"${min(scores):,.2f}")
        get_card_value_label(self._hspar_card_avg).setText(f"${sum(scores)/len(scores):,.2f}")
        get_card_value_label(self._hspar_card_cost).setText(f"${total_cost:,.2f}")
        get_card_value_label(self._hspar_card_mut).setText(str(mutation_count))

        self._fill_stock_table(self.hspar_table, selected_stocks)

        self.hspar_log.append(
            f"\nKONIEC  |  Mutacji PAR: {mutation_count}  |  "
            f"Najlepsza dywidenda: ${best_score:,.2f}  |  Akcji: {len(selected_stocks)}"
        )
        self.hspar_status.setText(
            f"Zakończone  |  Dywidenda: ${best_score:,.2f}/rok  |  "
            f"Mutacji PAR: {mutation_count}  |  Koszt: ${total_cost:,.2f}"
        )
        self.hspar_status.setStyleSheet(
            f"color: {GREEN_DARK}; background: #e9f4f1; border: 1px solid {GREEN_SOFT}; "
            f"border-radius: 6px; padding: 10px 14px;"
        )
        self.hspar_run_btn.setEnabled(True)
        self.hspar_init_btn.setEnabled(True)
        self.statusBar().showMessage(
            f"HS+PAR GOTOWY  |  Dywidenda: ${best_score:,.2f}  |  Mutacji: {mutation_count}"
        )
        self._refresh_best_solution()

    # ── Logic: Random ─────────────────────────────────────────────────────────

    def run_random_solution(self):
        budget = self.rand_budget.value()

        sector_limits = DEFAULT_SECTOR_LIMITS

        result = random_solution(budget=budget, sector_limits=sector_limits, seed=None)
        self._random_result = result

        get_card_value_label(self._rand_card_cost).setText(f"${result['total_cost']:,.2f}")
        get_card_value_label(self._rand_card_div).setText(f"${result['total_dividend']:,.2f}")
        get_card_value_label(self._rand_card_yield).setText(f"{result['total_dividend_yield']:.3f}%")
        get_card_value_label(self._rand_card_stocks).setText(str(result['num_stocks']))

        self._fill_stock_table(self.rand_table, result["selected_stocks"])
        self.statusBar().showMessage(
            f"LOSOWE: {result['num_stocks']} akcji | "
            f"Dywidenda: ${result['total_dividend']:,.2f} | "
            f"Koszt: ${result['total_cost']:,.2f}"
        )
        self._refresh_best_solution()

    # ── Logic: Harmony Search ─────────────────────────────────────────────────

    def hs_initialize(self):
        self.config = HarmonySearchConfig(
            budget=self.hs_budget.value(),
            HMS=self.hs_hms.value(),
            HMCR=self.hs_hmcr.value(),
            PAR=self.hs_par.value(),
            iterations=self.hs_iter.value(),
            seed=42
        )

        self.hs_status.setText("Inicjalizacja pamięci harmonii...")
        self.hs_status.setStyleSheet(
            f"color: {GOLD_DARK}; background: {BG_CARD}; border: 1px solid {GOLD_DARK}; "
            f"border-radius: 6px; padding: 10px 14px;"
        )
        QApplication.processEvents()

        stream = io.StringIO()
        with redirect_stdout(stream):
            harmony_memory, scores = self.config.initialize_harmony_memory()
        if stream.getvalue().strip():
            self.hs_log.append("=== INICJALIZACJA PAMIĘCI ===")
            self.hs_log.append(stream.getvalue().rstrip())

        best = max(scores)
        worst = min(scores)
        avg = sum(scores) / len(scores)

        get_card_value_label(self._hs_card_best).setText(f"${best:,.2f}")
        get_card_value_label(self._hs_card_worst).setText(f"${worst:,.2f}")
        get_card_value_label(self._hs_card_avg).setText(f"${avg:,.2f}")

        self.hs_status.setText(
            f"Pamięć zainicjalizowana  |  HMS={self.config.HMS}  |  "
            f"Best: ${best:,.2f}  |  Avg: ${avg:,.2f}"
        )
        self.hs_status.setStyleSheet(
            f"color: {GREEN_DARK}; background: #e9f4f1; border: 1px solid {GREEN_SOFT}; "
            f"border-radius: 6px; padding: 10px 14px;"
        )
        self.hs_run_btn.setEnabled(True)
        self.statusBar().showMessage(f"PAMIĘĆ HARMONII GOTOWA  |  HMS={self.config.HMS}")
        self._update_about_tab()

    def hs_run(self):
        if not self.config or not self.config.harmony_memory:
            return

        self.hs_status.setText("Uruchamianie Harmony Search...")
        self.hs_status.setStyleSheet(
            f"color: {GOLD_DARK}; background: {BG_CARD}; border: 1px solid {GOLD_DARK}; "
            f"border-radius: 6px; padding: 10px 14px;"
        )
        self.hs_run_btn.setEnabled(False)
        self.hs_init_btn.setEnabled(False)
        QApplication.processEvents()

        stream = io.StringIO()
        with redirect_stdout(stream):
            best_harmony, best_score = self.config.run_harmony_search(
                show_memory_every=0, verbose=True
            )
        if stream.getvalue().strip():
            self.hs_log.append("=== PRZEBIEG OPTYMALIZACJI ===")
            self.hs_log.append(stream.getvalue().rstrip())

        selected_stocks = [self.config.stocks[i] for i in best_harmony]
        total_cost = sum(s["lot_cost"] for s in selected_stocks)
        total_div = sum(s["annual_lot_dividend"] for s in selected_stocks)
        div_yield = (total_div / total_cost * 100) if total_cost else 0

        self._hs_result = {
            "selected_stocks": selected_stocks,
            "total_cost": total_cost,
            "total_dividend": total_div,
            "total_dividend_yield": div_yield,
            "num_stocks": len(selected_stocks),
            "sector_counts": {}
        }
        for s in selected_stocks:
            self._hs_result["sector_counts"][s["sector"]] = \
                self._hs_result["sector_counts"].get(s["sector"], 0) + 1

        scores = self.config.harmony_scores
        get_card_value_label(self._hs_card_best).setText(f"${best_score:,.2f}")
        get_card_value_label(self._hs_card_worst).setText(f"${min(scores):,.2f}")
        get_card_value_label(self._hs_card_avg).setText(f"${sum(scores)/len(scores):,.2f}")
        get_card_value_label(self._hs_card_cost).setText(f"${total_cost:,.2f}")
        get_card_value_label(self._hs_card_stocks).setText(str(len(selected_stocks)))

        self._fill_stock_table(self.hs_table, selected_stocks)

        self.hs_status.setText(
            f"Optymalizacja zakończona  |  Najlepsza dywidenda: ${best_score:,.2f}/rok  |  "
            f"Akcji: {len(selected_stocks)}  |  Koszt: ${total_cost:,.2f}"
        )
        self.hs_status.setStyleSheet(
            f"color: {GREEN_DARK}; background: #e9f4f1; border: 1px solid {GREEN_SOFT}; "
            f"border-radius: 6px; padding: 10px 14px;"
        )
        self.hs_run_btn.setEnabled(True)
        self.hs_init_btn.setEnabled(True)
        self.hs_export_btn.setEnabled(True)

        self.statusBar().showMessage(
            f"HARMONY SEARCH GOTOWY  |  Dywidenda: ${best_score:,.2f}  |  "
            f"Koszt: ${total_cost:,.2f}  |  Akcji: {len(selected_stocks)}"
        )
        self._refresh_best_solution()

    def hs_export(self):
        if not self._hs_result or not self.config:
            return
        sel = self._hs_result["selected_stocks"]
        best_score = self._hs_result["total_dividend"]
        sector_counts = self._hs_result["sector_counts"]
        payload = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "algorithm": "Harmony Search",
            "parameters": {
                "budget": self.config.budget,
                "HMS": self.config.HMS,
                "HMCR": self.config.HMCR,
                "PAR": self.config.PAR,
                "iterations": self.config.iterations,
                "seed": self.config.seed,
            },
            "best_solution": {
                "fitness_annual_dividend": best_score,
                "total_cost": self._hs_result["total_cost"],
                "num_stocks": self._hs_result["num_stocks"],
                "sector_counts": sector_counts,
                "stocks": sel,
            }
        }
        path = "best_harmony_solution.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        self.hs_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Zapisano do: {path}")
        self.statusBar().showMessage(f"JSON zapisany: {path}")

    # ── Best solution refresh ───────────────────────────────────────────────

    def _refresh_best_solution(self):
        candidates = []
        if self._random_result:
            candidates.append(("Losowe", self._random_result))
        if self._hs_result:
            candidates.append(("Harmony Search", self._hs_result))
        if self._hspar_result:
            candidates.append(("HS + PAR", self._hspar_result))

        if not candidates:
            self.best_status.setText("Brak danych. Uruchom metodę optymalizacji.")
            return

        source, best = max(candidates, key=lambda item: item[1]["total_dividend"])
        self._best_result = best

        get_card_value_label(self._best_card_div).setText(f"${best['total_dividend']:,.2f}")
        get_card_value_label(self._best_card_cost).setText(f"${best['total_cost']:,.2f}")
        get_card_value_label(self._best_card_yield).setText(f"{best['total_dividend_yield']:.3f}%")
        get_card_value_label(self._best_card_stocks).setText(str(best["num_stocks"]))

        self.best_status.setText(
            f"Najlepszy wynik  |  Dywidenda: ${best['total_dividend']:,.2f}/rok"
        )

        self._fill_stock_table(self.best_table, best["selected_stocks"])
        self._fill_sector_table(self.best_sector_table, best["sector_counts"])

    # ── Shared helpers ────────────────────────────────────────────────────────

    def _fill_stock_table(self, table, stocks):
        table.setRowCount(len(stocks))
        for row, s in enumerate(stocks):
            sc = SECTOR_COLORS.get(s["sector"], GREY)
            yc = GREEN if s["dividend_yield"] >= 3.0 else (GOLD if s["dividend_yield"] >= 1.5 else WHITE)
            for col, (text, color, align) in enumerate([
                (s["ticker"],                          GOLD,  Qt.AlignLeft | Qt.AlignVCenter),
                (s["sector"],                          sc,    Qt.AlignLeft | Qt.AlignVCenter),
                (f"${s['share_price']:.2f}",           WHITE, Qt.AlignRight | Qt.AlignVCenter),
                (f"${s['lot_cost']:,.2f}",             WHITE, Qt.AlignRight | Qt.AlignVCenter),
                (f"${s['annual_lot_dividend']:.2f}",   GREEN, Qt.AlignRight | Qt.AlignVCenter),
                (f"{s['dividend_yield']:.2f}%",        yc,   Qt.AlignRight | Qt.AlignVCenter),
            ]):
                item = QTableWidgetItem(text)
                item.setForeground(QColor(color))
                item.setTextAlignment(align)
                table.setItem(row, col, item)

    def _fill_sector_table(self, table, sector_counts):
        items = sorted(sector_counts.items(), key=lambda x: (-x[1], x[0]))
        table.setRowCount(len(items))
        for row, (sector, count) in enumerate(items):
            name_item = QTableWidgetItem(sector)
            name_item.setForeground(QColor(SECTOR_COLORS.get(sector, GREY)))
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 0, name_item)
            table.setItem(row, 1, count_item)

    def _update_about_tab(self):
        budget = self.config.budget if self.config else self.hs_budget.value()
        self.about_budget_value.setText(f"${budget:,.2f}")
        limits = self.config.sector_limits if self.config else DEFAULT_SECTOR_LIMITS
        self._fill_sector_table(self.about_limits_table, limits)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    for role, hex_color in [
        (QPalette.Window,          BG_DARK),
        (QPalette.WindowText,      WHITE),
        (QPalette.Base,            BG_PANEL),
        (QPalette.AlternateBase,   BG_CARD),
        (QPalette.Text,            WHITE),
        (QPalette.Button,          BG_CARD),
        (QPalette.ButtonText,      WHITE),
        (QPalette.Highlight,       ACCENT),
        (QPalette.HighlightedText, GOLD),
    ]:
        palette.setColor(role, QColor(hex_color))
    app.setPalette(palette)

    window = StockPortfolioApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()