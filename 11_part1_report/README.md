# 11. Part 1 report

`StrucIQ_Project_Part1_Report.docx` and `StrucIQ_Project_Part1_Report.pdf`: the Part 1 project report (November 2026).

## Building the report

The report is generated from `source/`.

| File | Purpose |
|---|---|
| `build_report.js` | Writes the Word file (Node.js with the `docx` package, version 9.8) |
| `figs.py` | Draws Figures 1 to 7 into `figs/` |
| `figs_ds.py` | Draws Figures A-1 and A-2 from the dataset tables (set `STRUCIQ_TABLES` to the folder `06_design_space_population/tables` of the Zenodo dataset) |
| `pagemap.py` | Reads page numbers from the PDF and writes `pages.json`, used for the contents page and the lists of figures and tables |
| `figs/` | Figures and title-page images at print resolution |

```
cd source
npm install docx@9.8.1
python3 figs.py
STRUCIQ_TABLES=/path/to/06_design_space_population/tables python3 figs_ds.py
node build_report.js
soffice --headless --convert-to pdf StrucIQ_Project_Part1_Report.docx
python3 pagemap.py && node build_report.js   # second pass fills the page numbers
```

The text is set in Times New Roman, 12 point, 1.5 line spacing, justified; headings 14 point.
