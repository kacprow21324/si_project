"""
Aplikacja desktopowa do wizualizacji danych akcji dywidendowych
oraz konfiguracji algorytmu Harmony Search.
Wall Street / American Capitalism Theme
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
                             QGroupBox, QTabWidget, QHeaderView, QFrame,
                             QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

from database import load_stocks
from config import HarmonySearchConfig

# ── Colour palette ──────────────────────────────────────────────────────────
BG_DARK      = "#0A0A0F"
BG_PANEL     = "#10141E"
BG_CARD      = "#161B2E"
GOLD         = "#FFD700"
GOLD_DARK    = "#B8860B"
GREEN        = "#00FF7F"
GREEN_DARK   = "#00C060"
RED          = "#FF4444"
WHITE        = "#F0F0F0"
GREY         = "#8A8A9A"
BORDER       = "#2A2E42"
ACCENT_BLUE  = "#1E3A5F"

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {BG_DARK};
    color: {WHITE};
    font-family: 'Consolas', 'Courier New', monospace;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    background-color: {BG_PANEL};
}}

QTabBar::tab {{
    background-color: {BG_CARD};
    color: {GREY};
    padding: 14px 36px;
    border: 1px solid {BORDER};
    border-bottom: none;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
    text-transform: uppercase;
}}

QTabBar::tab:selected {{
    background-color: {BG_PANEL};
    color: {GOLD};
    border-top: 3px solid {GOLD};
}}

QTabBar::tab:hover:!selected {{
    background-color: {ACCENT_BLUE};
    color: {WHITE};
}}

QGroupBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-top: 3px solid {GOLD_DARK};
    border-radius: 4px;
    margin-top: 16px;
    padding: 18px;
    font-size: 16px;
    font-weight: bold;
    color: {GOLD};
    letter-spacing: 2px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {GOLD};
}}

QTableWidget {{
    background-color: {BG_PANEL};
    alternate-background-color: {BG_CARD};
    color: {WHITE};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    font-size: 15px;
    selection-background-color: {ACCENT_BLUE};
    selection-color: {GOLD};
}}

QTableWidget::item {{
    padding: 8px 14px;
    border: none;
}}

QHeaderView::section {{
    background-color: {BG_CARD};
    color: {GOLD};
    padding: 10px 14px;
    border: none;
    border-right: 1px solid {BORDER};
    border-bottom: 2px solid {GOLD_DARK};
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 2px;
}}

QScrollBar:vertical {{
    background: {BG_DARK};
    width: 14px;
    border-left: 1px solid {BORDER};
}}

QScrollBar::handle:vertical {{
    background: {GOLD_DARK};
    min-height: 30px;
    border-radius: 4px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QPushButton {{
    background-color: {GOLD_DARK};
    color: {BG_DARK};
    border: none;
    padding: 14px 32px;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
    border-radius: 3px;
    text-transform: uppercase;
}}

QPushButton:hover {{
    background-color: {GOLD};
}}

QPushButton:pressed {{
    background-color: #8B6914;
}}

QPushButton:disabled {{
    background-color: #2A2E42;
    color: {GREY};
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {BG_CARD};
    color: {GREEN};
    border: 1px solid {BORDER};
    border-bottom: 2px solid {GOLD_DARK};
    padding: 10px 14px;
    font-size: 18px;
    font-weight: bold;
    font-family: 'Consolas', monospace;
    min-width: 160px;
    border-radius: 3px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-bottom: 2px solid {GOLD};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background-color: {ACCENT_BLUE};
    width: 24px;
    border: none;
}}

QLabel {{
    color: {WHITE};
    background: transparent;
}}

QStatusBar {{
    background-color: {BG_CARD};
    color: {GOLD};
    border-top: 1px solid {BORDER};
    font-size: 14px;
    letter-spacing: 1px;
    padding: 4px 12px;
}}

QFrame#divider {{
    color: {BORDER};
}}
"""


def make_label(text, size=14, bold=False, color=WHITE):
    lbl = QLabel(text)
    f = QFont("Consolas", size)
    f.setBold(bold)
    lbl.setFont(f)
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    return lbl


