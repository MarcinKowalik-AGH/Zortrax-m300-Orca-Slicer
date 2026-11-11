# Dysze M300 Classic — Z-SUITE i profile Orca R4

## Ustalenie źródłowe

**Klasyczny Zortrax M300 ma potwierdzoną dyszę 0,4 mm w Z-SUITE.** Zestaw 0,3 / 0,4 / 0,6 mm ze specyfikacji M300 Plus nie jest zestawem profili dla M300 Classic. Nie wolno przenosić pomiędzy tymi drukarkami deklaracji producenta.

Źródła pierwotne sprawdzone 11.11.2026:

- [Specyfikacja M Series Classic](https://support.zortrax.com/m-series-specification/): M300, dysza 0,4 mm, warstwy 0,09–0,29 mm.
- [Odpowiedź Zortrax z 20.05.2020](https://forum.zortrax.com/t/zortrax-m300-print-with-0-6-mm-nozzle/9671): producent sprostował pierwszą odpowiedź i potwierdził brak opcji 0,6 mm dla M300 w Z-SUITE.
- [Odpowiedź Zortrax z 04.07.2023](https://forum.zortrax.com/t/there-is-no-possibility-to-choose-a-nozzle-except-0-4/12068): brak profili 0,6 mm dla klasycznego M300; Plus i Dual są innymi przypadkami.
- [Specyfikacja M300 Plus](https://support.zortrax.com/m300-plus-specification/): 0,3 / 0,4 / 0,6 mm. Dostępność wariantu Z-SUITE może też zależeć od materiału.
- [Aktualna strona pobierania](https://support.zortrax.com/downloads/software/): M300 Classic pozostaje przy Z-SUITE 2.32.0, nie przy najnowszej wersji 3.x.

Nie uruchomiono lokalnie Z-SUITE; powyższy wniosek opiera się na specyfikacji i jednoznacznych odpowiedziach producenta, nie na zgadywaniu elementów menu. Profil Klippera 0,20 mm również nie jest kopią OEM 0,19 mm.

## Co zawiera zestaw

Dla własnego portu Klippera przygotowano dodatkowe warianty 0,3 i 0,6 mm. Są oznaczone **Klipper custom**, a nie jako fabryczne profile Z-SUITE M300. Nie dołączono niepotwierdzonego profilu 0,8 mm. Używać wyłącznie dysz zgodnych mechanicznie z zamontowanym hotendem; dysza z M300 Plus nie staje się przez profil zamiennikiem dyszy Classic.

| Parametr | 0,3 mm — custom | 0,4 mm — baza R3 | 0,6 mm — custom |
|---|---:|---:|---:|
| Proces / pierwsza warstwa modelu | 0,20 / 0,20 mm | 0,20 / 0,20 mm | 0,20 / 0,20 mm |
| Szerokość domyślna, ściana zewnętrzna, top, pełne wypełnienie | 0,32 mm | 0,42 mm | 0,63 mm |
| Ściana wewnętrzna / rzadkie wypełnienie | 0,34 mm | 0,45 mm | 0,68 mm |
| Szerokość pierwszej warstwy | 0,38 mm | 0,50 mm | 0,75 mm |
| Szerokość podpór | 0,30 mm | 0,40 mm | 0,60 mm |
| Zakres wysokości w profilu drukarki | 0,09–0,24 mm | 0,09–0,29 mm | 0,15–0,45 mm |
| Dostarczone procesy | jeden: 0,20 mm | jeden: 0,20 mm | jeden: 0,20 mm |

Szerokości i zakresy 0,3/0,6 są **własnymi ustawieniami początkowymi**, nie wartościami odzyskanymi z Z-SUITE. 0,20 mm przy dyszy 0,3 mm spełnia założony zakres, lecz nie wykorzystuje możliwości jej cienkich warstw. Raft pozostaje włączony (2 warstwy); silnik slicera wyznacza jego własną geometrię zależną od dyszy.

Dotychczasowy pakiet 0,4 mm R3 pozostaje **identyczny bajt w bajt**: SHA-256 `3b60cd1ec9d324d5c2ed5a2aec7ced13560d13eff56734167bede1655e4333a4`. Nie zmieniono prędkości 20/25/40/50/30/20/120 mm/s ani przyspieszeń 300–700 mm/s². Nie podniesiono temperatur ani limitu przepływu tylko dlatego, że dysza jest większa. Nadal obowiązują punkty wyjścia 8 mm³/s dla większości materiałów, 4 dla FLEX/SUPPORT Plus i 2 dla SEMIFLEX — rzeczywistą wydajność trzeba zmierzyć.

## Materiały i Pressure Advance

Każda drukarka ma 18 rozpoznanych pozycji materiałowych. Nazwy 0,3 i 0,6 kończą się odpowiednio `@Zortrax M300 0.3` i `@Zortrax M300 0.6`. Tylko dopasowane filamenty są zgodne z danym wariantem. To daje **oddzielne miejsca kalibracji PA/flow/retrakcji dla każdej dyszy**, a nie wspólny parametr nadpisywany między dyszami.

Dla nowych średnic zachowano nominalne temperatury, mnożniki przepływu, retrakcje i Z-hop jako punkt wyjścia z R3. Nie skalowano retrakcji proporcjonalnie do średnicy. PA=0 oznacza brak zmierzonej korekcji; zerowanie przed purge oraz ustawianie wartości filamentu po START_PRINT pozostają aktywne. Adaptive PA pozostaje wyłączone. Zmierz PA po zmianie dyszy, zamiast kopiować wynik 0,4 na 0,6.

Z-PEEK pozostaje **niedopuszczonym wpisem katalogowym** i nie należy wysyłać jego G-code na tę M300. Programowy sukces slicingu innych materiałów nie potwierdza ich przydatności mechanicznej, termicznej ani jakościowej. W szczególności drobna dysza wymaga oceny materiałów z dodatkami pod kątem zatykania. Jedna głowica nadal nie umożliwia jednoczesnego drukowania modelu i odrębnego rozpuszczalnego supportu.

## Instalacja

Archiwum `M300_Orca_0p3_0p4_0p6_R4.zip` należy rozpakować. W Orca wybierz **File → Import → Import Configs** i zaimportuj potrzebne pliki `.orca_printer` — nie zewnętrzny ZIP. Można zaimportować wszystkie trzy.

Drukarki do wyboru:

- `Zortrax M300 0.3 nozzle - Klipper custom`
- `Zortrax M300 0.4 nozzle`
- `Zortrax M300 0.6 nozzle - Klipper custom`

Dla każdej wybierz proces 0,20 mm o zgodnej nazwie oraz materiał z właściwym sufiksem. Reimport zastępuje presety o tej samej nazwie, dlatego wcześniej wykonaj eksport własnych skalibrowanych filamentów.

## Klipper: sama zmiana profilu Orca nie wystarcza

Na postoju, po zamontowaniu odpowiedniej dyszy, popraw istniejącą pozycję w aktywnym pliku konfiguracyjnym ekstrudera. Nie dopisuj drugiej sekcji i nie zmieniaj niczego podczas druku:

```ini
[extruder]
nozzle_diameter: 0.6
```

To przykład dla dyszy 0,6; dla 0,3/0,4 wpisz odpowiednią wartość. Następnie wykonaj kontrolowany restart Klippera i sprawdź konfigurację. Wybranie drukarki w Orca **nie aktualizuje** tej pozycji na Orange Pi. Nie zmieniaj `filament_diameter: 1.75`, `rotation_distance`, PID ani limitów temperatur w ramach samej deklaracji średnicy.

W Klipperze domyślna granica przekroju ekstruzji jest wyliczana jako `4 * nozzle_diameter^2`: odpowiednio 0,36 / 0,64 / 1,44 mm². Pozostawione jawne `max_extrude_cross_section` może nadpisywać tę zależność; nie zwiększaj go w ciemno, aby ukryć niezgodność średnicy. [Dokumentacja Klippera](https://www.klipper3d.org/Config_Reference.html#extruder).

Po fizycznej wymianie dyszy sprawdź pozycję jej końcówki, homing kontaktowy i mesh. Nie zmieniono hostowych linii purge — ich zachowanie na nowej dyszy wymaga nadzorowanej próby. Zestaw nie instaluje ani nie flashuje drukarki; kod hosta i wszystkie zabezpieczenia pozostają w `Zortrax-m300-Klipper`.

## Walidacja

`tools/build_nozzle_variants.py --check` kontroluje odtwarzalność, schematy 144/334/123 i brak zmiany pakietu 0,4. `tests/audit_nozzles.py` wykonuje slicing w prawdziwym Orca 2.3.2 dla 3×18 wpisów, sprawdzając średnicę, szerokości, warstwę, temperatury, START/END/PAUSE, M83, retrakcje, Z-hop i PA. Dodatkowy test z PA=0,035 sprawdza przekazywanie parametru, nie stanowi kalibracji.

Dokładny wynik przebiegu jest w `evidence/NOZZLE_VALIDATION_R4.json`; generowane G-code nie są drukowane. Import GUI i fizyczna kwalifikacja pozostają **niewykonane**. Wykrywanie przekroczeń domyślnego przekroju ekstruzji analizuje G-code slicera, nie wykonywany na sprzęcie kod START_PRINT/purge. Nie deklaruje się zgodności nowych dysz z oryginalnym firmware Zortraxa.
