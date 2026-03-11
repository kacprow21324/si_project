import csv

def load_stocks():
    """Load stock data from CSV file."""
    stocks = []
    
    with open("stock_data.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            stocks.append({
                "ticker": row["Ticker"],
                "sector": row["Sector"],
                "share_price": float(row["Share_Price"]),
                "lot_size": int(row["Lot_Size"]),
                "lot_cost": float(row["Lot_Cost"]),
                "annual_lot_dividend": float(row["Annual_Lot_Dividend"]),
                "dividend_yield": float(row["Dividend_Yield"])
            })
    
    return stocks
