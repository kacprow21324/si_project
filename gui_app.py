"""
Aplikacja desktopowa - Optymalizator Portfela Inwestycyjnego
Trzy zakładki: Losowe rozwiązanie | Harmony Search | Porównanie
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
    QTextEdit, QSizePolicy, QProgressBar, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush

from database import load_stocks
from config import HarmonySearchConfig
from random_solution import random_solution

# ── Colour palette ──────────────────────────────────────────────────────────
BG_DARK     = "#0D0D14"
BG_PANEL    = "#12121E"
BG_CARD     = "#1A1A2E"
BG_INPUT    = "#16213E"
GOLD        = "#F0C040"
GOLD_DARK   = "#A07820"
GREEN       = "#39FF14"
GREEN_DARK  = "#1A8A00"
GREEN_SOFT  = "#00C896"
RED         = "#FF4560"
BLUE        = "#00B4D8"
PURPLE      = "#7B2FBE"
WHITE       = "#E8E8F0"
GREY        = "#6A6A8A"
BORDER      = "#252540"
ACCENT      = "#0F3460"

SECTOR_COLORS = {
    "Technology":             "#00B4D8",
    "Healthcare":             "#39FF14",
    "Financials":             "#F0C040",
    "Consumer Cyclical":      "#FF9F1C",
    "Industrials":            "#A0C4FF",
    "Consumer Defensive":     "#BDE0FE",
    "Energy":                 "#FF4560",
    "Utilities":              "#9B5DE5",
    "Real Estate":            "#F15BB5",
    "Communication Services": "#00BBF9",
    "Basic Materials":        "#FEE440",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {BG_DARK};
    color: {WHITE};
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 15px;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    background-color: {BG_PANEL};
    border-radius: 0 4px 4px 4px;
}}

QTabBar::tab {{
    background-color: {BG_CARD};
    color: {GREY};
    padding: 18px 40px;
    border: 1px solid {BORDER};
    border-bottom: none;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-right: 2px;
    border-radius: 4px 4px 0 0;
}}

QTabBar::tab:selected {{
    background-color: {BG_PANEL};
    color: {GOLD};
    border-top: 3px solid {GOLD};
}}

QTabBar::tab:hover:!selected {{
    background-color: {ACCENT};
    color: {WHITE};
}}

QGroupBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 24px;
    padding: 18px;
    font-size: 13px;
    font-weight: 700;
    color: {GREY};
    letter-spacing: 2px;
    text-transform: uppercase;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    color: {GREY};
    background: {BG_CARD};
}}

QTableWidget {{
    background-color: {BG_PANEL};
    alternate-background-color: {BG_CARD};
    color: {WHITE};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 4px;
    font-size: 15px;
    selection-background-color: {ACCENT};
    selection-color: {GOLD};
    outline: none;
}}

QTableWidget::item {{
    padding: 9px 14px;
    border: none;
}}

QHeaderView::section {{
    background-color: {BG_CARD};
    color: {GREY};
    padding: 10px 14px;
    border: none;
    border-right: 1px solid {BORDER};
    border-bottom: 1px solid {GOLD_DARK};
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}}

QScrollBar:vertical {{
    background: {BG_DARK};
    width: 10px;
    border: none;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: {GOLD_DARK};
    min-height: 30px;
    border-radius: 5px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QPushButton {{
    background-color: {GOLD_DARK};
    color: {BG_DARK};
    border: none;
    padding: 13px 32px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 1px;
    border-radius: 4px;
    text-transform: uppercase;
}}

QPushButton:hover {{
    background-color: {GOLD};
}}

QPushButton:pressed {{
    background-color: #7A5A10;
}}

QPushButton:disabled {{
    background-color: #1E1E30;
    color: {GREY};
}}

QPushButton#btn_green {{
    background-color: {GREEN_DARK};
    color: {WHITE};
}}

QPushButton#btn_green:hover {{
    background-color: {GREEN};
    color: {BG_DARK};
}}

QPushButton#btn_green:disabled {{
    background-color: #0D1F0D;
    color: {GREY};
}}

QPushButton#btn_blue {{
    background-color: #0A3A5A;
    color: {BLUE};
    border: 1px solid {BLUE};
}}

QPushButton#btn_blue:hover {{
    background-color: #1050AA;
    color: {WHITE};
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {BG_INPUT};
    color: {GREEN};
    border: 1px solid {BORDER};
    border-bottom: 2px solid {GOLD_DARK};
    padding: 10px 14px;
    font-size: 17px;
    font-weight: 600;
    font-family: 'Consolas', 'Courier New', monospace;
    min-width: 160px;
    border-radius: 3px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-bottom: 2px solid {GOLD};
    background-color: #1A1A3A;
}}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background-color: {ACCENT};
    width: 24px;
    border: none;
}}

QLabel {{ color: {WHITE}; background: transparent; }}

QTextEdit {{
    background-color: {BG_PANEL};
    color: #B0FFB0;
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 14px;
    selection-background-color: {ACCENT};
}}

QProgressBar {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 3px;
    height: 10px;
    text-align: center;
    font-size: 12px;
    color: transparent;
}}

QProgressBar::chunk {{
    background-color: {GREEN_DARK};
    border-radius: 3px;
}}

QStatusBar {{
    background-color: {BG_CARD};
    color: {GOLD};
    border-top: 1px solid {BORDER};
    font-size: 14px;
    padding: 6px 14px;
}}

QScrollArea {{ border: none; background: transparent; }}
"""


