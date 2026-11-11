# M300 Classic — jeden model, warianty dyszy i procesy jakości R7

## Układ w OrcaSlicer 2.5.0

W polu Printer: **Zortrax M300 Classic**. Pole Variant wybiera dyszę 0.2, 0.3, 0.4 lub 0.6. Wewnętrznie Orca przechowuje cztery presety maszyny przypisane do jednego `printer_model` — tak samo zorganizowano profil K2 Plus. Nie są to cztery osobne pakiety offline.

Proces nie jest samą wysokością warstwy. Obejmuje także szerokości ścieżek, prędkości, ściany, wypełnienie, podpory i raft. Ta sama wysokość 0,16 mm może mieć wariant dla kilku dysz; nie oznacza to kopiowania całego procesu między dyszami. Przykład: ścieżka zewnętrzna dla dyszy 0,3 ma 0,33 mm, dla 0,6 ma 0,66 mm. W R7 procesy są filtrowane po zgodnym wariancie drukarki.

## Lista dla dyszy 0,4 mm

| Proces | Warstwa | Zastosowanie / różnica |
|---|---:|---|
| 0.08mm SuperDetail | 0,08 mm | Drobne szczegóły; obniżone prędkości ścian zewnętrznych i góry |
| 0.12mm Detail | 0,12 mm | Szczegółowy wydruk |
| 0.16mm Optimal | 0,16 mm | Pośrednia jakość/czas |
| 0.20mm High Quality | 0,20 mm | 3 ściany; wolniejsza ściana zewnętrzna i góra; grubsze zamknięcia |
| 0.20mm Standard | 0,20 mm | 2 ściany; 15% wypełnienia |
| 0.20mm Strength | 0,20 mm | 4 ściany; 40% gyroid; grubsza góra/dół |
| 0.24mm Draft | 0,24 mm | Szkic; 10% wypełnienia |
| 0.28mm SuperDraft | 0,28 mm | Zgrubny prototyp |

Pełna nazwa zawiera `@Zortrax M300 Classic 0.4 nozzle`. Dla pozostałych dysz jest analogiczna, bez przypisywania procesu do marki filamentu.

| Dysza | Dostarczone wysokości | Liczba procesów |
|---|---|---:|
| 0,2 mm | 0,06; 0,08; 0,10; 0,12; 0,16 | 5 |
| 0,3 mm | 0,08; 0,12; 0,16; 0,20 (HQ/Standard/Strength); 0,24 | 7 |
| 0,4 mm | 0,08; 0,12; 0,16; 0,20 (HQ/Standard/Strength); 0,24; 0,28 | 8 |
| 0,6 mm | 0,12; 0,16; 0,20 (HQ/Standard/Strength); 0,24; 0,28; 0,32; 0,36; 0,42 | 10 |

0,16 mm to górny przyjęty zakres dla dyszy 0,2. Nie ma procesu 0,20 mm dla tej dyszy. Zakresy 20–80% średnicy są punktem wyjścia zgodnym z dokumentacją Orca, a nie gwarancją jakości każdego filamentu.

Nie kopiowano prędkości, przyspieszeń ani G-code z Creality. Baza prędkości jest z R6 M300 Standard; rodzina jakości i nowe wysokości są adaptacją projektu, nie dosłownymi fabrycznymi presetami Z-SUITE. R6 z procesami per materiał i dane źródłowe są zachowane do audytu. Wspólna lista jakości nie odtwarza jednocześnie wszystkich różnych tabel prędkości Z-SUITE dla każdego materiału.

Raft pozostał dwuwarstwowy. Przy cienkich warstwach skorygowano wysokość pierwszej warstwy i odstęp nad raftem: `min(0.2, 0.6*d, h)` oraz `min(0.15, h)`. Kopiowanie odstępu 0,15 mm do wszystkich cienkich profili powodowało w rzeczywistym Orca błędy pustych warstw. Łatwość odrywania raftu wymaga próby fizycznej.

## Poprawka ładowania natywnego

W bazie R6 pełne presety zawierały metadane `inherits: ""`. Rzeczywisty loader systemowy Orca 2.5 odrzuca pustą nazwę rodzica, mimo że CLI potrafi wykonać slicing z takim plikiem. W R7 usunięto wyłącznie ten pusty klucz z samodzielnych presetów. Nie zastąpiono nim żadnego parametru drukowania. Dlatego walidacja obejmuje teraz również uruchomienie aplikacji i odczyt vendora, a nie tylko generowanie G-code.

## Filamenty

Zachowano 19 materiałów Zortrax z R6 i dodano 7 Generic: PLA, PETG, ABS, ASA, TPU, PA i PC. Razem 26 dla każdej dyszy, 104 presety. Z-SUPPORT nie wraca. Temperatury, retrakcje i PA materiałów Zortrax nie zostały ponownie przeliczone w R7; zmieniono zgodność z nazwą wariantu. Generic to jawnie nieskalibrowane punkty wyjścia, nie zalecenia konkretnej marki.

