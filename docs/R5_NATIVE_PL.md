# Zortrax M300 — natywny pakiet Orca R5

## Nazwy i zawartość

Producent w pakiecie systemowym: **Zortrax**. Model: **Zortrax M300**. Warianty drukarki: `Zortrax M300 0.2`, `Zortrax M300 0.3`, `Zortrax M300 0.4`, `Zortrax M300 0.6`. Nie ma dopisku custom.

Filamenty są nazwane konsekwentnie, np. `Z-PLA Pro @Zortrax M300 0.2`, `Z-PLA Pro @Zortrax M300 0.3`, `Z-PLA Pro @Zortrax M300 0.4`, `Z-PLA Pro @Zortrax M300 0.6`. Każdy filament jest kompatybilny wyłącznie z odpowiednią średnicą. Nazwa producenta jest nazwą rzeczywistej marki drukarki i materiałów. Natywny oznacza **format systemowego pakietu Orca**, nie twierdzenie, że Zortrax opublikował lub zatwierdził te profile Orca. Wartości wyliczone nie są podpisane jako pomiary producenta.

Pakiet zawiera 4 warianty drukarki, 25 rozpoznanych nazw materiałów dla każdej średnicy (100 wpisów) i 84 procesy: 4 domyślne Standard oraz po 20 procesów materiałowych. Dodatkowe procesy są potrzebne do zachowania odrębnych prędkości obrysów/wypełnienia dla materiałów — sam wybór filamentu nie zmienia tych pól procesu w Orca. Dla Z-PETG wybierz więc proces z Z-PETG i zgodną średnicą. Standard jest wspólnym punktem startowym opartym na Z-PLA Pro.

Dysza 0,2 mm ma proces **0,10 mm**. Pozostałe trzy mają proces **0,20 mm**. Nie ustawiono warstwy 0,20 mm dla dyszy 0,20 mm. Szerokości ścieżek: domyślna/zewnętrzna/top 1,10×d, wewnętrzna/infill 1,20×d, pierwsza warstwa 1,25×d, support 1,00×d. Są to jawne przeliczenia geometryczne; nie udajemy, że znaleziono fabryczny M300 0,2 mm.

## Faktycznie odczytane źródła

1. Z-SUITE 2.32.0, oryginalna biblioteka `Z-SUITE.dll`, SHA-256 `54a01c41318b1d30fc7822f6c974409ca8a9c90ec467b42e6c657131da4bf40a`. Odczytano **152 rekordy M300**, obejmujące materiał, średnicę, warstwę, jakość i rodzaj wypełnienia; 448 rekordów całej klasycznej części M200/M300/Inventure.
2. Załączony Z-SUITE BETA 4.0.0, SHA-256 ZIP `ad2c04816980b38fae4499f1ba54f7c2ccdbacd200b97d3dfd67d399c4d5aa26`; biblioteka SHA-256 `2b42e567aaee3c7370f8339aebafad0625d27726859231bf40ffaa93d0bdf0b2`. Odczytano 214 rekordów numerycznych z M200Plus, M300Plus, M300Dual, Inventure i Endureal. Dane tych modeli są nazwane zgodnie z rzeczywistym źródłem, a nie przedstawiane jako fabryczny M300 Classic.
3. Gdy nie ma odpowiedniej tabeli, zachowano oznaczoną bazę projektu R3 oraz zastosowano przeliczenie geometrii. Dla Z-PHA i Z-SUPPORT Plus nie odzyskano osobnej tabeli o dokładnie tej nazwie w obu analizowanych częściach konfiguracji; nie wymyślono jej pochodzenia.

Odczyt wykonuje ograniczony interpreter IL dla stałych konfiguracji i dekodera tablicy napisów. Nie uruchamia Z-SUITE ani instalatora na komputerze użytkownika. Repo nie zawiera DLL producenta, fontów ani grafik aplikacji. Zachowuje własny ekstraktor, surowe liczby, sumy plików i mapowanie pól.

Pierwszeństwo ma klasyczny M300. Przy braku materiału używane są nazwane tabele M200/Inventure z klasycznej wersji, potem tabele bety. Dla temperatur i retrakcji wybierana jest najbliższa dostępna warstwa. Ciągłe pola prędkości mogą być interpolowane między dwiema istniejącymi warstwami; poza zakresem zapisujemy „nearest”, a zmianę średnicy oznaczamy jako przeskalowanie, nie interpolację pomiarów. W klasycznych tabelach pole `SliceThickness` bywa inne niż etykieta interfejsu: np. etykieta 0,19 mm ma dla odczytanych rekordów efektywną wartość 0,20 mm. Ta różnica jest zachowana w raporcie.

## Co mapujemy, a czego nie kopiujemy bez przeliczenia

Temperatury, długości retrakcji, nadmiar powrotu, Z-hop, chłodzenie i prędkości pochodzą z wybranych tabel tam, gdzie istnieje jednoznaczne mapowanie. Prędkości źródłowe w mm/min są dzielone przez 60. Klasyczny wentylator 0..1 jest przeliczany na 0..100%. Różnica `R_Forward - R_Back` jest dodatkowym podaniem po retrakcji, a nie długością całej retrakcji.

