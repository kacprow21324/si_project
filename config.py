"""
Inicjalizacja parametrów algorytmu Harmony Search
i pamięci harmonii dla problemu optymalizacji portfela.
"""

import random
from database import load_stocks


class HarmonySearchConfig:
    """Konfiguracja parametrów algorytmu Harmony Search."""
    
    def __init__(self, budget=100000, HMS=10, HMCR=0.8, PAR=0.3, iterations=100, seed=None):
        """
        Inicjalizuje parametry algorytmu.
        
        Args:
            budget: Maksymalny budżet inwestycyjny (domyślnie 100000)
            HMS: Harmony Memory Size - rozmiar pamięci harmonii (domyślnie 10)
            HMCR: Harmony Memory Considering Rate - prawdopodobieństwo wyboru z pamięci (domyślnie 0.8)
            PAR: Pitch Adjusting Rate - prawdopodobieństwo dostrojenia (domyślnie 0.3)
            iterations: Liczba iteracji algorytmu (domyślnie 100)
            seed: Ziarno generatora losowego dla powtarzalności wyników
        """
        # Parametry problemu
        self.budget = budget
        self.sector_limits = {
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
            "Communication Services": 2
        }
        
        # Parametry algorytmu Harmony Search
        self.HMS = HMS          # Rozmiar pamięci harmonii
        self.HMCR = HMCR        # Harmony Memory Considering Rate
        self.PAR = PAR          # Pitch Adjusting Rate
        self.iterations = iterations  # Liczba iteracji (n)
        
        # Generator losowy
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # Dane akcji
        self.stocks = load_stocks()
        
        # Pamięć harmonii (zostanie zainicjalizowana)
        self.harmony_memory = []
        self.harmony_scores = []
        
    def initialize_harmony_memory(self):
        """
        Inicjalizuje pamięć harmonii losowymi rozwiązaniami.
        Generuje HMS rozwiązań i zapisuje je w pamięci.
        """
        print(f"Inicjalizacja pamięci harmonii...")
        print(f"  HMS (rozmiar pamięci): {self.HMS}")
        print(f"  Liczba dostępnych akcji: {len(self.stocks)}")
        print(f"  Budżet: ${self.budget:,.2f}")
        
        self.harmony_memory = []
        self.harmony_scores = []
        
        for i in range(self.HMS):
            harmony = self._generate_random_harmony()
            score = self._evaluate_harmony(harmony)
            
            self.harmony_memory.append(harmony)
            self.harmony_scores.append(score)
            
            print(f"  Harmonia {i+1}/{self.HMS}: {len(harmony)} akcji, dywidenda ${score:.2f}")
        
        best_score = max(self.harmony_scores)
        print(f"\nPamięć zainicjalizowana!")
        print(f"Najlepsza początkowa harmonia: ${best_score:.2f} dywidendy rocznie")
        
        return self.harmony_memory, self.harmony_scores
    
    def _generate_random_harmony(self):
        """Generuje losową harmonię (rozwiązanie)."""
        selected_indices = []
        total_cost = 0
        sector_counts = {}
        
        # Losowa kolejność rozważania akcji
        indices = list(range(len(self.stocks)))
        random.shuffle(indices)
        
        for idx in indices:
            stock = self.stocks[idx]
            
            # Sprawdź ograniczenie budżetowe
            if total_cost + stock["lot_cost"] > self.budget:
                continue
            
            # Sprawdź ograniczenia sektorowe
            sector = stock["sector"]
            current_count = sector_counts.get(sector, 0)
            sector_limit = self.sector_limits.get(sector, float('inf'))
            
            if current_count >= sector_limit:
                continue
            
            # Dodaj akcję do harmonii
            selected_indices.append(idx)
            total_cost += stock["lot_cost"]
            sector_counts[sector] = current_count + 1
        
        return selected_indices
    
    def _evaluate_harmony(self, harmony_indices):
        """
        Ocenia harmonię (rozwiązanie).
        
        Args:
            harmony_indices: Lista indeksów wybranych akcji
        
        Returns:
            float: Wartość funkcji celu (roczna dywidenda) lub 0 jeśli nielegalne
        """
        total_cost = 0
        total_dividend = 0
        sector_counts = {}
        
        for idx in harmony_indices:
            stock = self.stocks[idx]
            total_cost += stock["lot_cost"]
            total_dividend += stock["annual_lot_dividend"]
            
            sector = stock["sector"]
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        # Sprawdź ograniczenia
        if total_cost > self.budget:
            return 0
        
        for sector, count in sector_counts.items():
            if count > self.sector_limits.get(sector, float('inf')):
                return 0
        
        return total_dividend
    
    def get_summary(self):
        """Zwraca podsumowanie konfiguracji."""
        return {
            "budget": self.budget,
            "HMS": self.HMS,
            "HMCR": self.HMCR,
            "PAR": self.PAR,
            "iterations": self.iterations,
            "num_stocks": len(self.stocks),
            "memory_initialized": len(self.harmony_memory) > 0,
            "sector_limits": self.sector_limits
        }
    
    def print_config(self):
        """Wyświetla konfigurację."""
        print("=" * 70)
        print("KONFIGURACJA HARMONY SEARCH")
        print("=" * 70)
        print(f"Budżet inwestycyjny: ${self.budget:,.2f}")
        print(f"Liczba dostępnych akcji: {len(self.stocks)}")
        print(f"\nParametry algorytmu:")
        print(f"  HMS (Harmony Memory Size): {self.HMS}")
        print(f"  HMCR (Harmony Memory Considering Rate): {self.HMCR}")
        print(f"  PAR (Pitch Adjusting Rate): {self.PAR}")
        print(f"  Iteracje (n): {self.iterations}")
        print(f"\nLimity sektorowe:")
        for sector, limit in sorted(self.sector_limits.items()):
            print(f"  {sector}: max {limit} akcji")
        print("=" * 70)


if __name__ == "__main__":
    # Przykład użycia
    print("INICJALIZACJA PARAMETRÓW HARMONY SEARCH\n")
    
    # Utworzenie konfiguracji z domyślnymi parametrami
    config = HarmonySearchConfig(
        budget=100000,
        HMS=10,
        HMCR=0.8,
        PAR=0.3,
        iterations=100,
        seed=42
    )
    
    # Wyświetl konfigurację
    config.print_config()
    
    print("\n")
    
    # Zainicjalizuj pamięć harmonii
    harmony_memory, scores = config.initialize_harmony_memory()
    
    print(f"\nPamięć harmonii została zainicjalizowana z {len(harmony_memory)} harmonii.")
    print(f"Zakres wartości: ${min(scores):.2f} - ${max(scores):.2f}")
