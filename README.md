# Dividend Portfolio Optimizer (Capital Budgeting)

## Opis Projektu
Projekt to system optymalizacji portfela inwestycyjnego, będący praktyczną implementacją wielowymiarowego problemu plecakowego (Multi-dimensional 0-1 Knapsack Problem). Celem algorytmu jest wybór optymalnego zestawu pakietów akcji spółek dywidendowych z indeksu S&P 500, aby zmaksymalizować roczny dochód pasywny przy zachowaniu określonego profilu ryzyka.

## Logika Biznesowa
System symuluje realne warunki giełdowe – akcje kupowane są w tzw. paczkach (np. po 100 sztuk). 

* **Pojemność plecaka (Budżet):** Maksymalny kapitał początkowy przeznaczony na inwestycję (np. 100 000 USD).
* **Waga przedmiotu (Koszt):** Cena zakupu całego pakietu akcji danej spółki.
* **Wartość przedmiotu (Zysk):** Szacowana roczna wartość dywidendy wypłacona z tego pakietu.



## Ograniczenia i Dywersyfikacja
Klasyczny problem plecakowy został tutaj rozszerzony o dodatkowe reguły zarządzania ryzykiem:

* **Limit budżetu:** Suma kosztów wybranych pakietów nie może przekroczyć kapitału początkowego.
* **Limit sektorowy:** Aby uniknąć przeładowania portfela jedną branżą, wprowadzono twarde ograniczenie (np. portfel może zawierać maksymalnie 3 pakiety akcji ze spółek sektora "Technology" oraz maksymalnie 2 z sektora "Energy").
* **Zasada 0-1:** Dany pakiet akcji z listy można kupić w całości (1) lub odrzucić (0).

## Podejście Algorytmiczne
Z uwagi na dodatkowe ograniczenia kategoryjne (sektory), problem rozwiązano z wykorzystaniem **Integer Linear Programming (ILP)**. Funkcja celu maksymalizuje sumę dywidend, podczas gdy solver dba o to, by żadne z równań budżetowych i sektorowych nie zostało złamane.

## Struktura Danych Wejściowych
Algorytm przyjmuje zbiór danych historycznych (np. w formacie `.csv` pobranych z platformy Kaggle) o następującej strukturze:

| Ticker | Sector | Lot Cost (Weight) | Annual Lot Dividend (Value) |
| :--- | :--- | :--- | :--- |
| AAPL | Technology | $17,000 | $96.00 |
| KO | Consumer | $6,000 | $184.00 |
| CVX | Energy | $15,000 | $604.00 |