Surowe pola `...Feed` nie są kopiowane jako `filament_flow_ratio`: opisują inny model dawkowania i ścieżek. Flow ratio i maksymalny przepływ pozostają oznaczonymi, nieskalibrowanymi wartościami bazowymi projektu. Podobnie przyspieszenia 300–700 mm/s², mechanizm raftu Orca, G-code startu/końca i PA należą do adaptacji Klippera, nie do odzyskanej tabeli firmware OEM.

Pełne mapowanie: `evidence/R5_PROVENANCE.json`. Surowe liczby: `sources/ZSUITE_classic.json` i `sources/ZSUITE_beta4.json`. Opis źródła zawiera model, materiał, oryginalną i docelową średnicę/warstwę oraz regułę przeliczenia. Wszystkie 144/334/123 pola bazowych profili zostały zachowane; natywny format dodaje pola `type`, `instantiation`, `setting_id`.

## Limity i kwalifikacja

Nie zmieniono firmware ani konfiguracji Orange Pi. Nadal M83, START_PRINT/END_PRINT/PAUSE, zerowanie PA przed purge i PA z filamentu po starcie. PA=0 jest neutralne, wymaga pomiaru dla każdej dyszy i materiału. Adaptive PA pozostaje wyłączone.

Roboczy limit nastawy dyszy w profilach niekatalogowych to 265°C, stół do 105°C, prędkość retrakcji do 45 mm/s zgodnie z dotychczasową konfiguracją hosta. Tam, gdzie tabela OEM wymaga więcej, raport pokazuje **obie liczby** i ostrzeżenie. Obniżenie temperatury nie dowodzi, że dany materiał można poprawnie wydrukować; wymaga osobnej kwalifikacji. Nie wprowadzono ogólnego podwyższenia temperatur „bo Micro Swiss”.

**Wyłącznie katalog, bez drukowania na tej M300:** Z-PEEK, Z-PEI 1010, Z-PEI 9085, Z-SUPPORT High-Temp i Z-SUPPORT ATP 130. Ich wymagania wykraczają poza konfigurację; sama maska `filament_printable=0` nie jest niezawodną blokadą slicingu. Nie wysyłać ich G-code na drukarkę. Pozostałe podpory nie umożliwiają równoległego druku drugim materiałem na jednej dyszy. Materiały z dodatkami i elastyczne wymagają szczególnej oceny przed użyciem dyszy 0,2 mm; obecność na liście nie jest potwierdzeniem zgodności fizycznej.

## Instalacja natywna — zalecana

Rozpakuj `Zortrax_M300_NATIVE_R5.zip`, zamknij Orca i uruchom `INSTALL_NATIVE.py`. Domyślnie skrypt pokazuje tylko plan. Na macOS:

```bash
python3 INSTALL_NATIVE.py --config-dir "$HOME/Library/Application Support/OrcaSlicer"
python3 INSTALL_NATIVE.py --config-dir "$HOME/Library/Application Support/OrcaSlicer" --apply
```

Jeżeli jest już systemowy vendor Zortrax, wyeksportuj własne skalibrowane profile, a następnie dodaj jawne `--replace-existing-vendor`. Skrypt robi kopię w `vendor-backups`, nie zmienia `Orca.conf`, presetów użytkownika ani Klippera. Kopiuje indeks Zortrax.json i katalog Zortrax do folderu `system` istniejącej konfiguracji Orca.

Po ponownym uruchomieniu Orca otwórz dodawanie/usuwanie drukarek i zaznacz **Zortrax → Zortrax M300 → 0.2 / 0.3 / 0.4 / 0.6**. Wybierz materiał i zgodny proces. Natywne presety są systemowe; własny pomiar PA zapisz jako własną kopię filamentu, aby kolejna aktualizacja nie nadpisała kalibracji.

## Alternatywa: zwykły import

Cztery pliki `Zortrax_M300_0p2_R5.orca_printer` itd. są alternatywą dla instalacji natywnej. Import: File → Import → Import Configs. Zachowują te same wartości i nazwy, ale są presetami User, nie rejestrują producenta w kreatorze. **Nie instaluj równocześnie obu wariantów pod tymi samymi nazwami.** Zachowaj eksport skalibrowanych starych filamentów przed migracją; wcześniejszy Z-PLA Pro bez średnicy jest teraz Z-PLA Pro ...0.4.

Po fizycznej zmianie dyszy jej średnica musi być także wpisana w istniejącym `[extruder] nozzle_diameter` Klippera; profile tego nie zmieniają. Sprawdź pozycję końcówki, homing, mesh i hostowe purge na nadzorowanej próbie. Nie podnoś limitu przekroju ekstruzji w celu ukrycia błędu średnicy.

## Walidacja

Raport `evidence/R5_RUNTIME_VALIDATION.json` rozróżnia kontrolę natywnego indeksu, schematu i rzeczywisty slicing w Orca 2.3.2. Wartości katalogowe nie są zaliczane jako dopuszczone do druku. Test programowy nie potwierdza kalibracji ani jakości wydruku. Nie deklarujemy fizycznego testu drukarki ani ręcznego importu GUI na komputerze użytkownika.
