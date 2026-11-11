# Zortrax M300 Classic — OrcaSlicer R7

**Jeden model M300 Classic, cztery warianty dyszy i procesy jakości jak w układzie Creality.** Ten projekt dotyczy wyłącznie slicera na komputerze. Nie instaluje ani nie aktualizuje Klippera, Orange Pi lub MCU.

## Aktualna instalacja — Git na Macu

Zapisz projekt, zamknij Orca przez Cmd+Q. W lokalnym Terminalu Maca:

```bash
git -C "$HOME/Zortrax-m300-Orca-Slicer" pull --ff-only origin main &&
python3 "$HOME/Zortrax-m300-Orca-Slicer/tools/install_classic_r7.py" --apply
```

Instalator **nie zapisuje `OrcaSlicer.conf`** i nie modyfikuje ustawień Creality. Dodaje/aktualizuje tylko M300 we własnym vendorze Zortrax, z kopią i możliwością odtworzenia. Odmawia uruchomienia na Linux/Orange Pi, w SSH, jako root lub przy działającym Orca.

W Orca wybierz **Printer → Select/Remove printers (system presets) → Zortrax → Zortrax M300 Classic**, zaznacz potrzebne dysze **0.2 / 0.3 / 0.4 / 0.6**, nie odznaczaj Creality. Następnie wybierz nowy model i sprawdź listę Process.

Dopiero po sprawdzeniu nowego M300 zamknij Orca i wycofaj cztery stare pakiety do archiwum:

```bash
python3 "$HOME/Zortrax-m300-Orca-Slicer/tools/install_classic_r7.py" --archive-offline --apply
```

Dotyczy tylko `offline_M300_Classic_0.3_v1`, `0.4_v1`, `0.6_v1`, `0.8_v1`, po weryfikacji zawartości. Nie kasuje konfiguracji całego Orca, innych modeli ani własnych samodzielnych presetów. Mieszane pakiety pozostają z ostrzeżeniem. Kopie są obok katalogu Orca pod `OrcaSlicer-M300-R7-...`.

**Nie używaj dawnych `repair_macos_r6.py --apply` ani instalatorów Orange Pi do instalacji tych profili.** Starsze R3–R6 są historyczną bazą liczbową, nie bieżącą procedurą instalacji.

## Process — przykład dla dyszy 0.4

| Proces | Różnica |
|---|---|
| 0.08mm SuperDetail | Drobne szczegóły |
| 0.12mm Detail | Wysoka szczegółowość |
| 0.16mm Optimal | Pośrednia jakość i czas |
| 0.20mm High Quality | 3 ściany, wolniejsza powierzchnia, grubsze zamknięcia |
| 0.20mm Standard | 2 ściany, 15% wypełnienia |
| 0.20mm Strength | 4 ściany, 40% gyroid |
| 0.24mm Draft | 10% wypełnienia, grubsza warstwa |
| 0.28mm SuperDraft | Zgrubny prototyp |

Pełne procesy są zależne od dyszy: szerokości ścieżek i dopuszczalne warstwy różnią się. 0.16 mm jest dostępne dla wszystkich czterech dysz; 0.20 mm dla 0.3/0.4/0.6, nie dla 0.2. Łącznie 30 procesów jakości. Nie kopiowano przyspieszeń i prędkości K2 Plus.

## Materiały

19 materiałów Zortrax z R6 + Generic PLA/PETG/ABS/ASA/TPU/PA/PC, dla każdej średnicy: 104 presety. Bez dedykowanych Z-SUPPORT. Nazwy np. `Z-PLA Pro @Zortrax M300 0.4` i `Generic PLA @Zortrax M300 0.4`. Inne marki dodawaj jako własną kopię odpowiedniego Generic, np. SUNLU PLA; dostosuj do szpuli i skalibruj. Generic to nieskalibrowane wartości startowe.

PA=0 nadal czeka na pomiar. Wysokotemperaturowe PEEK/PEI są widoczne, ale obecność profilu i poprawny slicing nie potwierdzają możliwości druku przy limitach M300. R7 nie zmienia temperatur materiałów Zortrax ani konfiguracji hosta.

## Źródła i walidacja

Rodzina jakości jest adaptacją projektu na bazie R6; nie oficjalnym zestawem profili Zortraxa. Dane Z-SUITE i starsze procesy materiałowe zachowano do audytu. Aktualne pliki: `native_r7/`.

Naprawiono błąd natywnego ładowania: pełny preset bez rodzica nie może deklarować `inherits: ""`. CLI przyjmowało taki zapis, loader GUI go odrzucał. R7 pomija pusty klucz, nie usuwa ustawień drukowania.

138/138 testów slicingu PASS, 14 testów instalatora PASS; rzeczywista aplikacja Orca 2.5.0 w Linux/Xvfb zarejestrowała wszystkie 30 procesów, 104 filamenty i cztery widoczne warianty M300 bez błędów własnego vendora. Nie wykonano testu na Macu użytkownika ani fizycznego wydruku.

[Instrukcja i tabela wszystkich dysz](docs/M300_CLASSIC_R7_PL.md) · [Katalog procesów](evidence/R7_PROCESS_CATALOG.json) · [Walidacja](evidence/R7_VALIDATION.json).

Kod hosta pozostaje w osobnym repozytorium `Zortrax-m300-Klipper`.
