from harmony_search import HarmonySearchConfig

__all__ = ["HarmonySearchConfig"]


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