Nazwy nadal np. `Z-PLA Pro @Zortrax M300 0.4` i `Generic PLA @Zortrax M300 0.4`. Przy dodawaniu filamentu w Orca wybierz brakujące pozycje z listy zarządzania filamentami. Domyślnie wskazane są PLA.

SUNLU lub inna marka: wybierz Generic odpowiadający polimerowi, zapisz własną kopię np. `SUNLU PLA @Zortrax M300 0.4`, zachowaj zgodność z drukarką i ustaw temperaturę według konkretnej szpuli. Skalibruj przepływ, PA i retrakcję. PA=0 oznacza nadal brak pomiaru.

PEEK/PEI pozostają widoczne zgodnie z poprzednim zamówieniem, ale ich zapisane wymagania przekraczają możliwości konfiguracji 305/105; ich slicing nie jest fizycznym zatwierdzeniem druku. R7 nie zmienia ograniczeń drukarki.

## Instalacja — tylko Mac, bez modyfikacji pliku OrcaSlicer.conf

Zapisz projekt i zamknij Orca przez Cmd+Q. W lokalnym Terminalu Maca, nie SSH:

```bash
git -C "$HOME/Zortrax-m300-Orca-Slicer" pull --ff-only origin main &&
python3 "$HOME/Zortrax-m300-Orca-Slicer/tools/install_classic_r7.py" --apply
```

Nowy instalator kopiuje wyłącznie pliki M300 w vendorze Zortrax i aktualizuje jego indeks, zachowując ewentualne inne modele Zortraxa. Nie zapisuje OrcaSlicer.conf, nie aktywuje modeli za użytkownika, nie nadpisuje ustawień Creality/połączeń/kalibracji. Jest lokalna kopia i odwracalne odtworzenie. Nie uruchamiaj starych instalatorów `repair_macos_r6.py --apply`.

Uruchom Orca. W menu Printer wybierz **Select/Remove printers (system presets)**, zaznacz **Zortrax → Zortrax M300 Classic** i potrzebne średnice. Nie odznaczaj Creality. Wybierz M300 i właściwą dyszę; sprawdź listę Process. To sam Orca zapisuje aktywację własnym mechanizmem.

## Dopiero po potwierdzeniu M300 — usunięcie starych offline

Zamknij ponownie Orca. W Terminalu Maca:

```bash
python3 "$HOME/Zortrax-m300-Orca-Slicer/tools/install_classic_r7.py" --archive-offline --apply
```

Narzędzie archiwizuje wyłącznie rozpoznane lokalne pakiety `offline_M300_Classic_0.3_v1`, `0.4_v1`, `0.6_v1`, `0.8_v1`. Sprawdza, czy M300 Classic jest już włączony przez Orca. Pakiet mieszany z inną drukarką jest pozostawiany z ostrzeżeniem. Nie zmienia subskrypcji ani samodzielnych własnych presetów. Usunięcie oznacza wycofanie z aktywnego katalogu i zachowanie kopii, a nie nieodwracalną utratę.

Kopie: obok katalogu Orca, `OrcaSlicer-M300-R7-<czas>`. Przy zamkniętym programie można użyć `--restore /pełna/ścieżka/do/kopii`; odtworzenie nie nadpisze później zmienionych plików. Nie przesyłaj publicznie całej konfiguracji zawierającej dane konta.

## Walidacja i źródła

Run 43093602565: 138/138 prób slicingu PASS, 14 testów instalatora PASS. Faktycznie uruchomiona aplikacja OrcaSlicer 2.5.0 w Linux/Xvfb zarejestrowała 30 procesów, 104 filamenty i cztery widoczne warianty maszyny; wybrała natywny `Zortrax M300 Classic 0.4 nozzle`. Brak błędów natywnego vendora. Nie należy mylić tego z testem GUI na Macu użytkownika.

Dokładny wynik zapisany jest w `evidence/R7_VALIDATION.json`; zestawienie procesów w `evidence/R7_PROCESS_CATALOG.json`. Nie wykonywano instalacji na Macu użytkownika ani fizycznego wydruku; Orange Pi, Klipper i repo hosta pozostają niezmienione.

Źródła: oficjalny OrcaSlicer v2.5.0, `resources/profiles/Creality/machine/Creality K2 Plus.json`, proces `0.20mm Standard @Creality K2 Plus 0.4 nozzle.json`, wiki `quality_settings_layer_height`, mechanizm natywnego ładowania `PresetBundle.cpp` i `ConfigWizard.cpp`. Dane materiałowe M300: poprzedni pakiet R6 i zachowane źródła Z-SUITE.