def stat_card(title, value, value_color=GREEN):
    """Tworzy kartę ze statystyką w stylu finansowego dashboardu."""
    card = QFrame()
    card.setFrameShape(QFrame.StyledPanel)
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            border-top: 3px solid {GOLD_DARK};
            border-radius: 4px;
        }}
    """)
    lay = QVBoxLayout(card)
    lay.setContentsMargins(18, 14, 18, 14)
    lay.setSpacing(6)

    t = QLabel(title.upper())
    t.setStyleSheet(f"color: {GREY}; font-size: 13px; letter-spacing: 2px; background: transparent;")
    t.setFont(QFont("Consolas", 11, QFont.Bold))

    v = QLabel(value)
    v.setStyleSheet(f"color: {value_color}; font-size: 26px; font-weight: bold; background: transparent;")
    v.setFont(QFont("Consolas", 20, QFont.Bold))

    lay.addWidget(t)
    lay.addWidget(v)
    return card


class StockPortfolioApp(QMainWindow):
    """Główne okno aplikacji do optymalizacji portfela akcji."""

    def __init__(self):
        super().__init__()
        self.stocks = load_stocks()
        self.config = None
        self._ticker_index = 0
        self.init_ui()

    # ── UI setup ─────────────────────────────────────────────────────────────

    def init_ui(self):
        self.setWindowTitle("OPTYMALIZATOR PORTFELA INWESTYCYJNEGO")
        self.setGeometry(80, 80, 1500, 960)
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_ticker_bar())

        tabs = QTabWidget()
        tabs.setContentsMargins(10, 10, 10, 10)
        tabs.addTab(self._build_data_tab(),   "MARKET DATA")
        tabs.addTab(self._build_config_tab(), "HS ALGORITHM CONFIG")
        root.addWidget(tabs)

        sb = self.statusBar()
        sb.showMessage(f"SYSTEM READY  |  {len(self.stocks):,} SECURITIES LOADED")

        # Ticker animation timer
        self._ticker_timer = QTimer()
        self._ticker_timer.timeout.connect(self._scroll_ticker)
        self._ticker_timer.start(120)

    def _build_header(self):
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0A0A0F, stop:0.4 #1E3A5F, stop:0.6 #1E3A5F, stop:1 #0A0A0F);
                border-bottom: 2px solid {GOLD_DARK};
            }}
        """)
        lay = QHBoxLayout(header)
        lay.setContentsMargins(28, 0, 28, 0)

        left = make_label("OPTYMALIZATOR", 22, bold=True, color=GOLD)
        left.setStyleSheet(f"color: {GOLD}; background: transparent; letter-spacing: 3px;")

        center = make_label("PORTFEL INWESTYCYJNY", 14, color=GREY)
        center.setAlignment(Qt.AlignCenter)
        center.setStyleSheet(f"color: {GREY}; background: transparent; letter-spacing: 5px;")

        right_val = make_label("BUDGET: $100,000", 16, bold=True, color=GREEN)
        right_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right_val.setStyleSheet(f"color: {GREEN}; background: transparent; letter-spacing: 2px;")
        self.header_budget_label = right_val

        lay.addWidget(left, 2)
        lay.addWidget(center, 3)
        lay.addWidget(right_val, 2)
        return header

    def _build_ticker_bar(self):
        bar = QFrame()
        bar.setFixedHeight(38)
        bar.setStyleSheet(f"background-color: {BG_CARD}; border-bottom: 1px solid {BORDER};")

        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(0)

        self._ticker_label = QLabel()
        self._ticker_label.setStyleSheet(f"color: {GOLD}; font-size: 15px; letter-spacing: 1px; background: transparent;")
        self._ticker_label.setFont(QFont("Consolas", 13, QFont.Bold))

        # Build full ticker string from stock data
        self._ticker_string = "   |   ".join(
            f"{s['ticker']}  ${s['share_price']:.2f}  +{s['dividend_yield']:.2f}%"
            for s in self.stocks[:60]
        ) + "   |   "
        self._ticker_pos = 0

        lay.addWidget(self._ticker_label)
        return bar

    def _scroll_ticker(self):
        display_len = 160
        s = self._ticker_string
        pos = self._ticker_pos % len(s)
        chunk = (s + s)[pos:pos + display_len]
        self._ticker_label.setText(chunk)
        self._ticker_pos += 1

    # ── Data tab ─────────────────────────────────────────────────────────────

    def _build_data_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Stat cards row
        cards_row = QHBoxLayout()
        cards_row.setSpacing(10)

        sectors = {}
        total_div = 0
        total_cost = 0
        for s in self.stocks:
            sectors[s["sector"]] = sectors.get(s["sector"], 0) + 1
            total_div += s["annual_lot_dividend"]
            total_cost += s["lot_cost"]

        avg_yield = (total_div / total_cost * 100) if total_cost else 0

        cards_row.addWidget(stat_card("Total Securities",  f"{len(self.stocks):,}",         GOLD))
        cards_row.addWidget(stat_card("Sectors Covered",   f"{len(sectors)}",               WHITE))
        cards_row.addWidget(stat_card("Avg Lot Cost",      f"${total_cost/len(self.stocks):,.0f}", GREEN))
        cards_row.addWidget(stat_card("Avg Annual Div",    f"${total_div/len(self.stocks):,.2f}", GREEN))
        cards_row.addWidget(stat_card("Avg Div Yield",     f"{avg_yield:.2f}%",             GOLD))

        layout.addLayout(cards_row)

        # Table label
        lbl = make_label("LIVE MARKET DATA  -  ALL SECURITIES", 14, bold=True, color=GOLD)
        lbl.setStyleSheet(f"color: {GOLD}; background: transparent; letter-spacing: 2px; padding: 6px 0;")
        layout.addWidget(lbl)

        self.table = QTableWidget()
        self.populate_table()
        layout.addWidget(self.table)

        return widget

    def _build_config_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Parameters group
        params_group = QGroupBox("HARMONY SEARCH PARAMETERS")
        params_layout = QVBoxLayout(params_group)
        params_layout.setSpacing(12)

        def param_row(label_text, widget_obj, hint):
            row = QHBoxLayout()
            row.setSpacing(18)
            lbl = make_label(label_text, 14, bold=True, color=GREY)
            lbl.setFixedWidth(380)
            hint_lbl = make_label(hint, 12, color=GOLD_DARK)
            hint_lbl.setAlignment(Qt.AlignVCenter)
            row.addWidget(lbl)
            row.addWidget(widget_obj)
            row.addWidget(hint_lbl)
            row.addStretch()
            return row

        # Budget
        self.budget_spin = QSpinBox()
        self.budget_spin.setRange(10000, 1000000)
        self.budget_spin.setValue(100000)
        self.budget_spin.setSingleStep(10000)
        self.budget_spin.setPrefix("$ ")
        self.budget_spin.valueChanged.connect(
            lambda v: self.header_budget_label.setText(f"BUDGET: ${v:,}")
        )
        params_layout.addLayout(param_row("BUDGET  —  Investment Capital:", self.budget_spin,
                                          "Max capital to allocate"))

        # HMS
        self.hms_spin = QSpinBox()
        self.hms_spin.setRange(5, 100)
        self.hms_spin.setValue(10)
        params_layout.addLayout(param_row("HMS  —  Harmony Memory Size:", self.hms_spin,
                                          "Number of solutions in memory  [5 – 100]"))

        # HMCR
        self.hmcr_spin = QDoubleSpinBox()
        self.hmcr_spin.setRange(0.0, 1.0)
        self.hmcr_spin.setValue(0.8)
        self.hmcr_spin.setSingleStep(0.05)
        self.hmcr_spin.setDecimals(2)
        params_layout.addLayout(param_row("HMCR  —  Memory Considering Rate:", self.hmcr_spin,
                                          "Probability of choosing from memory  [0.0 – 1.0]"))

        # PAR
        self.par_spin = QDoubleSpinBox()
        self.par_spin.setRange(0.0, 1.0)
        self.par_spin.setValue(0.3)
        self.par_spin.setSingleStep(0.05)
        self.par_spin.setDecimals(2)
        params_layout.addLayout(param_row("PAR  —  Pitch Adjusting Rate:", self.par_spin,
                                          "Probability of fine-tuning a decision  [0.0 – 1.0]"))

        # Iterations
        self.iter_spin = QSpinBox()
        self.iter_spin.setRange(10, 2000)
        self.iter_spin.setValue(100)
        self.iter_spin.setSingleStep(10)
        params_layout.addLayout(param_row("N  —  Iterations:", self.iter_spin,
                                          "Number of optimization iterations  [10 – 2000]"))

        layout.addWidget(params_group)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.init_button = QPushButton("INITIALIZE HARMONY MEMORY")
        self.init_button.setFixedHeight(56)
        self.init_button.clicked.connect(self.initialize_memory)

        self.run_button = QPushButton("RUN OPTIMIZATION")
        self.run_button.setFixedHeight(56)
        self.run_button.setEnabled(False)
        self.run_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #0D3320;
                color: {GREY};
                border: 1px solid {BORDER};
                padding: 10px 24px;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 1px;
                border-radius: 3px;
            }}
            QPushButton:enabled {{
                background-color: #0D4A1A;
                color: {GREEN};
                border: 1px solid {GREEN_DARK};
            }}
            QPushButton:enabled:hover {{
                background-color: #1A6B28;
            }}
            QPushButton:enabled {{
                font-size: 16px;
            }}
        """)

        btn_row.addWidget(self.init_button)
        btn_row.addWidget(self.run_button)
        layout.addLayout(btn_row)

        # Result cards (hidden until initialized)
        self.result_cards_row = QHBoxLayout()
        self.result_cards_row.setSpacing(10)
        self._best_card  = stat_card("Best Dividend",  "—", GREEN)
        self._worst_card = stat_card("Worst Dividend", "—", RED)
        self._avg_card   = stat_card("Avg Dividend",   "—", GOLD)
        self._hms_card   = stat_card("Harmonies",      "—", WHITE)
        for c in [self._best_card, self._worst_card, self._avg_card, self._hms_card]:
            self.result_cards_row.addWidget(c)
        layout.addLayout(self.result_cards_row)

        # Status label
        self.status_label = make_label("STATUS:  AWAITING INITIALIZATION", 14, bold=True, color=GREY)
        self.status_label.setStyleSheet(
            f"color: {GREY}; background: {BG_CARD}; border: 1px solid {BORDER}; "
            f"padding: 14px 20px; letter-spacing: 2px;"
        )
        layout.addWidget(self.status_label)

        layout.addStretch()
        return widget

    # ── Table ─────────────────────────────────────────────────────────────────

    def populate_table(self):
        headers = ["TICKER", "SECTOR", "SHARE PRICE", "LOT SIZE", "LOT COST",
                   "ANNUAL DIVIDEND", "YIELD %"]

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.stocks))
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        for row, stock in enumerate(self.stocks):
            yld = stock["dividend_yield"]
            yld_color = GREEN if yld >= 3.0 else (GOLD if yld >= 1.5 else WHITE)

            items = [
                (stock["ticker"],                          GOLD,      Qt.AlignLeft | Qt.AlignVCenter),
                (stock["sector"],                          GREY,      Qt.AlignLeft | Qt.AlignVCenter),
                (f"${stock['share_price']:.2f}",           WHITE,     Qt.AlignRight | Qt.AlignVCenter),
                (str(stock["lot_size"]),                   GREY,      Qt.AlignCenter),
                (f"${stock['lot_cost']:,.2f}",             WHITE,     Qt.AlignRight | Qt.AlignVCenter),
                (f"${stock['annual_lot_dividend']:.2f}",   GREEN,     Qt.AlignRight | Qt.AlignVCenter),
                (f"{yld:.2f}%",                            yld_color, Qt.AlignRight | Qt.AlignVCenter),
            ]

            for col, (text, color, align) in enumerate(items):
                item = QTableWidgetItem(text)
                item.setForeground(QColor(color))
                item.setTextAlignment(align)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

        hdr = self.table.horizontalHeader()
        for i in range(len(headers)):
            hdr.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hdr.setStretchLastSection(True)

    # ── Logic ─────────────────────────────────────────────────────────────────

    def initialize_memory(self):
        budget     = self.budget_spin.value()
        HMS        = self.hms_spin.value()
        HMCR       = self.hmcr_spin.value()
        PAR        = self.par_spin.value()
        iterations = self.iter_spin.value()

        self.config = HarmonySearchConfig(
            budget=budget, HMS=HMS, HMCR=HMCR, PAR=PAR,
            iterations=iterations, seed=42
        )

        self.status_label.setText("STATUS:  INITIALIZING HARMONY MEMORY…")
        self.status_label.setStyleSheet(
            f"color: {GOLD}; background: {BG_CARD}; border: 1px solid {GOLD_DARK}; "
            f"padding: 10px 16px; letter-spacing: 1px;"
        )
        QApplication.processEvents()

        harmony_memory, scores = self.config.initialize_harmony_memory()

        best   = max(scores)
        worst  = min(scores)
        avg    = sum(scores) / len(scores)

        # Update result cards
        def _update_card(card, value):
            card.findChildren(QLabel)[1].setText(value)

        _update_card(self._best_card,  f"${best:,.2f}")
        _update_card(self._worst_card, f"${worst:,.2f}")
        _update_card(self._avg_card,   f"${avg:,.2f}")
        _update_card(self._hms_card,   str(HMS))

        self.status_label.setText(
            f"STATUS:  ✔  MEMORY INITIALIZED  |  HMS={HMS}  |  "
            f"BEST=${best:,.2f}  |  AVG=${avg:,.2f}"
        )
        self.status_label.setStyleSheet(
            f"color: {GREEN}; background: #0A1F0E; border: 1px solid {GREEN_DARK}; "
            f"padding: 14px 20px; letter-spacing: 2px;"
        )

        self.run_button.setEnabled(True)
        self.statusBar().showMessage(
            f"MEMORY INITIALIZED  |  HMS={HMS}  HMCR={HMCR}  PAR={PAR}  "
            f"N={iterations}  |  BEST HARMONY: ${best:,.2f}/yr"
        )


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Force dark palette so native widgets don't flash white
    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor(BG_DARK))
    palette.setColor(QPalette.WindowText,      QColor(WHITE))
    palette.setColor(QPalette.Base,            QColor(BG_PANEL))
    palette.setColor(QPalette.AlternateBase,   QColor(BG_CARD))
    palette.setColor(QPalette.Text,            QColor(WHITE))
    palette.setColor(QPalette.Button,          QColor(BG_CARD))
    palette.setColor(QPalette.ButtonText,      QColor(WHITE))
    palette.setColor(QPalette.Highlight,       QColor(ACCENT_BLUE))
    palette.setColor(QPalette.HighlightedText, QColor(GOLD))
    app.setPalette(palette)

    window = StockPortfolioApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
