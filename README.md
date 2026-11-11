# Zortrax-m300-Orca-Slicer

## R5 — natywne profile Zortrax M300

**0,2 / 0,3 / 0,4 / 0,6 mm.** Nazwy drukarek bez dopisku custom. Filamenty: `Z-PLA Pro @Zortrax M300 0.2`, `Z-PLA Pro @Zortrax M300 0.4` itd.

**[Komplet R5](profiles/R5/M300_R5_KOMPLET.zip?raw=true)** · **[Natywny vendor Zortrax](profiles/R5/Zortrax_M300_NATIVE_R5.zip?raw=true)** · [Instrukcja](docs/R5_NATIVE_PL.md)

Alternatywny import User: [0.2](profiles/R5/Zortrax_M300_0p2_R5.orca_printer?raw=true) / [0.3](profiles/R5/Zortrax_M300_0p3_R5.orca_printer?raw=true) / [0.4](profiles/R5/Zortrax_M300_0p4_R5.orca_printer?raw=true) / [0.6](profiles/R5/Zortrax_M300_0p6_R5.orca_printer?raw=true). Nie instalować obu wersji pod tymi samymi nazwami.

Źródła: **Z-SUITE 2.32 — 152 rekordy klasycznego M300; beta4.0 — 214 rekordów**. Pierwszeństwo: dane klasyczne, beta, jawne przeliczenia i baza projektu. Natywny oznacza format Orca, a nie oficjalne zatwierdzenie integracji przez Zortrax. [Pochodzenie pól](evidence/R5_PROVENANCE.json) · [Źródła i sumy](sources/SOURCE_MANIFEST_R5.json).

4 drukarki,100 wpisów filamentów,84 procesy:4 Standard i80 wariantów materiałowych dla różnych prędkości. Dysza0.2:warstwa0.10; pozostałe:0.20. [Katalog](evidence/R5_CATALOG.json). PA=0 do pomiaru; M83 i makra Klippera zachowane; robocze temperatury265/105C maksymalnie. Korekty względem OEM są ujawnione.

**Wyłącznie katalog:** Z-PEEK,Z-PEI1010,Z-PEI9085,Z-SUPPORT High-Temp,Z-SUPPORT ATP130. Nie drukować ich na tej M300. Pozostałe wpisy także wymagają fizycznej kwalifikacji.

[Test rzeczywistego Orca2.3.2](evidence/R5_RUNTIME_VALIDATION.json):80 kombinacji materiał/dysza,4 Standard i4 próby PA; bez adaptera metadanych natywnych presetów. Nie wykonano fizycznego wydruku ani ręcznego importu GUI użytkownika.

Host,MCU,OLED,Fluidd i makra pozostają w [Zortrax-m300-Klipper](https://github.com/MarcinKowalik-AGH/Zortrax-m300-Klipper). Profile nie aktualizują hosta. Starsze R3/R4 zachowano jako historyczną bazę; aktualny pakiet jest w `profiles/R5`.
