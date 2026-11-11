# Zortrax M300 — OrcaSlicer2.5.0 / R6

Natywne profile0.2/0.3/0.4/0.6. **19 materiałów,76 filamentów,80 procesów; bez sześciu Z-SUPPORT.** Wszystkie pozostałe materiały dostępne, także PEEK i PEI.

[Pobierz komplet](profiles/R6/M300_R6_KOMPLET.zip?raw=true) · [Natywny vendor](profiles/R6/Zortrax_M300_NATIVE_R6.zip?raw=true) · [Instrukcja](docs/R6_NATIVE_PL.md) · [Testy](evidence/R6_RUNTIME_VALIDATION.json).

[0.2 User](profiles/R6/Zortrax_M300_0p2_R6.orca_printer?raw=true) / [0.3 User](profiles/R6/Zortrax_M300_0p3_R6.orca_printer?raw=true) / [0.4 User](profiles/R6/Zortrax_M300_0p4_R6.orca_printer?raw=true) / [0.6 User](profiles/R6/Zortrax_M300_0p6_R6.orca_printer?raw=true). Nie instaluj natywnej i User wersji równocześnie.

Użytkownik potwierdził normalną pracę305°C/105°C. W profilach przywrócono rzeczywiste temperatury Z-SUITE:ABS275,ESD280,PCABS290. PEEK400/PEI360–370 są widoczne, ale ich wymagania przekraczają305°C: host odrzuci polecenie przed grzaniem. Nie udajemy druku PEEK przy305°C. Stół≤105°C.

Oficjalny silnik Orca2.5.0:76 kombinacji materiał/dysza+4 Standard+4 testy PA PASS. To kontrola programowa, nie84 fizyczne wydruki. PA=0 czeka na kalibrację. Firmware i host pozostają w osobnym repo Zortrax-m300-Klipper.

Starsze profile i surowe dane źródłowe zachowano wyłącznie do audytu; aktualny pakiet jest w profiles/R6, aktywny katalog w native.
