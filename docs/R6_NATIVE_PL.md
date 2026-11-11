# Zortrax M300 — OrcaSlicer 2.5.0, R6

## Zawartość
Natywny vendor Zortrax, model Zortrax M300, dysze0.2/0.3/0.4/0.6. Nazwy np. `Z-PLA Pro @Zortrax M300 0.4`. 19 materiałów×4=76 filamentów;4 Standard+76 procesów materiałowych=80 procesów. Dysza0.2:warstwa0.10;pozostałe0.20. Integracja społecznościowa na podstawie Z-SUITE, nie oficjalne wydanie Zortraxa.

Usunięto aktywne profile Z-SUPPORT, Z-SUPPORT ATP, Z-SUPPORT ATP130, Z-SUPPORT High-Temp, Z-SUPPORT Plus i Z-SUPPORT Premium. Wszystkie pozostałe materiały są widoczne i wybieralne, w tym Z-HIPS, Z-PEEK, Z-PEI1010 i Z-PEI9085. Każdy ma maskę ekstrudera1 oraz filament_is_support=0. Podpory geometryczne drukowane z tego samego materiału co model nadal są dostępne.

## Temperatury i test
Użytkownik potwierdził11.11.2026 nastawy305°C ekstrudera/105°C stołu i normalną pracę drukarki. Status: TEST ZGŁOSZONY PRZEZ UŻYTKOWNIKA, nie pomiar wykonany przez autora pakietu i nie test wszystkich materiałów. Host M300-305-105-R1 egzekwuje nastawy305/105, z progami awaryjnymi czujnika310/120. Niezależne limity ADC MCU nie są zmienione.

Usunięto poprzednie przycięcie profili do265°C. Przywrócono temperatury źródłowe, m.in. ABS/ABS2=275°C, ESD=280°C, PCABS=290°C. Pozostałe nastawy nie otrzymują arbitralnego dodatku za nazwę Micro Swiss.

DOSTĘPNY PROFIL NIE OZNACZA ZGODNOŚCI MATERIAŁU Z305°C. Odczytane wymagania: Z-PEEK400°C, Z-PEI1010=370°C, Z-PEI9085=360°C. Profile są widoczne i wybieralne oraz mają rzeczywiste temperatury. Host305°C odrzuci taki START_PRINT przed grzaniem i ruchem. Nie zastąpiono400°C fikcyjnymi305°C. Wymagania stołu/komory również wykraczają poza tę konfigurację. Sloty płyt w profilu mają limit105°C, ale to nie kwalifikuje tych materiałów; źródłowe temperatury są w R6_CATALOG.json i raporcie pochodzenia.

## Ekstruzja i jakość
M83, START_PRINT/END_PRINT/PAUSE zachowane. Prędkości, przyspieszenia, homing180°C, flow ratio, retrakcje i Z-hop nie są zmienione przez migrację. PA zerowane przed purge, następnie podawane z filamentu; PA=0 wymaga fizycznej kalibracji. Próba0.035 testuje przekazanie parametru, nie jest nastawą domyślną. Adaptive PA wyłączone.

## Instalacja
Rozpakuj `Zortrax_M300_NATIVE_R6.zip`, zamknij Orca2.5.0. Plan: `python3 INSTALL_NATIVE.py`. Instalacja: `python3 INSTALL_NATIVE.py --apply --replace-existing-vendor`. Skrypt tworzy kopię poprzedniego vendora i nie zmienia drukarki. Na Macu domyślny katalog to `~/Library/Application Support/OrcaSlicer`. Po starcie wybierz Zortrax → Zortrax M300 → średnica.

Alternatywa: import odpowiedniego `Zortrax_M300_0pX_R6.orca_printer` jako User. Nie stosuj obu metod równocześnie pod identycznymi nazwami. Stare ręcznie importowane presety Z-SUPPORT pozostaną na komputerze do ręcznego usunięcia; samo zaimportowanie nowego pliku nie kasuje obcych presetów. Zastąpienie natywnego vendora usuwa jego stare materiały podporowe. Wyeksportuj własne skalibrowane filamenty przed migracją.

Po fizycznej zmianie dyszy ustaw zgodne `nozzle_diameter` w istniejącej konfiguracji Klippera na postoju. Nie dodawaj drugiej sekcji ekstrudera i nie zmieniaj rotation_distance z powodu samej średnicy.

## Walidacja
Raport R6_RUNTIME_VALIDATION.json dotyczy rzeczywistego silnika oficjalnego Orca2.5.0, indeksu vendora i wygenerowanego G-code. Nawet poprawne wygenerowanie G-code dla PEEK nie oznacza fizycznej możliwości jego wydrukowania. Testy hosta obejmują odmowę temperatur ponad305/105 oraz start/pauzę/wznowienie/koniec z modelowaną temperaturą. Nie wykonano fizycznych wydruków76 kombinacji materiał–dysza ani instalacji na Orange Pi.
