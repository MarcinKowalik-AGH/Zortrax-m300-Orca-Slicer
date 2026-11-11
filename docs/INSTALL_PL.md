# Instalacja profilu — M300 Classic

Importuj plik z katalogu `profiles`, nie cały ZIP źródeł repozytorium. W OrcaSlicer wybierz **File → Import → Import Configs**. Zastąp poprzednie presety o tych samych nazwach, wybierz `Zortrax M300 0.4 nozzle`, jeden proces `0.20mm Standard` i odpowiedni filament `@Zortrax M300`.

Nie zmieniono parametrów druku podczas migracji. Dysza: 0,4 mm; filament: 1,75 mm; warstwa: 0,20 mm; E względne. Do druku wymagane są istniejące makra START_PRINT, END_PRINT oraz PAUSE w hoście M300. Pliki profili nie zawierają firmware ani instalatora hosta.

## Sterowanie drukarką jest w innym repozytorium

[Zortrax-m300-Klipper](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper) zawiera procedury, konfigurację hosta i niezależne zabezpieczenia termiczne. Zmiany hosta R3 są opisane w [PR #14](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper/pull/14). Sam import nie instaluje limitu stołu 105°C na drukarce. Przed użyciem sprawdź stan własnej instalacji i wersję hosta; nie uruchamiaj aktualizacji podczas druku.

PA=0 pozostaje neutralne do kalibracji danego filamentu. Nie wprowadzono offsetu temperatury dla Micro Swiss. Z-PEEK jest katalogiem, nie zatwierdzonym materiałem. Z-SUPPORT nie umożliwia równoczesnego druku drugiego materiału podporowego na jednogłowicowej M300.

Sprawdzono generowanie G-code, nie fizyczną jakość/bezpieczeństwo zmontowanej maszyny. Nadzorowane testy temperatur, purge, homingu, meshu, ekstruzji i przyczepności pozostają po stronie urządzenia. `MESH=AUTO` ładuje zapisaną siatkę; nie wykonuje nowego pomiaru.
