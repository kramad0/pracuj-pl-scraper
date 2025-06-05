from collections import Counter
import ast # Do bezpiecznej ewaluacji stringów jako list
import re # Do czyszczenia danych o wynagrodzeniu

CSV_FILE = "csv_js.csv"

IT_SPECIALIZATIONS = 'it_specializations' # np. ['Python', 'SQL']
TECHNOLOGIES_EXPECTED = 'technologies_expected' # np. ['AWS', 'Docker']
TECHNOLOGIES_OPTIONAL = 'technologies_optional' # np. "Wymaganie 1\nWymaganie 2"
BENEFITS = 'benefit_titles' # np. ['Opieka medyczna', 'Karta sportowa']
RESPONSIBILITES = 'responsibilities_section'
REQUIREMENTS = 'requirements_section'

TOP_N = 10 # Ile najczęstszych elementów wyświetlić

# Usuwa białe znaki i zmienia wszystko na małe litery

def wyczysc_i_znormalizuj_liste(lista_stringow):
    if isinstance(lista_stringow, list):
        return [str(s).strip().lower() for s in lista_stringow if str(s).strip()]
    return []

# Przetwarza kolumnę, gdzie każda komórka to string reprezentujący listę (np. "['Python', 'SQL']"). Zlicza wystąpienia poszczególnych elementów.

def zlicz_elementy_z_list_w_kolumnie(df, nazwa_kolumny, top_n=TOP_N):
    wszystkie_elementy = []
    stop_words = []
    
    for _, wiersz in df.iterrows():
        elementy_str = wiersz[nazwa_kolumny]
        if pd.notna(elementy_str) and isinstance(elementy_str, str) and elementy_str.startswith('[') and elementy_str.endswith(']'):
            try:
                # Bezpieczna konwersja stringa "[...]" na listę Pythona
                lista_elementow = ast.literal_eval(elementy_str)
                oczyszczone_elementy = [el.strip().lower() 
                                    for el in lista_elementow 
                                    if el.strip() and el.strip().lower() not in stop_words]
                wszystkie_elementy.extend(wyczysc_i_znormalizuj_liste(oczyszczone_elementy))
            except (ValueError, SyntaxError):
                print(f"Ostrzeżenie: Nie udało się sparsować jako listy: {elementy_str} w kolumnie {nazwa_kolumny}")
        elif pd.notna(elementy_str) and isinstance(elementy_str, list): # Jeśli już jest listą
             wszystkie_elementy.extend(wyczysc_i_znormalizuj_liste(elementy_str))

    licznik = Counter(wszystkie_elementy)
    return licznik.most_common(top_n)

# Przetwarza kolumnę, gdzie każda komórka to string z elementami oddzielonymi separatorem. Zlicza wystąpienia poszczególnych elementów.

def zlicz_elementy_z_tekstu_w_kolumnie(df, nazwa_kolumny, separator='\n', top_n=TOP_N):
    wszystkie_elementy = []
    stop_words = ['nasze wymagania','mile widziane','our requirements','optional','wymagania pracodawcy']

    for _, wiersz in df.iterrows():
        tekst_elementow = wiersz[nazwa_kolumny]
        if pd.notna(tekst_elementow) and isinstance(tekst_elementow, str):
            lista_elementow = tekst_elementow.split(separator)
            # Usuwamy puste stringi po splicie, normalizujemy i porównujemy ze stop_words
            oczyszczone_elementy = [el.strip().lower() 
                                    for el in lista_elementow 
                                    if el.strip() and el.strip().lower() not in stop_words]
            wszystkie_elementy.extend(oczyszczone_elementy)

    licznik = Counter(wszystkie_elementy)
    return licznik.most_common(top_n)

# Funkcja, która prezentuje dla nazwa_kolumny w zależności od zdefiniowanej dla niej w SCRAPE_CONFIG metody

def analizuj_czestosc(metoda, df, nazwa_kolumny, top_n=TOP_N):
    print(f"\n Najczęściej występujące {nazwa_kolumny}: (TOP {top_n}):")
    if(metoda =='lista'):
        wyswietlane = zlicz_elementy_z_list_w_kolumnie(df, nazwa_kolumny, top_n)
        if wyswietlane:
            for co, ile in wyswietlane:
                print(f"- {co}: {ile} razy")
        else:
            print("Brak danych lub nie udało się przetworzyć.")
    elif(metoda =='tekst'):
        wyswietlane = zlicz_elementy_z_tekstu_w_kolumnie(df, nazwa_kolumny,'\n', top_n)
        if wyswietlane:
            for co, ile in wyswietlane:
                print(f"- {co}: {ile} razy")
        else:
            print("Brak danych lub nie udało się przetworzyć.")
    else:
        print("Niepoprawna metoda")

def main():
        try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {CSV_FILE}. Upewnij się, że plik istnieje i ścieżka jest poprawna.")
    except Exception as e:
        print(f"Błąd podczas wczytywania pliku CSV: {e}")
    
    print(f"Analiza pliku: {CSV_FILE}")
    print("--------------------------------------------------")
    
    analizuj_czestosc("lista", df, TECHNOLOGIES_EXPECTED)
    analizuj_czestosc("lista", df, TECHNOLOGIES_OPTIONAL)
    analizuj_czestosc("tekst", df, REQUIREMENTS)
    analizuj_czestosc("lista", df, BENEFITS)
    analizuj_czestosc("lista", df, IT_SPECIALIZATIONS)

if__name__ = "__main__":
    main()