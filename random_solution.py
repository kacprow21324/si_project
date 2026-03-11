import random
from database import load_stocks


def random_solution(budget=100000, sector_limits=None, seed=None):
    """
    Generuje losowe rozwiązanie problemu portfela inwestycyjnego.
    
    Args:
        budget: Maksymalny budżet na inwestycję (default: 100000)
        sector_limits: Słownik z limitami dla sektorów, np. {"Technology": 3, "Energy": 2}
        seed: Ziarno dla generatora losowego (dla powtarzalności)
    
    Returns:
        dict: Słownik z wynikami:
            - selected_stocks: Lista wybranych akcji
            - total_cost: Całkowity koszt portfela
            - total_dividend: Całkowita roczna dywidenda
            - sector_counts: Liczba akcji w każdym sektorze
    """
    if seed is not None:
        random.seed(seed)
    
    # Załaduj dane
    stocks = load_stocks()
    
    # Wymieszaj listę akcji losowo
    random.shuffle(stocks)
    
    # Inicjalizacja
    selected = []
    total_cost = 0
    total_dividend = 0
    sector_counts = {}
    
    # Iteruj przez losowo wymieszane akcje
    for stock in stocks:
        # Sprawdź limit budżetu
        if total_cost + stock["lot_cost"] > budget:
            continue
        
        # Sprawdź limity sektorowe (jeśli są zdefiniowane)
        if sector_limits:
            sector = stock["sector"]
            current_count = sector_counts.get(sector, 0)
            sector_limit = sector_limits.get(sector, float('inf'))
            
            if current_count >= sector_limit:
                continue
        
        # Dodaj akcję do portfela
        selected.append(stock)
        total_cost += stock["lot_cost"]
        total_dividend += stock["annual_lot_dividend"]
        
        # Aktualizuj licznik sektora
        sector = stock["sector"]
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    return {
        "selected_stocks": selected,
        "total_cost": total_cost,
        "total_dividend": total_dividend,
        "total_dividend_yield": (total_dividend / total_cost * 100) if total_cost > 0 else 0,
        "sector_counts": sector_counts,
        "num_stocks": len(selected)
    }


def print_solution(solution):
    """Wyświetla szczegóły rozwiązania w czytelny sposób."""
    print("=" * 70)
    print("LOSOWE ROZWIĄZANIE PORTFELA INWESTYCYJNEGO")
    print("=" * 70)
    print(f"Liczba wybranych akcji: {solution['num_stocks']}")
    print(f"Całkowity koszt: ${solution['total_cost']:,.2f}")
    print(f"Roczna dywidenda: ${solution['total_dividend']:,.2f}")
    print(f"Stopa dywidendy: {solution['total_dividend_yield']:.2f}%")
    print("\n" + "=" * 70)
    print("ROZKŁAD SEKTOROWY:")
    print("=" * 70)
    for sector, count in sorted(solution['sector_counts'].items()):
        print(f"  {sector}: {count} akcji")
    
    print("\n" + "=" * 70)
    print("WYBRANE AKCJE:")
    print("=" * 70)
    print(f"{'Ticker':<10} {'Sektor':<25} {'Koszt':<12} {'Dywidenda':<12} {'Yield':<8}")
    print("-" * 70)
    for stock in solution['selected_stocks']:
        print(f"{stock['ticker']:<10} {stock['sector']:<25} "
              f"${stock['lot_cost']:>10,.2f} ${stock['annual_lot_dividend']:>10,.2f} "
              f"{stock['dividend_yield']:>6.2f}%")
    print("=" * 70)


if __name__ == "__main__":
    # Przykład 1: Proste losowe rozwiązanie bez limitów sektorowych
    print("PRZYKŁAD 1: Bez limitów sektorowych")
    solution1 = random_solution(budget=100000)
    print_solution(solution1)
    
    print("\n\n")
    
    # Przykład 2: Z limitami sektorowymi
    print("PRZYKŁAD 2: Z limitami sektorowymi")
    sector_limits = {
        "Technology": 3,
        "Energy": 2,
        "Healthcare": 3,
        "Financials": 3
    }
    solution2 = random_solution(budget=100000, sector_limits=sector_limits)
    print_solution(solution2)
