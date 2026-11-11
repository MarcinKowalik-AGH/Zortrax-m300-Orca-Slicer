# Naprawa instalacji M300 w Orca na Macu

## Dwie niezależne instalacje

`m300-orange-pi/install-orange-pi.py` aktualizuje host Klippera na Orange Pi. Nie jest instalatorem profili Orca. Poprawnie zakończona aktualizacja hosta305/105 nie oznacza, że wgrano presety slicera do MCU. Nie cofaj działającego hosta tylko w celu poprawienia listy profili na Macu. W razie błędu drukarki zachowaj log i receipt aktualizacji; nie wykonuj reset --hard ani przypadkowego flashowania.

Poniższa procedura dotyczy WYŁĄCZNIE lokalnego OrcaSlicer2.5 na Macu. Nie wysyła G-code, nie łączy się z drukarką i nie modyfikuje Klippera.

## Dlaczego nadal widać offline_M300_Classic

To lokalne pakiety użytkownika, ładowane w Orca2.5 z `user/<konto>/_local/<bundle_id>`. Samo skopiowanie `system/Zortrax.json` nie usuwa tych pakietów. Natywne drukarki i filamenty mają również listy aktywacji w `OrcaSlicer.conf`: `models` i `filaments`. Poprzedni instalator kopiował pliki, pozostawiając aktywację użytkownikowi i nie porządkując starych pakietów.

Nowe narzędzie archiwizuje rozpoznane stare pakiety M300 oraz ich presety, wgrywa pełen natywny R6 i aktywuje cztery średnice z materiałami. Nie kasuje całego katalogu Orca, nie usuwa Creality ani Inventure. Profile współdzielone z innymi drukarkami, pakiety mieszane i subskrybowane nie są automatycznie usuwane; pojawia się ostrzeżenie. Subskrypcje należy wyłączyć w File > Preset Bundle. Stare własne kalibracje M300 pozostają w kopii i nie są automatycznie przenoszone do nowych presetów.

## Procedura

Zapisz projekt i zamknij Orca przez Cmd+Q. Otwórz lokalny Terminal na Macu. Jeżeli wiersz zaczyna się od `klipper@m300`, wpisz `exit` i wróć do terminala Maca. Nie używaj sudo.

Po pobraniu lub aktualizacji repo `Zortrax-m300-Orca-Slicer`:

```bash
python3 "$HOME/Zortrax-m300-Orca-Slicer/tools/repair_macos_r6.py"
```

Powyższe pokazuje plan bez zmian. Zastosowanie:

```bash
python3 "$HOME/Zortrax-m300-Orca-Slicer/tools/repair_macos_r6.py" --apply
```

Skrypt odmawia uruchomienia poza macOS, w SSH, jako root i przy działającym Orca. Wymaga istniejącego `~/Library/Application Support/OrcaSlicer/OrcaSlicer.conf`. Niestandardowy katalog należy wskazać przez `--config-dir` zgodnie z Help > Show Configuration Folder.

Zachowuje odczytaną średnicę aktualnego profilu M300, jeżeli jest to0.2/0.3/0.4/0.6; w przeciwnym razie wybiera0.4. Można jawnie podać `--nozzle 0.6`. To jest tylko wybór profilu slicera; nie deklaracja fizycznej wymiany dyszy ani zmiana konfiguracji hosta.

Po komunikacie GOTOWE uruchom Orca i nowy pusty projekt. Nie otwieraj starego3MF do sprawdzenia listy, ponieważ może wnieść własne zapisane ustawienia. W System presets powinny być `Zortrax M300 0.2`, `0.3`, `0.4`, `0.6`. Wybierz rzeczywiście zamontowaną średnicę oraz odpowiedni filament i proces. Pakiet R6 ma4 warianty drukarki,76 filamentów i80 procesów, bez dedykowanych Z-SUPPORT.

## Kopia i odwracalność

Przed pierwszą zmianą tworzona jest prywatna lokalna kopia `~/Library/Application Support/OrcaSlicer-M300-backup-<czas>`. Folder zawiera poprzednie zmieniane pliki oraz `RECEIPT.json`. Nie wysyłaj całej kopii publicznie — plik konfiguracji może zawierać dane konta.

Przywracanie przy zamkniętym Orca:

```bash
python3 "$HOME/Zortrax-m300-Orca-Slicer/tools/repair_macos_r6.py" --restore "/pełna/ścieżka/OrcaSlicer-M300-backup-..."
```

Przywracanie odmawia nadpisania plików zmienionych już po naprawie. W razie takiej odmowy nie kasuj konfiguracji ani kopii. Narzędzie zatrzymuje się także na nieznanym formacie lub dowiązaniu symbolicznym zamiast zgadywać, co usunąć.

## Walidacja i ograniczenia

18 testów w tymczasowym systemie plików PASS: cztery stare pakiety, aktywacja4/76/80, zachowanie Creality/Inventure, współdzielonych presetów i innych kont, kopie kalibracji, odrzucanie SSH/Linux, idempotencja, automatyczny rollback po błędzie oraz odtwarzanie kopii. Run43078435596, commit72e82fa78e8c229cbe70c6f97cb4c32589f453ca. Nie przeprowadzono instalacji na komputerze użytkownika ani testu jego GUI. Parametry drukowania w native/ nie zostały zmienione przez tę poprawkę.

Podstawa formatu: kod OrcaSlicer v2.5.0, `PresetBundle.cpp::load_user_presets`, `Preset.cpp::set_visible_from_appconfig`, `AppConfig.cpp::load/save` i `ConfigWizard.cpp::BundleMap::load`.
