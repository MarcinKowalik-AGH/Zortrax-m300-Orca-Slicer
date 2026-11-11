# Zortrax-m300-Orca-Slicer

## Profile średnic dysz R4

**M300 Classic w Z-SUITE: 0,4 mm.** Warianty 0,3 i 0,6 mm są własnymi rozszerzeniami dla Klippera, nie profilami OEM. Nie mylić z M300 Plus. Każdy wariant ma jeden proces 0,20 mm i osobne filamenty/PA.

| Dysza | Pakiet |
|---|---|
| 0,3 mm — Klipper custom | [Import](profiles/Zortrax_M300_Classic_N0p3_0p20_CUSTOM_R4.orca_printer?raw=true) |
| 0,4 mm — niezmieniona baza R3 | [Import](profiles/Zortrax_M300_Classic_0p20_MicroSwiss_R3.orca_printer?raw=true) |
| 0,6 mm — Klipper custom | [Import](profiles/Zortrax_M300_Classic_N0p6_0p20_CUSTOM_R4.orca_printer?raw=true) |

[Komplet ZIP](profiles/M300_Orca_0p3_0p4_0p6_R4.zip?raw=true) · [Źródła, parametry i instalacja](docs/NOZZLES_R4_PL.md) · [Testy wszystkich wariantów](evidence/NOZZLE_VALIDATION_R4.json)

**Po fizycznej zmianie dyszy trzeba również poprawić `nozzle_diameter` w Klipperze. Import Orca nie zmienia hosta.** Z-PEEK pozostaje katalogowy; PA=0 czeka na pomiar osobno dla każdej dyszy i materiału. Nowe profile nie podnoszą temperatur, prędkości, przyspieszeń ani przepływu. Test silnika: 51 kombinacji materiał/dysza PASS oraz 3 testy przekazywania PA; bez testu GUI i druku fizycznego.

---

Profile **OrcaSlicer dla Zortrax M300 Classic z Klipperem**. Osobne repozytorium slicera; bez firmware MCU, hosta, Fluidd i instalatorów drukarki.

## Pobranie i import

**[Profil R3 — dysza 0,4 mm, warstwa 0,20 mm](profiles/Zortrax_M300_Classic_0p20_MicroSwiss_R3.orca_printer?raw=true)**

OrcaSlicer: **File → Import → Import Configs**. Wybierz plik `.orca_printer`, następnie drukarkę `Zortrax M300 0.4 nozzle`, proces `0.20mm Standard @Zortrax M300 0.4 nozzle` i materiał z dopiskiem `@Zortrax M300`. Przy ponownym imporcie zastąp wcześniejsze presety o tych samych nazwach. Nie importuj archiwum audytowego jako konfiguracji.

Pakiet zawiera **1 drukarkę, 1 proces oraz 18 wpisów filamentów**. 17 profili przeszło programowy test generowania G-code w silniku OrcaSlicer 2.3.2. **Z-PEEK jest wpisem katalogowym, niedopuszczonym do druku**; sama flaga slicera nie blokuje niezawodnie generowania G-code. Wynik slicingu nie potwierdza przydatności każdego materiału na rzeczywistym M300. Nie wykonano testu GUI na komputerze użytkownika ani fizycznego wydruku.

## Podział projektów

| Tutaj: OrcaSlicer | [Zortrax-m300-Klipper](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper) |
|---|---|
| Presety drukarki, procesu i materiałów | Host, MCU, OLED i Fluidd |
| Wywołania START_PRINT / END_PRINT / PAUSE | Implementacje makr i procedur |
| Temperatury materiałowe, M83, nastawy PA | Egzekwowanie limitów grzania, homing, mesh |
| Testy importowanych ustawień i wygenerowanego G-code | Testy sterowania drukarką i instalatory |

**Import presetu nie aktualizuje Klippera.** Stół ma w profilach nastawy do 105°C. Egzekwowanie limitu 105°C po stronie drukarki wymaga odpowiedniego hosta R3; w repozytorium hosta pozostaje osobnym zadaniem. Nie zwiększono limitu hotendu. Micro Swiss oznacza przygotowanie do zestawu M2580-04, nie potwierdzoną kalibrację zamontowanego hotendu.

`M83` pozostaje włączone. Pressure Advance jest jawnie zerowane przed START_PRINT, a następnie ustawiane z filamentu. Dostarczone `PA=0` jest neutralnym ustawieniem **do czasu pomiaru**, nie wynikiem kalibracji. Adaptive PA jest wyłączone. Zachowano prędkości, przyspieszenia, flow ratio i retrakcje R3 bez zmian.

## Dokumentacja i źródła

- [Instrukcja oraz rozdział odpowiedzialności host/profil](docs/INSTALL_PL.md)
- [Micro Swiss, limit stołu i strojenie PA](docs/MICROSWISS_R3_PL.md)
- [Oryginalny wynik walidacji R3](evidence/VALIDATION_RESULTS_R3_SOURCE.json)
- [Oryginalne wyniki G-code R3](evidence/ORCA_RUNTIME_RESULTS_R3.json)
- [Manifest migracji i pochodzenie każdego pliku](MIGRATION.json)

`profiles/` zawiera plik do importu, `presets/` jego edytowalne pliki JSON, `tests/` niezależne testy slicera, `evidence/` raporty, a `archive/` oryginalny pakiet źródeł i starsze raporty. Aktywne profile nie są budowane z repozytorium Klippera.

## Weryfikacja i rozwój

```bash
python3 tools/validate_profiles.py
python3 tools/build_bundle.py --output /tmp/m300-test.orca_printer
# Z zainstalowanym OrcaSlicer 2.3.2:
python3 tests/audit_r3.py --orca /sciezka/do/AppRun --bundle profiles/Zortrax_M300_Classic_0p20_MicroSwiss_R3.orca_printer --out /tmp/m300-orca-audit
```

GitHub Actions wykonuje kontrolę struktury oraz slicing dwuwieżowego modelu na przypiętym binarium OrcaSlicer 2.3.2. Sprawdza start/koniec, temperatury, M83, retrakcję, Z-hop i przekazywanie PA. Nie wykonuje kompilacji ani instalacji Klippera. Metadane `type` i `from=system` są adapterem CLI wyłącznie w kopiach testowych; pakiet importowy pozostaje pakietem użytkownika.

Migracja z commita `1f58160e2d0e81c462648e57fa0ee69123313a4f` repozytorium M300 zachowuje profil R3 **bajt w bajt**, bez zmiany parametrów. Historia oryginalnych commitów pozostaje w repozytorium źródłowym; jej identyfikatory i sumy plików zapisano w manifeście. Licencję kodu zachowano z projektu źródłowego.
