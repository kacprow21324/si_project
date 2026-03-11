"""
Generator danych CSV dla Dividend Portfolio Optimizer.
Generuje 10 000 rekordów symulujących pakiety akcji spółek dywidendowych S&P 500.
"""

import csv
import random
import string

# ── Konfiguracja ──────────────────────────────────────────────────────────────

OUTPUT_FILE = "stock_data.csv"
NUM_RECORDS = 10_000
LOT_SIZE = 100  # sztuk w pakiecie

# Sektory S&P 500 z wagami (prawdopodobieństwo wystąpienia)
SECTORS = {
    "Technology":        0.18,
    "Healthcare":        0.13,
    "Financials":        0.13,
    "Consumer Cyclical": 0.10,
    "Industrials":       0.10,
    "Consumer Defensive":0.08,
    "Energy":            0.06,
    "Utilities":         0.06,
    "Real Estate":       0.05,
    "Communication Services": 0.05,
    "Basic Materials":   0.06,
}

# Parametry cenowe i dywidendowe per sektor
# share_price_range: (min, max) cena jednej akcji w USD
# dividend_yield_range: (min, max) roczna stopa dywidendy (0.01 = 1%)
SECTOR_PARAMS = {
    "Technology":            {"share_price_range": (50, 450),  "dividend_yield_range": (0.003, 0.025)},
    "Healthcare":            {"share_price_range": (40, 400),  "dividend_yield_range": (0.008, 0.035)},
    "Financials":            {"share_price_range": (20, 200),  "dividend_yield_range": (0.015, 0.050)},
    "Consumer Cyclical":     {"share_price_range": (30, 350),  "dividend_yield_range": (0.005, 0.030)},
    "Industrials":           {"share_price_range": (40, 300),  "dividend_yield_range": (0.010, 0.035)},
    "Consumer Defensive":    {"share_price_range": (30, 250),  "dividend_yield_range": (0.015, 0.045)},
    "Energy":                {"share_price_range": (30, 250),  "dividend_yield_range": (0.020, 0.060)},
    "Utilities":             {"share_price_range": (25, 120),  "dividend_yield_range": (0.025, 0.055)},
    "Real Estate":           {"share_price_range": (15, 150),  "dividend_yield_range": (0.030, 0.070)},
    "Communication Services":{"share_price_range": (20, 300),  "dividend_yield_range": (0.005, 0.040)},
    "Basic Materials":       {"share_price_range": (30, 200),  "dividend_yield_range": (0.010, 0.040)},
}

# ── Generowanie tickerów ─────────────────────────────────────────────────────

def generate_unique_tickers(n: int) -> list[str]:
    """Generuje n unikalnych tickerów 2-5 literowych."""
    tickers: set[str] = set()
    while len(tickers) < n:
        length = random.choices([2, 3, 4, 5], weights=[5, 50, 30, 15])[0]
        ticker = "".join(random.choices(string.ascii_uppercase, k=length))
        tickers.add(ticker)
    return list(tickers)


# ── Generowanie rekordów ─────────────────────────────────────────────────────

def generate_records(n: int) -> list[dict]:
    sector_names = list(SECTORS.keys())
    sector_weights = list(SECTORS.values())
    tickers = generate_unique_tickers(n)

    records = []
    for ticker in tickers:
        sector = random.choices(sector_names, weights=sector_weights, k=1)[0]
        params = SECTOR_PARAMS[sector]

        # Cena jednej akcji (zaokrąglona do centów)
        share_price = round(random.uniform(*params["share_price_range"]), 2)

        # Koszt pakietu (lot)
        lot_cost = round(share_price * LOT_SIZE, 2)

        # Stopa dywidendy
        div_yield = random.uniform(*params["dividend_yield_range"])

        # Roczna dywidenda z pakietu
        annual_lot_dividend = round(lot_cost * div_yield, 2)

        records.append({
            "Ticker": ticker,
            "Sector": sector,
            "Share_Price": share_price,
            "Lot_Size": LOT_SIZE,
            "Lot_Cost": lot_cost,
            "Annual_Lot_Dividend": annual_lot_dividend,
            "Dividend_Yield": round(div_yield * 100, 4),  # w procentach
        })

    return records


# ── Zapis do CSV ──────────────────────────────────────────────────────────────

def save_csv(records: list[dict], path: str) -> None:
    fieldnames = [
        "Ticker",
        "Sector",
        "Share_Price",
        "Lot_Size",
        "Lot_Cost",
        "Annual_Lot_Dividend",
        "Dividend_Yield",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    random.seed(42)  # powtarzalność wyników
    print(f"Generowanie {NUM_RECORDS} rekordów...")
    data = generate_records(NUM_RECORDS)
    save_csv(data, OUTPUT_FILE)
    print(f"Zapisano do {OUTPUT_FILE}")

    # Podsumowanie
    sectors_count: dict[str, int] = {}
    for r in data:
        sectors_count[r["Sector"]] = sectors_count.get(r["Sector"], 0) + 1

    print("\n── Podsumowanie per sektor ──")
    print(f"{'Sektor':<28} {'Liczba':>6}  {'Śr. koszt lotu':>15}  {'Śr. dywidenda':>14}")
    print("─" * 70)
    for sector in sorted(sectors_count.keys()):
        sec_data = [r for r in data if r["Sector"] == sector]
        avg_cost = sum(r["Lot_Cost"] for r in sec_data) / len(sec_data)
        avg_div = sum(r["Annual_Lot_Dividend"] for r in sec_data) / len(sec_data)
        print(f"{sector:<28} {sectors_count[sector]:>6}  ${avg_cost:>13,.2f}  ${avg_div:>12,.2f}")

    print(f"\n{'RAZEM':<28} {len(data):>6}")