def lbl(text, size=15, bold=False, color=WHITE, align=None):
    l = QLabel(text)
    f = QFont("Segoe UI", size)
    f.setBold(bold)
    l.setFont(f)
    l.setStyleSheet(f"color: {color}; background: transparent;")
    if align:
        l.setAlignment(align)
    return l


def metric_card(title, value="—", value_color=GREEN, subtitle=""):
    """Tworzy kompaktową kartę metryki."""
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1E1E38, stop:1 #141426);
            border: 1px solid {BORDER};
            border-left: 3px solid {value_color};
            border-radius: 6px;
        }}
    """)
    lay = QVBoxLayout(card)
    lay.setContentsMargins(14, 10, 14, 10)
    lay.setSpacing(3)

    t = QLabel(title.upper())
    t.setStyleSheet(f"color: {GREY}; font-size: 12px; letter-spacing: 1.5px; background: transparent;")
    t.setFont(QFont("Segoe UI", 11, QFont.Bold))

    v = QLabel(value)
    v.setStyleSheet(f"color: {value_color}; font-size: 26px; font-weight: 700; background: transparent;")
    v.setFont(QFont("Consolas", 20, QFont.Bold))
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
        self._ticker_pos = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("OPTYMALIZATOR PORTFELA — Harmony Search vs Losowy")
        self.setGeometry(60, 60, 1560, 980)
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_ticker_bar())

        self.tabs = QTabWidget()
        self.tabs.setContentsMargins(8, 8, 8, 8)
        self.tabs.tabBar().setElideMode(Qt.ElideNone)
        self.tabs.addTab(self._build_market_tab(),  "DANE RYNKOWE")
        self.tabs.addTab(self._build_random_tab(),  "LOSOWE")
        self.tabs.addTab(self._build_hs_tab(),      "HARMONY SEARCH")
        self.tabs.addTab(self._build_compare_tab(), "POROWNANIE")
        root.addWidget(self.tabs)

        sb = self.statusBar()
        sb.showMessage(f"SYSTEM GOTOWY  |  {len(self.stocks):,} akcji zaladowanych")

        self._ticker_timer = QTimer()
        self._ticker_timer.timeout.connect(self._scroll_ticker)
        self._ticker_timer.start(80)

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        h = QFrame()
        h.setFixedHeight(80)
        h.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0D0D14, stop:0.3 #0F3460, stop:0.7 #0F3460, stop:1 #0D0D14);
                border-bottom: 2px solid {GOLD_DARK};
            }}
        """)
        lay = QHBoxLayout(h)
        lay.setContentsMargins(24, 0, 24, 0)

        title = QLabel("OPTYMALIZATOR PORTFELA DYWIDENDOWEGO")
        title.setFont(QFont("Consolas", 20, QFont.Bold))
        title.setStyleSheet(f"color: {GOLD}; letter-spacing: 2px; background: transparent;")

        sub = QLabel("Algorytm Harmoniczny | Problem Plecakowy 0-1")
        sub.setFont(QFont("Segoe UI", 13))
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color: {GREY}; letter-spacing: 3px; background: transparent;")

        self.header_budget = QLabel("BUDZET:  $100,000")
        self.header_budget.setFont(QFont("Consolas", 16, QFont.Bold))
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
            f"color: {GOLD}; font-family: 'Consolas'; font-size: 12px; background: transparent;"
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

        cards_row = QHBoxLayout()
        cards_row.setSpacing(8)
        cards_row.addWidget(metric_card("Akcje", f"{len(self.stocks):,}", GOLD))
        cards_row.addWidget(metric_card("Sektory", str(len(sectors)), BLUE))
        cards_row.addWidget(metric_card("Śr. koszt lotu", f"${total_cost/len(self.stocks):,.0f}", GREEN_SOFT))
        cards_row.addWidget(metric_card("Śr. roczna dywidenda", f"${total_div/len(self.stocks):,.2f}", GREEN))
        cards_row.addWidget(metric_card("Śr. stopa dywidendy", f"{avg_yield:.2f}%", GOLD))
        lay.addLayout(cards_row)

        lbl_title = lbl("DANE RYNKOWE  —  WSZYSTKIE INSTRUMENTY", 14, bold=True, color=GREY)
        lbl_title.setStyleSheet(f"color: {GREY}; letter-spacing: 2px; padding: 4px 0;")
        lay.addWidget(lbl_title)

        self.market_table = QTableWidget()
        self._populate_market_table()
        lay.addWidget(self.market_table)
        return w

    def _populate_market_table(self):
        headers = ["TICKER", "SEKTOR", "CENA AKCJI", "ROZMIAR LOTU", "KOSZT LOTU", "DYWIDENDA ROK.", "YIELD %"]
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
        ctrl_lay = QHBoxLayout(ctrl)
        ctrl_lay.setSpacing(20)

        budget_group = QVBoxLayout()
        budget_group.addWidget(lbl("Budżet ($)", 10, bold=True, color=GREY))
        self.rand_budget = QSpinBox()
        self.rand_budget.setRange(10000, 1000000)
        self.rand_budget.setValue(100000)
        self.rand_budget.setSingleStep(10000)
        self.rand_budget.setPrefix("$ ")
        self.rand_budget.valueChanged.connect(
            lambda v: self.header_budget.setText(f"BUDZET:  ${v:,}")
        )
        budget_group.addWidget(self.rand_budget)
        ctrl_lay.addLayout(budget_group)

        ctrl_lay.addStretch()

        info_lbl = lbl("Każde uruchomienie daje inne losowe rozwiązanie.", 14, color=GREY)
        ctrl_lay.addWidget(info_lbl)

        ctrl_lay.addStretch()

        self.rand_btn = QPushButton("GENERUJ LOSOWE ROZWIAZANIE")
        self.rand_btn.setFixedHeight(48)
        self.rand_btn.clicked.connect(self.run_random_solution)
        ctrl_lay.addWidget(self.rand_btn)

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
        self.rand_table.setColumnCount(7)
        self.rand_table.setHorizontalHeaderLabels(
            ["TICKER", "SEKTOR", "CENA AKCJI", "KOSZT LOTU", "DYWIDENDA ROK.", "YIELD %", ""]
        )
        self.rand_table.setAlternatingRowColors(True)
        self.rand_table.verticalHeader().setVisible(False)
        self.rand_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rand_table.setSelectionBehavior(QTableWidget.SelectRows)
        hdr = self.rand_table.horizontalHeader()
        for i in range(7):
            hdr.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hdr.setStretchLastSection(True)
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
            pg_lay.addWidget(lbl(label_text, 14, bold=True, color=GREY), row, 0)
            pg_lay.addWidget(widget_obj, row, 1)
            h = lbl(hint, 13, color=GOLD_DARK)
            pg_lay.addWidget(h, row, 2)

        self.hs_budget = QSpinBox()
        self.hs_budget.setRange(10000, 1000000)
        self.hs_budget.setValue(100000)
        self.hs_budget.setSingleStep(10000)
        self.hs_budget.setPrefix("$ ")
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
        self.hs_par.setValue(0.3)
        self.hs_par.setSingleStep(0.05)
        self.hs_par.setDecimals(2)
        param_row_hs(3, "PAR — Pitch Adjusting Rate", self.hs_par,
                     "Prawdopodobieństwo dostrojenia wektora  [0–1]")

        self.hs_iter = QSpinBox()
        self.hs_iter.setRange(100, 100000)
        self.hs_iter.setValue(100)
        self.hs_iter.setSingleStep(100)
        param_row_hs(4, "N — Liczba iteracji", self.hs_iter, "Liczba krokow optymalizacji  [100–100000]")

        lay.addWidget(params_group)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.hs_init_btn = QPushButton("INICJALIZUJ PAMIEC HARMONII")
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
            f"border-radius: 4px; padding: 10px 14px; font-size: 12px;"
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
        self.hs_table.setColumnCount(7)
        self.hs_table.setHorizontalHeaderLabels(
            ["TICKER", "SEKTOR", "CENA AKCJI", "KOSZT LOTU", "DYWIDENDA ROK.", "YIELD %", ""]
        )
        self.hs_table.setAlternatingRowColors(True)
        self.hs_table.verticalHeader().setVisible(False)
        self.hs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.hs_table.setSelectionBehavior(QTableWidget.SelectRows)
        hdr2 = self.hs_table.horizontalHeader()
        for i in range(7):
            hdr2.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hdr2.setStretchLastSection(True)

        # Log
        log_grp = QGroupBox("Logi algorytmu")
        log_lay = QVBoxLayout(log_grp)
        self.hs_log = QTextEdit()
        self.hs_log.setReadOnly(True)
        self.hs_log.setFixedHeight(160)
        self.hs_log.setPlaceholderText("Tu pojawią się logi z działania Harmony Search...")
        log_clear = QPushButton("WYCZYŚĆ LOGI")
        log_clear.setFixedHeight(34)
        log_clear.clicked.connect(self.hs_log.clear)
        log_lay.addWidget(self.hs_log)
        log_lay.addWidget(log_clear)

        lay.addWidget(self.hs_table, 3)
        lay.addWidget(log_grp, 1)

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
        self.hspar_par.setValue(0.2)
        self.hspar_par.setSingleStep(0.05)
        self.hspar_par.setDecimals(2)
        param_row(3, "PAR — Pitch Adjusting Rate (mutacja)", self.hspar_par,
                  "Prawdopodobieństwo zamiany akcji w harmonii  [0.1–0.3]")

        self.hspar_iter = QSpinBox()
        self.hspar_iter.setRange(100, 100000)
        self.hspar_iter.setValue(100)
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

        self.hspar_init_btn = QPushButton("INICJALIZUJ PAMIEC")
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
            f"border-radius: 4px; padding: 10px 14px; font-size: 12px;"
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
        self.hspar_table.setColumnCount(7)
        self.hspar_table.setHorizontalHeaderLabels(
            ["TICKER", "SEKTOR", "CENA AKCJI", "KOSZT LOTU", "DYWIDENDA ROK.", "YIELD %", ""]
        )
        self.hspar_table.setAlternatingRowColors(True)
        self.hspar_table.verticalHeader().setVisible(False)
        self.hspar_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.hspar_table.setSelectionBehavior(QTableWidget.SelectRows)
        hdr3 = self.hspar_table.horizontalHeader()
        for i in range(7):
            hdr3.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hdr3.setStretchLastSection(True)

        log_grp = QGroupBox("Logi algorytmu (z informacją o mutacjach)")
        log_lay = QVBoxLayout(log_grp)
        self.hspar_log = QTextEdit()
        self.hspar_log.setReadOnly(True)
        self.hspar_log.setFixedHeight(150)
        self.hspar_log.setPlaceholderText("Tu pojawią się logi — w tym informacje kiedy PAR wykonał mutację...")
        log_clear = QPushButton("WYCZYŚĆ LOGI")
        log_clear.setFixedHeight(34)
        log_clear.clicked.connect(self.hspar_log.clear)
        log_lay.addWidget(self.hspar_log)
        log_lay.addWidget(log_clear)

        lay.addWidget(self.hspar_table, 3)
        lay.addWidget(log_grp, 1)

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
            f"color: {GOLD}; background: {BG_CARD}; border: 1px solid {GOLD_DARK}; "
            f"border-radius: 4px; padding: 10px 14px;"
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
            f"Pamiec zainicjalizowana  |  HMS={self.hspar_config.HMS}  |  Best: ${best:,.2f}"
        )
        self.hspar_status.setStyleSheet(
            f"color: {GREEN}; background: #0A1F0E; border: 1px solid {GREEN_DARK}; "
            f"border-radius: 4px; padding: 10px 14px;"
        )
        self.hspar_run_btn.setEnabled(True)

    def hspar_run(self):
        if not self.hspar_config or not self.hspar_config.harmony_memory:
            return

        self.hspar_status.setText("Uruchamianie HS z mutacjami PAR...")
        self.hspar_status.setStyleSheet(
            f"color: {GOLD}; background: {BG_CARD}; border: 1px solid {GOLD_DARK}; "
            f"border-radius: 4px; padding: 10px 14px;"
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
            f"Zakonczone  |  Dywidenda: ${best_score:,.2f}/rok  |  "
            f"Mutacji PAR: {mutation_count}  |  Koszt: ${total_cost:,.2f}"
        )
        self.hspar_status.setStyleSheet(
            f"color: {GREEN}; background: #0A1F0E; border: 1px solid {GREEN_DARK}; "
            f"border-radius: 4px; padding: 10px 14px;"
        )
        self.hspar_run_btn.setEnabled(True)
        self.hspar_init_btn.setEnabled(True)
        self.statusBar().showMessage(
            f"HS+PAR GOTOWY  |  Dywidenda: ${best_score:,.2f}  |  Mutacji: {mutation_count}"
        )
        self._refresh_comparison()

    # ── Comparison Tab ────────────────────────────────────────────────────────

    def _build_compare_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(14)

        title = lbl("PORÓWNANIE METOD OPTYMALIZACJI", 13, bold=True, color=GOLD)
        title.setStyleSheet(f"color: {GOLD}; letter-spacing: 2px; padding: 4px 0;")
        lay.addWidget(title)

        hint = lbl(
            "Uruchom wszystkie trzy metody — wyniki pojawią się tu automatycznie.",
            14, color=GREY
        )
        lay.addWidget(hint)

        # Comparison grid — 4 columns: metryka | losowe | HS | roznica
        grid = QGridLayout()
        grid.setSpacing(10)

        for col, (text, color) in enumerate([
            ("METRYKA", GREY), ("LOSOWE", BLUE), ("HARMONY SEARCH", GREEN), ("ROZNICA (HS vs Losowe)", GOLD)
        ]):
            h = lbl(text, 13, bold=True, color=color)
            h.setStyleSheet(
                f"color: {color}; background: {BG_CARD}; border-bottom: 2px solid {color}; "
                f"padding: 8px 14px; letter-spacing: 1px;"
            )
            h.setAlignment(Qt.AlignCenter)
            grid.addWidget(h, 0, col)

        metrics = [
            ("Roczna dywidenda ($)",  "_cmp_div",    lambda x: f"${x:,.2f}", True),
            ("Koszt portfela ($)",    "_cmp_cost",   lambda x: f"${x:,.2f}", False),
            ("Stopa dywidendy (%)",   "_cmp_yield",  lambda x: f"{x:.3f}%",  True),
            ("Liczba akcji",          "_cmp_stocks", lambda x: str(int(x)),  True),
        ]

        for row_i, (metric_name, attr, fmt_fn, higher_is_better) in enumerate(metrics, 1):
            grid.addWidget(lbl(metric_name, 15, color=WHITE), row_i, 0)

            colors = [BLUE, GREEN, GOLD]
            suffixes = ["_rand", "_hs", "_diff"]
            for col_j, (suffix, color) in enumerate(zip(suffixes, colors), 1):
                v = lbl("—", 13, bold=(col_j == 3), color=color)
                v.setAlignment(Qt.AlignCenter)
                v.setStyleSheet(
                    f"color: {color}; background: {BG_CARD}; border: 1px solid {BORDER}; "
                    f"border-radius: 4px; padding: 8px;"
                )
                setattr(self, attr + suffix, v)
                grid.addWidget(v, row_i, col_j)

        lay.addLayout(grid)
        lay.addWidget(separator())

        # Winner banner
        self._cmp_winner = lbl("Uruchom obie metody aby zobaczyc porownanie.", 14, bold=True, color=GREY)
        self._cmp_winner.setAlignment(Qt.AlignCenter)
        self._cmp_winner.setStyleSheet(
            f"color: {GREY}; background: {BG_CARD}; border: 1px solid {BORDER}; "
            f"border-radius: 8px; padding: 20px; font-size: 16px;"
        )
        lay.addWidget(self._cmp_winner)

        # Sector comparison — 2 columns
        sec_row = QHBoxLayout()
        sec_row.setSpacing(10)

        rand_sec_grp = QGroupBox("Sektory — Losowe")
        self._cmp_rand_sec_lay = QVBoxLayout(rand_sec_grp)
        self._cmp_rand_sec_lbl = lbl("(brak danych)", 13, color=GREY)
        self._cmp_rand_sec_lay.addWidget(self._cmp_rand_sec_lbl)
        sec_row.addWidget(rand_sec_grp)

        hs_sec_grp = QGroupBox("Sektory — Harmony Search")
        self._cmp_hs_sec_lay = QVBoxLayout(hs_sec_grp)
        self._cmp_hs_sec_lbl = lbl("(brak danych)", 13, color=GREY)
        self._cmp_hs_sec_lay.addWidget(self._cmp_hs_sec_lbl)
        sec_row.addWidget(hs_sec_grp)

        lay.addLayout(sec_row)
        lay.addStretch()
        return w

    # ── Logic: Random ─────────────────────────────────────────────────────────

    def run_random_solution(self):
        budget = self.rand_budget.value()

        sector_limits = {
            "Technology": 3, "Energy": 2, "Healthcare": 3, "Financials": 3,
            "Consumer Defensive": 3, "Consumer Cyclical": 3, "Industrials": 3,
            "Basic Materials": 2, "Real Estate": 2, "Utilities": 2,
            "Communication Services": 2
        }

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
        self._refresh_comparison()

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
            f"color: {GOLD}; background: {BG_CARD}; border: 1px solid {GOLD_DARK}; "
            f"border-radius: 4px; padding: 10px 14px;"
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
            f"Pamiec zainicjalizowana  |  HMS={self.config.HMS}  |  "
            f"Best: ${best:,.2f}  |  Avg: ${avg:,.2f}"
        )
        self.hs_status.setStyleSheet(
            f"color: {GREEN}; background: #0A1F0E; border: 1px solid {GREEN_DARK}; "
            f"border-radius: 4px; padding: 10px 14px;"
        )
        self.hs_run_btn.setEnabled(True)
        self.statusBar().showMessage(f"PAMIĘĆ HARMONII GOTOWA  |  HMS={self.config.HMS}")

    def hs_run(self):
        if not self.config or not self.config.harmony_memory:
            return

        self.hs_status.setText("Uruchamianie Harmony Search...")
        self.hs_status.setStyleSheet(
            f"color: {GOLD}; background: {BG_CARD}; border: 1px solid {GOLD_DARK}; "
            f"border-radius: 4px; padding: 10px 14px;"
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
            f"Optymalizacja zakonczona  |  Najlepsza dywidenda: ${best_score:,.2f}/rok  |  "
            f"Akcji: {len(selected_stocks)}  |  Koszt: ${total_cost:,.2f}"
        )
        self.hs_status.setStyleSheet(
            f"color: {GREEN}; background: #0A1F0E; border: 1px solid {GREEN_DARK}; "
            f"border-radius: 4px; padding: 10px 14px;"
        )
        self.hs_run_btn.setEnabled(True)
        self.hs_init_btn.setEnabled(True)
        self.hs_export_btn.setEnabled(True)

        self.statusBar().showMessage(
            f"HARMONY SEARCH GOTOWY  |  Dywidenda: ${best_score:,.2f}  |  "
            f"Koszt: ${total_cost:,.2f}  |  Akcji: {len(selected_stocks)}"
        )
        self._refresh_comparison()

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

    # ── Comparison refresh ────────────────────────────────────────────────────

    def _refresh_comparison(self):
        r = self._random_result
        h = self._hs_result

        if not r and not h:
            return

        def fmt_diff(a, b, fmt_fn, higher_is_better=True):
            if a is None or b is None:
                return "—", GREY
            diff = b - a
            pct = diff / a * 100 if a else 0
            sign = "+" if diff > 0 else "-"
            color = GREEN if (diff > 0) == higher_is_better else RED
            return f"{sign} {fmt_fn(abs(diff))}  ({sign}{abs(pct):.1f}%)", color

        metrics = [
            ("_cmp_div",    "total_dividend",      lambda x: f"${x:,.2f}", True),
            ("_cmp_cost",   "total_cost",           lambda x: f"${x:,.2f}", False),
            ("_cmp_yield",  "total_dividend_yield", lambda x: f"{x:.3f}%",  True),
            ("_cmp_stocks", "num_stocks",           lambda x: str(int(x)),  True),
        ]

        for attr, key, fmt_fn, hib in metrics:
            r_val = r[key] if r else None
            h_val = h[key] if h else None

            getattr(self, attr + "_rand").setText(fmt_fn(r_val) if r_val is not None else "—")
            getattr(self, attr + "_hs").setText(fmt_fn(h_val)   if h_val is not None else "—")

            diff_text, diff_color = fmt_diff(r_val, h_val, fmt_fn, hib)
            diff_lbl = getattr(self, attr + "_diff")
            diff_lbl.setText(diff_text)
            diff_lbl.setStyleSheet(
                f"color: {diff_color}; background: {BG_CARD}; border: 1px solid {BORDER}; "
                f"border-radius: 4px; padding: 8px;"
            )

        if r and h:
            if h["total_dividend"] > r["total_dividend"]:
                diff_pct = (h["total_dividend"] - r["total_dividend"]) / r["total_dividend"] * 100
                self._cmp_winner.setText(
                    f"HARMONY SEARCH WYGRYWA  |  ${h['total_dividend']:,.2f}/rok  "
                    f"(+{diff_pct:.1f}% wiecej niz losowe)"
                )
                self._cmp_winner.setStyleSheet(
                    f"color: {GREEN}; background: #0A1F0E; border: 2px solid {GREEN_DARK}; "
                    f"border-radius: 8px; padding: 20px; font-size: 16px; font-weight: 700;"
                )
            else:
                diff_pct = (r["total_dividend"] - h["total_dividend"]) / h["total_dividend"] * 100
                self._cmp_winner.setText(
                    f"ROZWIAZANIE LOSOWE WYGRYWA  |  ${r['total_dividend']:,.2f}/rok  "
                    f"(+{diff_pct:.1f}% wiecej niz HS)"
                )
                self._cmp_winner.setStyleSheet(
                    f"color: {BLUE}; background: #0A0F2A; border: 2px solid {BLUE}; "
                    f"border-radius: 8px; padding: 20px; font-size: 16px; font-weight: 700;"
                )

        if r:
            self._update_sector_display(self._cmp_rand_sec_lay, self._cmp_rand_sec_lbl, r["sector_counts"])
        if h:
            self._update_sector_display(self._cmp_hs_sec_lay, self._cmp_hs_sec_lbl, h["sector_counts"])

    def _update_sector_display(self, layout, old_label, sector_counts):
        # Remove old sector widgets
        for i in reversed(range(layout.count())):
            w = layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        bar = SectorBar(sector_counts)
        layout.addWidget(bar)
        for sector, count in sorted(sector_counts.items(), key=lambda x: -x[1]):
            color = SECTOR_COLORS.get(sector, GREY)
            row_w = QWidget()
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(0, 1, 0, 1)
            row_l.setSpacing(8)
            name_l = lbl(sector, 14, color=color)
            cnt_l  = lbl(f"×{count}", 14, bold=True, color=WHITE)
            row_l.addWidget(name_l)
            row_l.addStretch()
            row_l.addWidget(cnt_l)
            layout.addWidget(row_w)

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
                ("",                                   GREY,  Qt.AlignCenter),
            ]):
                item = QTableWidgetItem(text)
                item.setForeground(QColor(color))
                item.setTextAlignment(align)
                table.setItem(row, col, item)


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