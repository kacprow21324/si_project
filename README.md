Autor: Kacper Woszczyło 21324

System wspomagania decyzji inwestycyjnych, który rozwiązuje problem optymalizacji portfela dywidendowego przy użyciu algorytmów kombinatorycznych. Aplikacja traktuje budowanie portfela akcyjnego jako rozszerzoną wersję 0-1 Knapsack Problem (Problemu Plecakowego), gdzie celem jest maksymalizacja pasywnego dochodu z dywidend przy zachowaniu ścisłych ograniczeń budżetowych i reguł zarządzania ryzykiem.

System operuje na rzeczywistych danych historycznych spółek z indeksu S&P 500 (np. pobranych z platformy Kaggle).
Logika Biznesowa i Ograniczenia

W przeciwieństwie do teoretycznych modeli finansowych zakładających możliwość kupna ułamków akcji, ten projekt symuluje realne środowisko brokerskie, w którym akcje kupuje się w tzw. paczkach (lotach), np. po 100 sztuk.

    Pojemność "Plecaka" (Budżet): Sztywny limit kapitału początkowego (np. 100 000 PLN ).

    Waga Przedmiotu (Koszt Inwestycji): Cena zakupu pełnej paczki akcji danej spółki.

    Wartość Przedmiotu (Zysk): Szacowana roczna wartość wypłaconej dywidendy z danej paczki akcji.

Ograniczenia Dywersyfikacyjne (Hard Constraints)

Aby zapobiec wygenerowaniu portfela o zbyt wysokim ryzyku (np. złożonego w 100% z jednej branży), wprowadzono dodatkowe ograniczenia kategoryjne. System nie pozwoli na zakup więcej niż określonej liczby paczek z jednego sektora (np. maksymalnie 3 pakiety akcji z sektora technologicznego).
