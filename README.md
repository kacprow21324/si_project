# Dividend Portfolio Optimizer

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![CSV](https://img.shields.io/badge/Data-CSV-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Autor:** Kacper Woszczyło 21324

## Opis Projektu

System optymalizacji portfela inwestycyjnego wykorzystujący algorytm do rozwiązania wielowymiarowego problemu plecakowego (Multi-dimensional 0-1 Knapsack Problem). Celem jest maksymalizacja rocznego dochodu z dywidend przy zachowaniu ograniczeń budżetowych i dywersyfikacji sektorowej.

## Logika Biznesowa

System symuluje realne warunki inwestycyjne na giełdzie:

* **Budżet (Pojemność plecaka):** Maksymalny kapitał początkowy (np. $100,000)
* **Koszt (Waga przedmiotu):** Cena zakupu pakietu akcji (lot)
* **Dywidenda (Wartość przedmiotu):** Szacowana roczna dywidenda z pakietu
* **Zasada 0-1:** Pakiet można kupić w całości (1) lub odrzucić (0)

## Ograniczenia i Dywersyfikacja

* **Limit budżetu:** Suma kosztów ≤ kapitał początkowy
* **Limity sektorowe:** Maksymalna liczba pakietów na sektor (np. Technology: 3, Energy: 2)
* **Dywersyfikacja:** Automatyczna kontrola ryzyka przez ograniczenia sektorowe

## Struktura Projektu

```
si_project/
├── database.py           # Ładowanie danych z CSV
├── config.py            # Inicjalizacja parametrów (HMS, HMCR, PAR, n)
├── random_solution.py   # Generator losowych rozwiązań
├── harmony_search.py    # Implementacja algorytmu Harmony Search
├── gui_app.py          # Aplikacja desktopowa (PyQt5)
├── stock_data.csv      # Baza danych akcji (10000 rekordów)
└── generate_data.py    # Generator danych testowych
```

## Dane Wejściowe

Format danych CSV (10,000 akcji):

| Ticker | Sector | Share_Price | Lot_Size | Lot_Cost | Annual_Lot_Dividend | Dividend_Yield |
|--------|--------|-------------|----------|----------|---------------------|----------------|
| DDRA | Consumer Cyclical | 70.78 | 100 | 7,078 | 150.85 | 2.13% |
| CCS | Consumer Defensive | 239.59 | 100 | 23,959 | 424.94 | 1.77% |
| EAZO | Financials | 53.05 | 100 | 5,305 | 176.38 | 3.32% |
