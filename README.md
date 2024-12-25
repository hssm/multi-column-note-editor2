This Anki add-on lets you change the note editor to see your fields inside multiple columns. A new input box at the bottom of the window allows you to easily and quickly change how many columns you see. Each note type can have its own custom number of columns, and any field with a lot of content can be toggled to take up a full line again.


https://github.com/user-attachments/assets/a348d53f-061e-4f7c-bc50-bdf70a148395


[AnkiWeb Link](https://ankiweb.net/shared/info/1876579195)

Known issues:
- The tabbing order follows the original field order, not the visual order. `tabindex` does not work. Will need to capture the key and do it manually.
- Editing the note model to change the number or order of fields will scramble the column width settings. The add-on can only target field index, so if the index changes, too bad.
