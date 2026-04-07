"""
Inicjalizacja parametrów algorytmu Harmony Search
i pamięci harmonii dla problemu optymalizacji portfela.
"""

import random
from database import load_stocks


class HarmonySearchConfig:
    """Konfiguracja parametrów algorytmu Harmony Search."""

    def __init__(self, budget=100000, HMS=10, HMCR=0.7, PAR=0.15, iterations=100, seed=None):
        """
        Inicjalizuje parametry algorytmu.

        Args:
            budget: Maksymalny budżet inwestycyjny (domyślnie 100000)
            HMS: Harmony Memory Size - rozmiar pamięci harmonii (domyślnie 10)
            HMCR: Harmony Memory Considering Rate - prawdopodobienstwo wyboru z pamieci (domyslnie 0.7)
            PAR: Pitch Adjusting Rate - prawdopodobienstwo dostrojenia (domyslnie 0.15)
            iterations: Liczba iteracji algorytmu (domyslnie 100)
            seed: Ziarno generatora losowego dla powtarzalnosci wynikow
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
            "Communication Services": 2,
        }

        # Parametry algorytmu Harmony Search
        self.HMS = HMS          # Rozmiar pamieci harmonii
        self.HMCR = HMCR        # Harmony Memory Considering Rate
        self.PAR = PAR          # Pitch Adjusting Rate
        self.iterations = iterations  # Liczba iteracji (n)

        # Generator losowy
        self.seed = seed
        if seed is not None:
            random.seed(seed)

        # Dane akcji
        self.stocks = load_stocks()

        # Pamiec harmonii (zostanie zainicjalizowana)
        self.harmony_memory = []
        self.harmony_scores = []

    def initialize_harmony_memory(self):
        """
        Inicjalizuje pamiec harmonii losowymi rozwiazaniami.
        Generuje HMS rozwiazan i zapisuje je w pamieci.
        """
        print("Inicjalizacja pamieci harmonii...")
        print(f"  HMS (rozmiar pamieci): {self.HMS}")
        print(f"  Liczba dostepnych akcji: {len(self.stocks)}")
        print(f"  Budzet: ${self.budget:,.2f}")

        self.harmony_memory = []
        self.harmony_scores = []

        for i in range(self.HMS):
            harmony = self._generate_random_harmony()
            score = self._evaluate_harmony(harmony)

            self.harmony_memory.append(harmony)
            self.harmony_scores.append(score)

            print(f"  Harmonia {i + 1}/{self.HMS}: {len(harmony)} akcji, dywidenda ${score:.2f}")

        best_score = max(self.harmony_scores)
        print("\nPamiec zainicjalizowana!")
        print(f"Najlepsza poczatkowa harmonia: ${best_score:.2f} dywidendy rocznie")

        return self.harmony_memory, self.harmony_scores

    def _generate_random_harmony(self):
        """Generuje losowa harmonie (rozwiazanie)."""
        selected_indices = []
        total_cost = 0
        sector_counts = {}

        # Losowa kolejnosc rozwazania akcji
        indices = list(range(len(self.stocks)))
        random.shuffle(indices)

        for idx in indices:
            stock = self.stocks[idx]

            # Sprawdz ograniczenie budzetowe
            if total_cost + stock["lot_cost"] > self.budget:
                continue

            # Sprawdz ograniczenia sektorowe
            sector = stock["sector"]
            current_count = sector_counts.get(sector, 0)
            sector_limit = self.sector_limits.get(sector, float("inf"))

            if current_count >= sector_limit:
                continue

            # Dodaj akcje do harmonii
            selected_indices.append(idx)
            total_cost += stock["lot_cost"]
            sector_counts[sector] = current_count + 1

        return selected_indices

    def _evaluate_harmony(self, harmony_indices):
        """
        Ocenia harmonie (rozwiazanie).

        Args:
            harmony_indices: Lista indeksow wybranych akcji

        Returns:
            float: Wartość funkcji celu (roczna dywidenda) lub 0 jesli nielegalne
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

        # Sprawdz ograniczenia
        if total_cost > self.budget:
            return 0

        for sector, count in sector_counts.items():
            if count > self.sector_limits.get(sector, float("inf")):
                return 0

        return total_dividend

    def _memory_index_pool(self):
        """Zwraca unikalne indeksy akcji wystepujace w pamieci harmonii."""
        pool = set()
        for harmony in self.harmony_memory:
            pool.update(harmony)
        return list(pool)

    def _generate_harmony_from_pool(self, index_pool):
        """Buduje harmonie korzystajac tylko z indeksow dostepnych w podanej puli."""
        if not index_pool:
            return self._generate_random_harmony()

        selected_indices = []
        total_cost = 0
        sector_counts = {}

        shuffled_pool = index_pool[:]
        random.shuffle(shuffled_pool)

        for idx in shuffled_pool:
            stock = self.stocks[idx]

            if total_cost + stock["lot_cost"] > self.budget:
                continue

            sector = stock["sector"]
            current_count = sector_counts.get(sector, 0)
            sector_limit = self.sector_limits.get(sector, float("inf"))
            if current_count >= sector_limit:
                continue

            selected_indices.append(idx)
            total_cost += stock["lot_cost"]
            sector_counts[sector] = current_count + 1

        return selected_indices

    def _apply_pitch_adjustment(self, harmony_indices):
        """Dyskretny pitch adjustment: zamiana jednej akcji na inna spelniajaca ograniczenia."""
        if not harmony_indices:
            return harmony_indices

        removed_idx = random.choice(harmony_indices)
        remaining = [idx for idx in harmony_indices if idx != removed_idx]

        total_cost = 0
        sector_counts = {}
        for idx in remaining:
            stock = self.stocks[idx]
            total_cost += stock["lot_cost"]
            sector = stock["sector"]
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        remaining_set = set(remaining)
        candidates = []
        for idx, stock in enumerate(self.stocks):
            if idx in remaining_set or idx == removed_idx:
                continue

            if total_cost + stock["lot_cost"] > self.budget:
                continue

            sector = stock["sector"]
            sector_limit = self.sector_limits.get(sector, float("inf"))
            if sector_counts.get(sector, 0) + 1 > sector_limit:
                continue

            candidates.append(idx)

        if not candidates:
            return harmony_indices[:]

        new_idx = random.choice(candidates)
        remaining.append(new_idx)
        return remaining

    def _improvise_new_harmony(self):
        """
        Tworzy nowa harmonie wg regul HMCR i PAR:
        - jesli random < HMCR: wybor elementow tylko z pamieci HM,
          a nastepnie mozliwe dostrojenie (PAR),
        - w przeciwnym razie: pelne losowanie z calej przestrzeni.
        """
        draw = random.random()  # [0.0, 1.0)

        if draw < self.HMCR:
            pool = self._memory_index_pool()
            harmony = self._generate_harmony_from_pool(pool)
            source = "HM"

            par_draw = random.random()
            if par_draw < self.PAR:
                harmony = self._apply_pitch_adjustment(harmony)
                source = "HM+PAR"
        else:
            harmony = self._generate_random_harmony()
            source = "RANDOM"

        return harmony, draw, source

    def _harmony_cost(self, harmony_indices):
        """Liczy calkowity koszt harmonii."""
        return sum(self.stocks[idx]["lot_cost"] for idx in harmony_indices)

    def _harmony_tickers(self, harmony_indices):
        """Zwraca liste tickerow dla harmonii."""
        return [self.stocks[idx]["ticker"] for idx in harmony_indices]

    def print_harmony_memory(self, header="PAMIEC HARMONII", max_tickers=8):
        """Wyswietla wszystkie rozwiazania przechowywane w pamieci HM."""
        print("\n" + "=" * 90)
        print(header)
        print("=" * 90)

        if not self.harmony_memory:
            print("(brak harmonii w pamieci)")
            print("=" * 90)
            return

        ranking = sorted(
            enumerate(zip(self.harmony_memory, self.harmony_scores), start=1),
            key=lambda x: x[1][1],
            reverse=True,
        )

        for rank, (original_pos, (harmony, score)) in enumerate(ranking, start=1):
            cost = self._harmony_cost(harmony)
            tickers = self._harmony_tickers(harmony)
            shown = ", ".join(tickers[:max_tickers])
            if len(tickers) > max_tickers:
                shown += ", ..."

            print(
                f"#{rank:>2} | slot HM: {original_pos:>2} | fitness: ${score:>10.2f} | "
                f"koszt: ${cost:>11,.2f} | akcje: {len(harmony):>2}"
            )
            print(f"     tickery: {shown if shown else '(pusto)'}")

        print("=" * 90)

    def run_harmony_search(self, show_memory_every=0, verbose=True):
        """
        Uruchamia iteracyjna czesc Harmony Search.

        Args:
            show_memory_every: co ile iteracji wypisywac pelna pamiec (0 = tylko koniec)
            verbose: czy wypisywac log iteracji

        Returns:
            tuple: (najlepsza_harmonia, najlepszy_fitness)
        """
        if not self.harmony_memory:
            self.initialize_harmony_memory()

        if verbose:
            print("\nSTART HARMONY SEARCH")
            print(f"Iteracje: {self.iterations}")
            print(f"HMCR: {self.HMCR:.2f}")

        for iteration in range(1, self.iterations + 1):
            new_harmony, draw, source = self._improvise_new_harmony()
            new_score = self._evaluate_harmony(new_harmony)

            worst_score = min(self.harmony_scores)
            worst_idx = self.harmony_scores.index(worst_score)

            replaced = False
            if new_score > worst_score:
                self.harmony_memory[worst_idx] = new_harmony
                self.harmony_scores[worst_idx] = new_score
                replaced = True

            if verbose:
                print(
                    f"Iter {iteration:>4}/{self.iterations} | draw={draw:.4f} | "
                    f"zrodlo={source:>6} | new_fit=${new_score:>9.2f} | "
                    f"worst_fit=${worst_score:>9.2f} | "
                    f"{'PODMIANA' if replaced else 'BEZ ZMIANY'}"
                )

            if show_memory_every > 0 and iteration % show_memory_every == 0:
                self.print_harmony_memory(header=f"PAMIEC HARMONII PO ITERACJI {iteration}")

        best_score = max(self.harmony_scores)
        best_idx = self.harmony_scores.index(best_score)
        best_harmony = self.harmony_memory[best_idx]

        if verbose:
            print("\nKONIEC HARMONY SEARCH")
            print(f"Najlepszy fitness: ${best_score:.2f}")
            self.print_harmony_memory(header="KONCOWA PAMIEC HARMONII")

        return best_harmony, best_score

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
            "sector_limits": self.sector_limits,
        }

    def print_config(self):
        """Wyswietla konfiguracje."""
        print("=" * 70)
        print("KONFIGURACJA HARMONY SEARCH")
        print("=" * 70)
        print(f"Budzet inwestycyjny: ${self.budget:,.2f}")
        print(f"Liczba dostepnych akcji: {len(self.stocks)}")
        print("\nParametry algorytmu:")
        print(f"  HMS (Harmony Memory Size): {self.HMS}")
        print(f"  HMCR (Harmony Memory Considering Rate): {self.HMCR}")
        print(f"  PAR (Pitch Adjusting Rate): {self.PAR}")
        print(f"  Iteracje (n): {self.iterations}")
        print("\nLimity sektorowe:")
        for sector, limit in sorted(self.sector_limits.items()):
            print(f"  {sector}: max {limit} akcji")
        print("=" * 70)


if __name__ == "__main__":
    # Przyklad uzycia
    print("INICJALIZACJA PARAMETROW HARMONY SEARCH\n")

    # Utworzenie konfiguracji z domyslnymi parametrami
    config = HarmonySearchConfig(
        budget=100000,
        HMS=10,
        HMCR=0.7,
        PAR=0.15,
        iterations=100,
        seed=42,
    )

    # Wyswietl konfiguracje
    config.print_config()

    print("\n")

    # Zainicjalizuj pamiec harmonii
    harmony_memory, scores = config.initialize_harmony_memory()

    print(f"\nPamiec harmonii zostala zainicjalizowana z {len(harmony_memory)} harmonii.")
    print(f"Zakres wartosci: ${min(scores):.2f} - ${max(scores):.2f}")

    # Uruchom optymalizacje i pokaz koncowa pamiec
    config.run_harmony_search(show_memory_every=20, verbose=True)
