const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, HeadingLevel, PageBreak, Footer, PageNumber, NumberFormat, BorderStyle, PageBorderDisplay, PageBorderOffsetFrom, PageBorderZOrder,
  ShadingType, TabStopType, LevelFormat, VerticalAlign, SectionType,
} = require("docx");

const PAGES = fs.existsSync("pages.json") ? JSON.parse(fs.readFileSync("pages.json")) : {};
const FONT = "Times New Roman";
const W = 9026; // A4 text width in DXA with 1-inch margins
const TITLE = "Digital Twin for Live Condition Monitoring and Retrofit Decision Support of Reinforced Concrete Members";

// inline **bold** and *italic*
function plainRuns(t, base) {    // plain text with f_{open} style subscripts
  const out = []; const re = /([_^])\{([^}]*)\}/g; let last = 0, m;
  while ((m = re.exec(t))) { if (m.index > last) out.push(new TextRun({ text: t.slice(last, m.index), ...base })); out.push(new TextRun({ text: m[2], ...(m[1] === "_" ? { subScript: true } : { superScript: true }), ...base })); last = m.index + m[0].length; }
  if (last < t.length) out.push(new TextRun({ text: t.slice(last), ...base })); return out;
}
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(...plainRuns(text.slice(last, m.index), base));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), italics: true, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(...plainRuns(text.slice(last), base));
  return out;
}

const SMALL = new Set(["et","al","a","an","the","and","or","but","nor","for","of","on","in","at","to","by","as","per","via","vs"]);
function titleCase(t) {
  let first = true;
  return t.split(" ").map(w => {
    const m = w.match(/^([^A-Za-z0-9]*)(.*)$/); const pre = m[1], core = m[2];
    let out = core;
    if (core && !/[A-Z0-9]/.test(core)) {
      out = core.split("-").map((p, i) => (!first && i === 0 && SMALL.has(p.replace(/[^a-z]/g, "")) && /^[a-z]+[,;:.)]*$/.test(p)) ? p : p.charAt(0).toUpperCase() + p.slice(1)).join("-");
    }
    if (core) first = false;
    return pre + out;
  }).join(" ");
}
function capText(text) {   // "**Table 1.** title; note" -> title case title, note as its own sentence
  const m = text.match(/^(\*\*[^*]+\*\*\s*)(.*)$/); if (!m) return text;
  let body = m[2]; let note = "";
  const k = body.indexOf("; "); if (k >= 0) { note = body.slice(k + 2); body = body.slice(0, k); }
  body = body.replace(/\.$/, "");
  let out = m[1] + titleCase(body) + (note ? ". " + note.charAt(0).toUpperCase() + note.slice(1) : "");
  if (note && !/\.$/.test(out)) out += ".";
  return out;
}
const P = (text, o = {}) => new Paragraph({
  children: runs(text, o.run || {}), alignment: o.align || AlignmentType.JUSTIFIED,
  spacing: { after: o.after ?? 100, before: o.before ?? 0, line: o.line ?? 360 },
  indent: o.indent, keepNext: o.keepNext,
});
const C = (text, o = {}) => P(text, { align: AlignmentType.CENTER, ...o });
const H1 = (text, key) => new Paragraph({
  heading: HeadingLevel.HEADING_1, children: [new TextRun({ text, bold: true, size: 28, font: FONT })],
  alignment: AlignmentType.CENTER, pageBreakBefore: !/CHAPTER 1:/.test(text) && false,
  spacing: { before: 320, after: 160, line: 300 }, keepNext: true,
});
const H2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2, children: [new TextRun({ text, bold: true, size: 28, font: FONT })],
  spacing: { before: 200, after: 80, line: 300 }, keepNext: true,
});
const H1pb = (text) => new Paragraph({ pageBreakBefore: true, heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, spacing: { before: 0, after: 200 }, children: [new TextRun({ text, bold: true, size: 28, font: FONT })] });
const pb = () => new Paragraph({ children: [new PageBreak()] });
const NUM = (text, ref = "nums", level = 0) => new Paragraph({
  numbering: { reference: ref, level }, children: runs(text), alignment: AlignmentType.JUSTIFIED,
  spacing: { after: 40, line: 360 },
});
const caption = (text) => new Paragraph({
  children: runs(capText(text), { size: 24 }), alignment: AlignmentType.CENTER,
  spacing: { before: 40, after: 160, line: 276 },
});
const tcaption = (text) => new Paragraph({
  children: runs(capText(text), { size: 24 }), alignment: AlignmentType.CENTER,
  spacing: { before: 120, after: 60, line: 276 }, keepNext: true,
});

const bd = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const borders = { top: bd, bottom: bd, left: bd, right: bd };
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: none, bottom: none, left: none, right: none };

function tableBook(headers, rows, widths, o = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const leftCol = widths.map((_, i) => rows.some(r => String(r[i]).length > 32));
  const rule = { style: BorderStyle.SINGLE, size: 8, color: "000000" };
  const thin = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
  const cell = (t, w, head, first, last, ci) => new TableCell({
    borders: { left: none, right: none, top: head ? rule : none, bottom: head ? thin : (last ? rule : none) },
    width: { size: w, type: WidthType.DXA },
    margins: { top: 60, bottom: 60, left: 80, right: 80 }, verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      children: runs(String(t), { size: o.size || 22, bold: head || first }),
      alignment: (!head && leftCol[ci]) ? AlignmentType.LEFT : AlignmentType.CENTER, spacing: { after: 0, line: 240 },
    })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths, alignment: AlignmentType.CENTER,
    borders: { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none },
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], true, false, false, i)) }),
      ...rows.map((r, j) => new TableRow({ cantSplit: true, children: r.map((t, i) => cell(t, widths[i], false, i === 0, j === rows.length - 1, i)) })),
    ],
  });
}

function table(headers, rows, widths, o = {}) { return tableBook(headers, rows, widths, o); }
function tableGridOld(headers, rows, widths, o = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, w, head) => new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: head ? { fill: "E7E6E6", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 30, bottom: 30, left: 80, right: 80 }, verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      children: runs(String(t), { size: o.size || 20, bold: head }),
      alignment: o.alignAll || AlignmentType.LEFT, spacing: { after: 0, line: 240 },
    })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths, alignment: AlignmentType.CENTER,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], true)) }),
      ...rows.map(r => new TableRow({ cantSplit: true, children: r.map((t, i) => cell(t, widths[i], false)) })),
    ],
  });
}

function img(file, wIn) {
  const buf = fs.readFileSync("figs/" + file);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const wpx = wIn * 96, hpx = wpx * h / w;
  return new ImageRun({ type: "png", data: buf, transformation: { width: wpx, height: hpx },
    altText: { title: file, description: file, name: file } });
}
const fig = (file, wIn) => new Paragraph({ children: [img(file, wIn)], alignment: AlignmentType.CENTER,
  spacing: { before: 60, after: 0 }, keepNext: true });
function figPair(f1, f2, c1, c2) {
  const half = W / 2;
  const mk = (f, c) => new TableCell({ borders: noBorders, width: { size: half, type: WidthType.DXA },
    margins: { left: 40, right: 40 },
    children: [new Paragraph({ children: [img(f, 3.0)], alignment: AlignmentType.CENTER, spacing: { after: 0 } }),
      new Paragraph({ children: runs(capText(c), { size: 24 }), alignment: AlignmentType.CENTER, spacing: { before: 40, after: 60, line: 276 } })] });
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [half, half],
    borders: { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none },
    rows: [new TableRow({ cantSplit: true, children: [mk(f1, c1), mk(f2, c2)] })] });
}

// Table of contents line with dot leader
const tocLine = (label, key, indent = 0, bold = false) => new Paragraph({
  tabStops: [{ type: TabStopType.RIGHT, position: W, leader: "dot" }],
  indent: { left: indent }, spacing: { after: 0, line: 360 },
  children: [new TextRun({ text: label, bold }), new TextRun({ text: "\t" + (PAGES[key] ?? "") , bold })],
});

// ---------------- FRONT MATTER ----------------
function imgW(file, wIn) {
  const buf = fs.readFileSync("figs/" + file);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  return new ImageRun({ type: "png", data: buf, transformation: { width: wIn * 96, height: wIn * 96 * h / w },
    altText: { title: file, description: file, name: file } });
}
const spaced = (t) => t.split("").join(" ");
const HEAD = (t, spacedOut = false) => C(spacedOut ? spaced(t) : t, { run: { bold: true, size: 28 }, after: 280, before: 120 });
const TEAM = [["P. Sahasra Reddy", "1601-23-732-015"], ["M. Bhagirath Reddy", "1601-23-732-046"], ["P. Sreekar Aditya Reddy", "1601-23-732-048"]];
const NOB = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
const teamTable = new Table({ width: { size: 5600, type: WidthType.DXA }, columnWidths: [3200, 2400], alignment: AlignmentType.CENTER, borders: NOB,
  rows: TEAM.map(([n, r]) => new TableRow({ children: [n, r].map((t, k) => new TableCell({ borders: noBorders, width: { size: k ? 2400 : 3200, type: WidthType.DXA },
    children: [new Paragraph({ children: [new TextRun({ text: t, bold: true })], spacing: { after: 60, line: 300 } })] })) })) });

const titlePage = [
  new Paragraph({ children: [imgW("cbit_banner.png", 6.2)], alignment: AlignmentType.CENTER, spacing: { after: 300 } }),
  C("A Project Part 1 Report", { run: { bold: true, size: 30 }, after: 120 }),
  C("on", { after: 200 }),
  C(TITLE, { run: { bold: true, size: 32 }, after: 240, line: 300 }),
  C("A project report submitted for the partial fulfilment of award of Bachelor of Engineering in Civil Engineering", { after: 120 }),
  C("By", { after: 120 }),
  teamTable,
  C("Under the Guidance of", { before: 160, after: 120 }),
  C("Dr. A. Balaji Rao", { run: { bold: true }, after: 60 }),
  C("Associate Professor, Department of Civil Engineering", { after: 120 }),
  C("Submitted to", { after: 120 }),
  C("Dr. Dudam Bharath Kumar", { run: { bold: true }, after: 60 }),
  C("Assistant Professor, Department of Civil Engineering", { after: 120 }),
  new Paragraph({ children: [imgW("cbit_crest.png", 0.95)], alignment: AlignmentType.CENTER, spacing: { after: 120 } }),
  C("DEPARTMENT OF CIVIL ENGINEERING", { run: { bold: true }, after: 80 }),
  C("CHAITANYA BHARATHI INSTITUTE OF TECHNOLOGY (Autonomous)", { run: { bold: true }, after: 80 }),
  C("Gandipet, Hyderabad – 500075", { after: 80 }),
  C("November 2026", { run: { bold: true } }),
];

const declaration = [
  HEAD("DECLARATION", true),
  P(`We hereby declare that the project work entitled **"${TITLE}"** submitted to the Department of Civil Engineering, Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad in partial fulfilment of the requirements for the award of the degree of Bachelor of Engineering in Civil Engineering, is a record of original work carried out by us under the supervision of Dr. A. Balaji Rao, Associate Professor, Department of Civil Engineering, CBIT, Hyderabad.`),
  P("We further declare that the work reported in this project has not been submitted, either in part or in full, for the award of any other degree or diploma in this institute or any other institution.", { after: 500 }),
  P("Signature of candidates:", { after: 700 }),
  ...TEAM.map(([n, r]) => P(`**${n} (${r})**`, { after: 700, align: AlignmentType.LEFT })),
  P("B.E. Civil Engineering, CBIT, Hyderabad", { after: 60, align: AlignmentType.LEFT }),
  P("November 2026", { align: AlignmentType.LEFT }),
];

const sigBlock = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W / 2, W / 2], borders: NOB,
  rows: [new TableRow({ children: [
    ["Dr. A. Balaji Rao", "Associate Professor, Department of Civil Engineering, CBIT, Hyderabad"],
    ["Dr. K. Jagannadha Rao", "Professor and Head, Department of Civil Engineering, CBIT, Hyderabad"],
  ].map(([n, d]) => new TableCell({ borders: noBorders, width: { size: W / 2, type: WidthType.DXA }, margins: { right: 200 },
    children: [new Paragraph({ children: [], spacing: { before: 1300 } }),
      new Paragraph({ children: [new TextRun({ text: n, bold: true })], spacing: { after: 40, line: 300 } }),
      new Paragraph({ children: [new TextRun({ text: d })], spacing: { after: 0, line: 300 } })] })) })] });

const certificate = [
  HEAD("CERTIFICATE", true),
  P(`This is to certify that the project entitled **"${TITLE}"** is a bonafide record of work carried out by the students of B.E. Civil Engineering (Batch 2027) in partial fulfilment of the requirements for the award of the degree of Bachelor of Engineering in Civil Engineering from Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad, affiliated to Osmania University.`),
  P("The project was carried out under my supervision and guidance during the academic year 2026–2027. To the best of my knowledge and belief, the work reported herein does not form part of any other project report or dissertation on the basis of which a degree or award was conferred on an earlier occasion on this or any other candidate.", { after: 200 }),
  sigBlock,
  P("", { after: 600 }),
  P("Place: Hyderabad", { after: 60, align: AlignmentType.LEFT }), P("Date: November 2026", { align: AlignmentType.LEFT }),
];

const ack = [
  HEAD("ACKNOWLEDGEMENTS"),
  P("The authors wish to express sincere gratitude to **Dr. A. Balaji Rao**, Associate Professor, Department of Civil Engineering, Chaitanya Bharathi Institute of Technology (CBIT), Hyderabad, for his valuable guidance and constant encouragement throughout this project."),
  P("The authors would like to thank **Dr. K. Jagannadha Rao**, Professor and Head, Department of Civil Engineering, CBIT, for his institutional support and for providing the resources necessary to conduct this research."),
  P("Sincere thanks are also due to **Dr. C. V. Narasimhulu**, Professor and Principal, CBIT, for providing the necessary facilities to carry out this work."),
  P("Finally, the authors thank the review panel members, faculty and laboratory staff of the Department of Civil Engineering, CBIT, for their questions, comments and support during the project."),
];

const toc = [
  HEAD("TABLE OF CONTENTS"),
  tocLine("Declaration", "decl"), tocLine("Certificate", "cert"), tocLine("Acknowledgements", "ack"), tocLine("Abstract", "abs"),
  tocLine("List of Figures", "lof"), tocLine("List of Tables", "lot"), tocLine("Nomenclature", "nom"),
  tocLine("CHAPTER 1: INTRODUCTION", "ch1"),
  tocLine("1.1 Background and Need for the Study", "s11", 300), tocLine("1.2 Present State of Knowledge", "s12", 300),
  tocLine("1.3 Gap Identified", "s13", 300), tocLine("1.4 Aim, Objectives and Hypotheses", "s14", 300),
  tocLine("CHAPTER 2: LITERATURE REVIEW", "ch2"),
  tocLine("CHAPTER 3: METHODOLOGY", "ch3"),
  tocLine("3.1 Description of Location", "s31", 300), tocLine("3.2 Specimen and Materials", "s32", 300), tocLine("3.3 Methodology", "s33", 300), tocLine("3.4 Design-Space Dataset", "s34", 300),
  tocLine("CHAPTER 4: RESULTS AND DISCUSSION", "ch4"),
  tocLine("4.1 Stiffness Left After Loading", "s41", 300), tocLine("4.2 Vibration Against Deflection", "s42", 300),
  tocLine("4.3 Twin Accuracy", "s43", 300), tocLine("4.4 Blind Validation Against a Published Test", "s44", 300),
  tocLine("4.5 Retrofit Simulation", "s45", 300), tocLine("4.6 Repair Rule for the Specimens", "s46", 300), tocLine("4.7 Design-Space Dataset", "s47", 300),
  tocLine("CHAPTER 5: CONCLUSIONS", "ch5"),
  tocLine("CHAPTER 6: WORK PROGRESS", "ch6"),
  tocLine("CHAPTER 7: ACHIEVEMENTS", "ch7"),
  tocLine("REFERENCES", "ref"),
  tocLine("ANNEXURE", "anA"),
];

const lofLine = (label, text, key) => new Paragraph({
  tabStops: [{ type: TabStopType.RIGHT, position: W, leader: "dot" }], spacing: { after: 0, line: 360 },
  children: [new TextRun({ text: label + " ", bold: true }), new TextRun({ text: titleCase(text) + "\t" + (PAGES[key] ?? "") })] });
const lof = [
  HEAD("LIST OF FIGURES"),
  lofLine("Figure 1.", "Specimen elevation and cross-section under four-point bending", "f1"),
  lofLine("Figure 2.", "Methodology flow diagram", "f2"),
  lofLine("Figure 3.", "Sobol total indices of the stiffness left after 72 kN", "f3"),
  lofLine("Figure 4.", "Median deflection error at 72 kN for four estimators", "f4"),
  lofLine("Figure 5.", "Least intrusive compliant scheme across 10,000 beams", "f5"),
  lofLine("Figure 6.", "Share of beams where each scheme complies", "f6"),
  lofLine("Figure 7.", "Gantt chart of the project", "f7"),
  lofLine("Figure A-1.", "Static against vibration stiffness loss, 10,000 beams", "f8"),
  lofLine("Figure A-2.", "Growth of deflection under sustained load", "f9"),
];
const lot = [
  HEAD("LIST OF TABLES"),
  lofLine("Table 1.", "Hypotheses and their status", "t1"),
  lofLine("Table 2.", "Summary of key studies", "t2"),
  lofLine("Table 3.", "Materials and random inputs of the Monte Carlo simulation", "t3"),
  lofLine("Table 4.", "Deflection stiffness left at three load levels", "t4"),
  lofLine("Table 5.", "Blind prediction against a published test", "t5"),
  lofLine("Table 6.", "Decision tree performance", "t6"),
  lofLine("Table 7.", "Repair rule for the specimens", "t7"),
  lofLine("Table 8.", "Achievements of Part 1", "t8"),
  lofLine("Table A-1.", "Ranges of the design-space population", "t9"),
  lofLine("Table A-2.", "Stiffness left and vibration fraction by damage stage", "t10"),
  lofLine("Table A-3.", "Condition stages of the design-space dataset", "t11"),
  lofLine("Table A-4.", "Mesh convergence and independent elastic check", "tb1"),
  lofLine("Table A-5.", "Capacities of the supporting published programme", "tb2"),
  lofLine("Table A-6.", "Planned instrumentation of the Part 2 beam tests", "tb3"),
];
function subRuns(t) {            // "f_{ck}" -> f with subscript ck
  const out = []; const re = /_\{([^}]*)\}/g; let last = 0, m;
  while ((m = re.exec(t))) { if (m.index > last) out.push(new TextRun({ text: t.slice(last, m.index) })); out.push(new TextRun({ text: m[1], subScript: true })); last = m.index + m[0].length; }
  if (last < t.length) out.push(new TextRun({ text: t.slice(last) })); return out;
}
const NOM = [
  ["b, h, d", "Width, overall depth and effective depth of the section (mm)"],
  ["L", "Clear span (mm or m)"],
  ["f_{ck}", "Characteristic compressive strength of concrete (MPa)"],
  ["E_{c}, E_{s}", "Elastic modulus of concrete and of steel (MPa)"],
  ["f_{t}", "Tensile strength of concrete (MPa)"],
  ["f_{y}", "Yield strength of steel (MPa)"],
  ["P, P_{y}", "Total load; hand-calculated first-yield load (kN)"],
  ["δ", "Midspan deflection (mm)"],
  ["EI", "Flexural rigidity (kN·m²)"],
  ["f", "Natural frequency (Hz)"],
  ["κ", "Fraction of the static stiffness loss registered by a vibration measurement"],
  ["f_{open}, f_{closed}", "Frequency of the cracked beam with cracks open; frequency of the undamaged beam (Hz)"],
  ["ε_{fd}", "Debonding strain of a bonded laminate"],
  ["R²", "Coefficient of determination"],
  ["IS", "Indian Standard (Bureau of Indian Standards)"],
  ["ACI", "American Concrete Institute"],
  ["CBIT", "Chaitanya Bharathi Institute of Technology"],
];
const nom = [HEAD("NOMENCLATURE"),
  new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [2000, W - 2000], borders: NOB,
    rows: NOM.map(([a, d]) => new TableRow({ children: [a, d].map((t, k) => new TableCell({ borders: noBorders, width: { size: k ? W - 2000 : 2000, type: WidthType.DXA },
      children: [new Paragraph({ children: subRuns(t), spacing: { after: 40, line: 360 } })] })) })) })];

const abstract = [
  HEAD("ABSTRACT"),
  P("Visual inspection and code checks treat a cracked reinforced concrete beam as either sound or unsafe, and they rarely measure how much stiffness the beam has lost. This project develops a digital twin that measures the present condition of a reinforced concrete member and recommends the least intrusive retrofit that restores compliance with IS 456:2000. In Part 1, we model a simply supported beam of 230 × 300 mm section, 3.0 m span, M30 concrete and three 12 mm Fe500 bars under four-point bending, using an OpenSeesPy model whose cross-section is divided into concrete and steel fibres. We propagate the scatter of five material properties through 300 simulated beams loaded to 72 kN. The deflection stiffness left after 72 kN has a median of 39%, with a 90% band of 23% to 66%, and scatter in tensile strength explains 67% of the output variance. A vibration reading registers only a fraction of this loss (31% to 39% in the published tests), so natural frequency alone over-estimates the stiffness of a cracked beam. The twin, which combines deflection and vibration readings with calibrated uncertainty, predicts deflection with a median error of 0.7% on 150 unseen beams. Against a published four-point bending test, the blind model reproduces the frequency of the freely hung beam within 3.3% and the peak load within 3.0%. A simulation of 10,000 beams designed to IS 456:2000 finds carbon fibre laminates the least intrusive compliant scheme for 49% of damaged beams. A three-level decision tree selects the correct scheme for 90.1% of 3,000 unseen beams. An open dataset of 10,000 further beams, with strengthening, corrosion and 50-year sustained-load stages, shows that vibration registers 48% to 62% of the stiffness loss as damage grows. Part 2 tests the twin and its repair decisions on our own beams.", { after: 240 }),
  P("**Keywords:** 1. Residual flexural stiffness; 2. Vibration-based stiffness bias; 3. Tensile strength scatter; 4. Deflection-updated digital twin; 5. Least intrusive retrofit selection"),
];

// ---------------- BODY ----------------
const body = [
  H1("CHAPTER 1: INTRODUCTION"),
  H2("1.1 Background and Need for the Study"),
  P("Reinforced concrete beams crack in service. Overload, a change of use or long-term creep widens these cracks and lowers the flexural stiffness of the beam; a less stiff beam deflects more and protects its steel less. An engineer who inspects the beam sees the cracks but cannot see how much stiffness the beam has lost or whether it still meets IS 456:2000, the Indian Standard code of practice for plain and reinforced concrete. This project builds a digital twin of a reinforced concrete member: a computational model that takes measurements from the real beam, updates its estimate of the beam's present stiffness, and recommends the least intrusive repair or retrofit that brings the beam back within code limits. We start with a single simply supported beam rather than a building, because a specimen lets us control the loading, measure the damage directly and test each retrofit to failure. Part 1, reported here, builds and checks the computational side of the twin; Part 2 casts and tests the physical beams."),
  H2("1.2 Present State of Knowledge"),
  P("Vibration-based damage identification rests on one link: damage lowers stiffness, and lower stiffness lowers natural frequency (Fan & Qiao, 2011). On the Z24 bridge, temperature moved the frequencies by more than the imposed damage did (Peeters & De Roeck, 2001), and the stiffness inferred from vibration recovered when cracks closed (Maeck & De Roeck, 2003). Laboratory tests confirm the same gap at member scale: Musiał et al. (2021) found that beams loaded to 45 kN kept about 54% of their static stiffness but about 80% of their vibration stiffness, and Ozturkoglu et al. (2024) found vibration stiffness of 88% to 98% in beams whose static stiffness had fallen below half. Both studies also show that bonded carbon fibre laminates restore part of the lost stiffness and strength, under the design rules of ACI PRC-440.2-23. Digital twin research joins measurement, model updating and decision into one loop (Kapteyn et al., 2021), and Torzoni et al. (2024) applied it to civil structures with vibration-based damage classification and maintenance planning."),
  H2("1.3 Gap Identified"),
  P("Three gaps remain. First, civil digital twins are trained and tested on synthetic data only and treat stiffness reductions below 30% as undamaged (Torzoni et al., 2024); none has been checked against measured static and dynamic stiffness of the same reinforced concrete beam. Second, no study has quantified how much of the static stiffness loss a vibration reading registers across the scatter of real concrete properties. Third, existing twins stop at a damage label; none ends in a retrofit scheme checked against the flexure, shear, deflection and crack-width clauses of IS 456:2000 and the strengthening provisions of IS 15988:2013."),
  H2("1.4 Aim, Objectives and Hypotheses"),
  P("**Aim:** To develop and experimentally validate a digital twin that measures damage in reinforced concrete beams and recommends retrofitting.", { after: 40 }),
  P("**Objectives:**", { after: 20 }),
  NUM("To model the flexural response of a reinforced concrete beam under four-point bending and quantify how material scatter spreads the stiffness left after a given load."),
  NUM("To quantify how much of the static stiffness loss a vibration measurement registers, and to correct the twin for this bias."),
  NUM("To build a twin that predicts the service-load deflection of a damaged beam within 5%, with calibrated uncertainty bounds."),
  NUM("To validate the beam model blind against published laboratory tests before testing our own beams."),
  NUM("To select, for each damaged beam, the least intrusive retrofit that restores compliance with IS 456:2000, and to verify it by failure tests."),
  tcaption("**Table 1.** Hypotheses and their status at the end of Part 1"),
  table(["No.", "Hypothesis", "Status"], [
    ["H1", "Damage must be measured; it cannot be inferred from the load history.", "Supported (published tests, simulation)"],
    ["H2", "Vibration over-estimates the stiffness of a cracked beam.", "To be confirmed on own beams; supported by two published tests and simulation"],
    ["H3", "The twin predicts the 30 kN service deflection within 5%.", "Supported in simulation; to confirm on own beams"],
    ["H4", "The recommended repair meets the target capacity.", "To be tested by failure tests in Part 2"],
  ], [700, 5000, 3326]),

  H1("CHAPTER 2: LITERATURE REVIEW"),
  P("We organise the review around the chain the twin follows: how a cracked beam loses stiffness, how a measurement sees that loss, how a model turns the measurement into a state, and how the state becomes a repair decision."),
  P("**Stiffness loss in a cracked beam.** After cracking, concrete between cracks still carries tension through bond (tension stiffening), so a beam stays stiffer than its fully cracked section until the steel yields. ACI 318-19 and IS 1893 (Part 1):2016 take 0.70 of the gross moment of inertia for uncracked members and 0.35 for cracked beams; for our beam the fully cracked section gives 0.22. These are design averages and do not say how much stiffness a particular beam has left. Fibre-section models capture the behaviour by integrating concrete and steel fibres along force-based elements (Spacone et al., 1996; McKenna, 2011), and the tension-softening law of the concrete controls how fast stiffness falls after cracking."),
  P("**What vibration sees.** A vibration test excites the beam at strains far below service, so flexural cracks stay closed and the frequency reflects a stiffer, partly closed section (Maeck & De Roeck, 2003). This is why vibration stiffness stays high while static stiffness falls (Musiał et al., 2021; Ozturkoglu et al., 2024). Damage also affects durability: Picandet et al. (2001) found gas permeability rising exponentially with damage measured as loss of dynamic modulus, which is why IS 456:2000 (clause 35.3.2) tightens crack-width limits from 0.3 mm to 0.2 mm and 0.1 mm for harsher exposure."),
  P("**Twins and model updating.** Kapteyn et al. (2021) formalised the digital twin as a probabilistic graphical model linking physical state, data, model and action. Torzoni et al. (2024) built one for civil structures from synthetic data. Bayesian model updating (Beck & Katafygiotis, 1998) lets a twin report bounds on stiffness; Sobol indices (Sobol, 2001; Saltelli et al., 2010) rank uncertain inputs; bootstrap resampling (Efron, 1979) gives intervals without a distributional assumption."),
  P("**From condition to repair.** ACI 562-16 separates repair (renewal for maintenance) from strengthening (increase in capacity). IS 15988:2013 (clause 8.5.1) lists concrete, steel and fibre-reinforced polymer jacketing but gives no damage scale for flexural members. ACI PRC-440.2-23 limits laminates by debonding strain (Teng et al., 2003) and requires the unstrengthened member to carry 1.1 times dead load plus 0.75 times live load. Seismic indices such as that of Park and Ang (1985) need hysteretic energy and do not apply to monotonic service damage."),
  tcaption("**Table 2.** Summary of key studies"),
  table(["Study", "Contribution", "Left open for this project"], [
    ["Peeters & De Roeck (2001); Maeck & De Roeck (2003)", "Frequency changes on a bridge; environmental effects; recovery on crack closure", "Member-level static stiffness"],
    ["Musiał et al. (2021); Ozturkoglu et al. (2024)", "Static and dynamic stiffness of the same beams, before and after laminates", "No twin; no code-based scheme choice"],
    ["Picandet et al. (2001)", "Dynamic-modulus damage linked to gas permeability", "Coupons, not members"],
    ["Kapteyn et al. (2021); Torzoni et al. (2024)", "Digital twin framework; vibration-based damage classification", "Synthetic data only; no code checks"],
  ], [2800, 3600, 2626]),

  H1("CHAPTER 3: METHODOLOGY"),
  H2("3.1 Description of Location"),
  P("The computational work was carried out on the team's computers and on cloud computing servers. The Part 2 specimens are to be cast and tested in the laboratories of the Department of Civil Engineering, Chaitanya Bharathi Institute of Technology, Gandipet, Hyderabad. No field site is involved in Part 1."),
  H2("3.2 Specimen and Materials"),
  P("A simply supported beam of 230 × 300 mm section and 3.0 m span, reinforced with three 12 mm Fe500 bars, was adopted (Figure 1). Two equal loads are applied 1.0 m from each support, so the middle 1.0 m is under constant moment. The hand-calculated yield load is 81.2 kN, the design load 69.8 kN and the service load 46.5 kN; damage stages from 35 kN to 72 kN were defined, all below yield. Top bars of 6 to 10 mm were found to change the results by less than 1.5%. The materials and random inputs are given in Table 3."),
  fig("f31_specimen.png", 5.6),
  caption("**Figure 1.** Specimen elevation and cross-section; the shaded zone carries constant moment."),
  tcaption("**Table 3.** Materials and random inputs of the Monte Carlo simulation"),
  table(["Material or input", "Value or distribution"], [
    ["Concrete, M30: characteristic strength", "Normal, mean 30 MPa, standard deviation 5 MPa, truncated at 20 MPa"],
    ["Concrete elastic modulus", "5000 √(strength) × lognormal factor, coefficient of variation 15%"],
    ["Concrete tensile strength", "0.7 √(strength) × lognormal factor, coefficient of variation 15%"],
    ["Tension-softening slope", "Uniform, 0.05 to 0.10 of the elastic modulus"],
    ["Steel, Fe500: yield strength", "Normal, mean 500 MPa, standard deviation 25 MPa"],
    ["Retrofit materials", "Carbon fibre strips 50 × 1.2 mm (1 to 4 strips, 1 or 2 plies); steel plate 3 to 6 mm; concrete jacket 75 to 125 mm"],
  ], [3400, 5626]),
  H2("3.3 Methodology"),
  P("The work was organised in the eight steps of Figure 2.", { after: 0 }),
  fig("f32_flow.png", 6.2),
  caption("**Figure 2.** Methodology flow diagram; step 5 (shaded) is the calibration of the twin."),
  P("**Step 1, specimen.** The section was checked for flexure (clause 38.1), shear (clause 40) and deflection (clause 23.2) of IS 456:2000. **Step 2, model.** The beam was modelled in OpenSeesPy, an open-source structural analysis program, with 24 force-based elements: beam elements whose cross-section is divided into concrete and steel fibres, so that cracking and yielding are followed through the depth. Concrete fibres were given a tension-softening branch and steel fibres a smooth bilinear (Menegotto–Pinto) law with 1% hardening, and each beam was loaded and unloaded at each damage stage. Mesh convergence and the elastic response were checked independently, including in STAAD.Pro, a commercial structural analysis program (Annexure, Table A-4). **Step 3, Monte Carlo simulation.** In a Monte Carlo simulation the model is run many times, each time with material properties drawn at random from their measured scatter. Three hundred beams were sampled from Table 3 and loaded to 72 kN. The deflection stiffness left was recorded, and the vibration reading was represented by κ, the fraction of static loss that vibration registers (0.31 to 0.39 from the published tests). Beam 56 failed to converge numerically and was rerun with 200 element iterations and deeper sub-stepping; three converged beams rerun the same way gave identical results. **Step 4, sensitivity.** A quadratic surrogate, a polynomial fitted to the 300 results that stands in for the full model, was checked by five-fold cross-validation (fitted on four-fifths of the beams and tested on the rest, five times). Sobol total indices, the share of the output variance caused by each input including its interactions, were computed on it."),
  P("**Step 5, twin.** The twin's uncertainty was calibrated on beams 0 to 149 and tested on beams 150 to 299. Four estimators of deflection were compared: no updating, vibration only, deflection only, and the twin, which combines both. Median error, 90% interval coverage, bootstrap intervals and paired significance tests were computed. **Step 6, blind validation.** The tests of Musiał et al. (2021) were modelled before their results were compared; their stiffness–load figure was digitised with a reading uncertainty of 0.05 MN·m², and the twin logic was run on the measured data at checks every 5 kN. Two further programmes, Ozturkoglu et al. (2024) and Pešić et al. (2015), were used as supporting evidence (Annexure, Table A-5). **Step 7, retrofit simulation.** Ten thousand simply supported, uniformly loaded beams were designed to IS 456:2000 (span 3 to 8 m, M20 to M30, tension steel 0.5% to 1.2%, all exposure classes), given a damage level from Step 3 at the twin's lower 95% bound, and, for half of them, a change of use of 1.5 or 2.0 times the live load. Each beam was checked for flexure, shear, deflection (Annex C) and crack width (Annex F) before and after each scheme, and the least intrusive compliant scheme was chosen in the order monitor, seal cracks, laminates, steel plate, concrete jacket. **Step 8, decision tree and rule.** A decision tree, a sequence of yes-or-no questions on the beam's demand and condition, was limited to three levels, weighted so that rare plate and jacket cases were not ignored, trained on 70% of the beams, tested on the other 30% (Pedregosa et al., 2011) and rerun with 3,000 beams; a Red/Amber/Green rule for our specimens was checked against IS 456:2000, ACI 318-19, ACI 437R-03, ACI 562-16 and ACI PRC-440.2-23."),

  H2("3.4 Design-Space Dataset"),
  P("The model of Step 2 was then applied to 10,000 beams covering the range of simply supported beams found in buildings. Each beam was taken through five damage stages, given simulated instrument readings and two benchmark tasks, and extended with strengthening, corrosion, sustained-load and fatigue stages; 40 beams were reanalysed with a continuum model as a cross-check. The dataset is published on Zenodo (Pesaru et al., 2026a); its design ranges and procedure are given in the Annexure (Tables A-1 to A-3). The code of every step, the processing scripts and the source files of this report are kept in a public GitHub repository (Pesaru et al., 2026b)."),

  H1("CHAPTER 4: RESULTS AND DISCUSSION"),
  H2("4.1 Stiffness Left After Loading (H1)"),
  P("All 300 beams converged. The deflection stiffness left after 72 kN has a median of 39% and a 90% band of 23% to 66% (bootstrap 95% interval of the median 37.0% to 41.3%); beam 56 keeps the least, 17.7%. Two nominally identical published beams kept 51% and 57% at 45 kN. The overlap between load levels is large (Table 4): 20% of beams loaded only to service read below 70%, and 55% loaded to design read above 40%. The load history cannot tell how much stiffness a beam has lost, which supports H1: damage must be measured, not inferred from the load history. Tensile-strength scatter drives 67% of this spread and cube strength only 7% (Figure 3; surrogate cross-validated R² 0.951)."),
  tcaption("**Table 4.** Deflection stiffness left at three load levels (300 beams)"),
  table(["Load level", "Load (kN)", "Median left (%)", "Range (%)"], [
    ["Service", "46.5", "81", "56 to 94 (5th to 95th percentile)"],
    ["Design", "69.8", "43", "23 to 69 (5th to 95th percentile)"],
    ["Final damage stage", "72.0", "39", "23 to 66 (90% band)"],
  ], [2400, 1500, 1800, 3326]),
  H2("4.2 Vibration Against Deflection (H2)"),
  P("With κ between 0.31 and 0.39, the vibration reading after 72 kN reports 79% stiffness left (72% to 88%) against 39% from deflection. The published tests show the same bias: 80% against 54% at 45 kN (Musiał et al., 2021), and 88% to 98% against 45% to 48% after yield (Ozturkoglu et al., 2024). Vibration registers only a fraction of the static loss because cracks stay closed at small amplitudes, which supports H2: vibration over-estimates the stiffness of a cracked beam."),
  H2("4.3 Twin Accuracy (H3)"),
  P("H3 states that the twin predicts the service deflection within 5%. The twin and the deflection-only estimator both reach a median error of 0.7% at 72 kN (twin bootstrap interval 0.57% to 0.78%), against 60% with no updating and 51% with vibration only (Figure 4). The twin beats vibration only (p < 0.001) but not deflection only (p = 0.052), so the deflection reading carries most of the information. The 90% interval covers 89% to 93% of beams at 50 to 72 kN but only 81% at 35 kN; the intervals will be recalibrated with our own data. On the published measurements, learning the vibration bias cut the error from 30% to 4% (5.5% when the last check was held out)."),
  figPair("f41_sobol.png", "f42_error.png",
    "**Figure 3.** Sobol total indices of the stiffness left after 72 kN",
    "**Figure 4.** Median deflection error at 72 kN for four estimators"),
  H2("4.4 Blind Validation Against a Published Test"),
  P("The test beam of Musiał et al. (2021) was modelled from its reported materials before its results were examined. The free–free frequency in Table 5 is the first bending frequency of the beam hung freely, with no supports."),
  tcaption("**Table 5.** Blind prediction against the test of Musiał et al. (2021)"),
  table(["Quantity", "Predicted", "Measured", "Difference"], [
    ["Free–free natural frequency (Hz)", "85.5", "88.4", "−3.3%"],
    ["Peak load (kN)", "55.7", "57.4", "−3.0%"],
    ["Static stiffness left at 45 kN (%)", "55", "54", "+1 point"],
    ["Strengthened capacity, laminates (kN)", "80 and 107", "90 and 116", "8% to 11% conservative"],
  ], [3800, 1700, 1700, 1826]),
  P("The end points match well, but the stiffness path from 12 to 45 kN differs by 19 percentage points (root mean square) and by 29 at worst. Fourteen other tension laws came within 10 to 11 points, but the best law changed with the treatment of setup compliance, so the path is not identifiable from this test. We kept the base model unchanged: the twin corrects the model with measurements instead of relying on its stiffness path."),
  H2("4.5 Retrofit Simulation"),
  P("Across 10,000 beams, laminates are the least intrusive compliant scheme for 49%, monitoring suffices for 32% and crack sealing for 15%; only 4.5% need a plate or jacket (Figure 5). Laminates comply in 97% to 100% of beams needing up to 30% more strength but only 58% at 50% to 60%, where debonding governs; plates comply in at least 91% and jackets in all (Figure 6). The decision tree (Table 6) splits on moment demand to capacity, crack width to its limit, deflection to its limit and span to effective depth; its errors lean to the safe side (249 laminate beams sent to plate, 20 plate or jacket beams sent to laminates). An unweighted tree scores 95.7% but catches only 60 of 135 plate or jacket beams, so the weighted tree was kept."),
  figPair("f43_counts.png", "f44_compliance.png",
    "**Figure 5.** Least intrusive compliant scheme across 10,000 beams",
    "**Figure 6.** Share of beams where each scheme complies, by strength increase needed"),
  tcaption("**Table 6.** Decision tree performance"),
  table(["Measure", "10,000 beams", "3,000-beam check"], [
    ["Correct on unseen beams", "90.1% (3,000 beams)", "89.6% (900 beams)"],
    ["Correct on training beams; balanced accuracy", "91.0%; 91.5%", "Same scheme shares"],
    ["Plate or jacket beams caught", "115 of 135", "Same laminate limit"],
  ], [3800, 2600, 2626]),
  H2("4.6 Repair Rule for the Specimens"),
  P("All damage stages lie below the 81.2 kN yield load, so strength is intact and the loss is in serviceability; at 72 kN the hand-calculated steel stress is about 440 MPa (0.89 of yield), so a real beam may yield. The rule of Table 7 is therefore serviceability-led with a strength guard; its stiffness thresholds will be reset from our first beam, loaded to 46.5 kN. Relative to the bare cracked section, two laminates raise the cracked moment of inertia 1.33 times, a 100 × 5 mm plate 2.50 times and a 75 mm jacket 2.16 times. These results cover damage before yield and do not replace an engineer's inspection; H4 awaits the Part 2 failure tests."),
  tcaption("**Table 7.** Repair rule for the specimens"),
  table(["Class", "Action", "Trigger"], [
    ["Red", "Strengthen; check ACI PRC-440.2-23 Equation 9.2 before laminates", "Recovery under 75% of peak deflection, cracks 1 mm or wider, or yielding or spalling"],
    ["Amber", "Seal or inject cracks, stiffen if needed, monitor", "Cracks over 0.3 mm under service load, or stiffness left under 70%"],
    ["Green", "Monitor", "Cracks 0.3 mm or less, full recovery, stiffness left 70% or more"],
  ], [1100, 3700, 4226]),

  H2("4.7 Design-Space Dataset"),
  P("Across the 10,000 beams, vibration again registered only a fraction of the static stiffness loss, rising from 0.48 at the first damage stage to 0.62 at the last (medians); on the beams of Musiał et al. (2021) the breathing-crack relation gave 0.44 against 0.42 measured. The fraction therefore depends on the beam and the damage level, but in every case vibration under-reports the loss, which extends H2 across the design space. With one noisy reading per stage, a learned model estimated the stiffness left within 2.9 percentage points, against 19.9 for reading vibration directly. Strengthening raised the peak load by a median of 18% (laminates) to 44% (jacket); corrosion of 15% cut it by 22%; and 50 years of sustained service load increased the deflection 2.7 times, 0.90 of the IS 456:2000 Annex C estimate. A continuum model gave larger deflections after cracking, so the fibre values are a lower bound for short or deep beams. The Annexure gives the full results (Tables A-2 and A-3, Figures A-1 and A-2)."),

  H1("CHAPTER 5: CONCLUSIONS"),
  P("Nominally identical beams kept between 23% and 66% of their stiffness after the same load, so the condition of a beam has to be measured rather than inferred from its load history. Scatter in tensile strength explains 67% of this spread, which means cube strength alone cannot predict how a beam cracks and softens."),
  P("Natural frequency registered only a fraction of the static stiffness loss, so a twin that relies on frequency alone under-reports damage. Our twin predicted deflection with a median error of 0.7% on unseen beams, and learning the vibration bias reduced the error on published test data from 30% to 4%. The blind model matched the published frequency and peak load within 3.3% and predicted strengthened capacity 8% to 11% on the safe side."),
  P("Across 10,000 beams designed to IS 456:2000, laminates were the least intrusive compliant repair for 49% of beams and worked up to about 30% additional strength, and a decision tree of depth three selected the correct scheme for 90.1% of unseen beams. In Part 2, we will test our own beams to confirm on measured data that the twin predicts service deflection within 5% (H3), reset the repair thresholds, and load the retrofitted beams to failure to check that each recommended repair reaches its target capacity (H4)."),
  P("In the design-space dataset of 10,000 further beams, the share of the static stiffness loss that vibration registered rose from 0.48 to 0.62 with damage, so the vibration bias is not a fixed number and has to be learned for each beam, as the twin does. With one noisy reading per stage, a learned model estimated the stiffness left within 3 percentage points, against 20 for reading vibration directly. Corrosion of 15% cut the peak load by 22%, and 50 years of sustained service load nearly tripled the deflection, in line with the code method used as a check. These results are published as an open dataset with a permanent identifier."),
];

const refs = [
  "American Concrete Institute. (2003). *Strength evaluation of existing concrete buildings* (ACI 437R-03). American Concrete Institute.",
  "American Concrete Institute. (2016). *Code requirements for assessment, repair, and rehabilitation of existing concrete structures and commentary* (ACI 562-16). American Concrete Institute.",
  "American Concrete Institute. (2019). *Building code requirements for structural concrete and commentary* (ACI 318-19). American Concrete Institute.",
  "American Concrete Institute. (2023). *Design and construction of externally bonded fiber-reinforced polymer (FRP) systems for strengthening concrete structures: Guide* (ACI PRC-440.2-23). American Concrete Institute.",
  "Beck, J. L., & Katafygiotis, L. S. (1998). Updating models and their uncertainties. I: Bayesian statistical framework. *Journal of Engineering Mechanics, 124*(4), 455–461. https://doi.org/10.1061/(ASCE)0733-9399(1998)124:4(455)",
  "Bureau of Indian Standards. (2000). *Plain and reinforced concrete: Code of practice* (IS 456:2000, 4th rev.). Bureau of Indian Standards.",
  "Bureau of Indian Standards. (2013). *Seismic evaluation and strengthening of existing reinforced concrete buildings: Guidelines* (IS 15988:2013). Bureau of Indian Standards.",
  "Bureau of Indian Standards. (2016). *Criteria for earthquake resistant design of structures, Part 1: General provisions and buildings* (IS 1893 (Part 1):2016, 6th rev.). Bureau of Indian Standards.",
  "Coronelli, D., & Gambarova, P. (2004). Structural assessment of corroded reinforced concrete beams: Modeling guidelines. *Journal of Structural Engineering, 130*(8), 1214–1224. https://doi.org/10.1061/(ASCE)0733-9445(2004)130:8(1214)",
  "Du, Y. G., Clark, L. A., & Chan, A. H. C. (2005a). Residual capacity of corroded reinforcing bars. *Magazine of Concrete Research, 57*(3), 135–147. https://doi.org/10.1680/macr.57.3.135.60482",
  "Du, Y. G., Clark, L. A., & Chan, A. H. C. (2005b). Effect of corrosion on ductility of reinforcing bars. *Magazine of Concrete Research, 57*(7), 407–419. https://doi.org/10.1680/macr.2005.57.7.407",
  "Efron, B. (1979). Bootstrap methods: Another look at the jackknife. *The Annals of Statistics, 7*(1), 1–26. https://doi.org/10.1214/aos/1176344552",
  "European Committee for Standardization. (2004). *Eurocode 2: Design of concrete structures, Part 1-1: General rules and rules for buildings* (EN 1992-1-1:2004). European Committee for Standardization.",
  "Fan, W., & Qiao, P. (2011). Vibration-based damage identification methods: A review and comparative study. *Structural Health Monitoring, 10*(1), 83–111. https://doi.org/10.1177/1475921710365419",
  "Kapteyn, M. G., Pretorius, J. V. R., & Willcox, K. E. (2021). A probabilistic graphical model foundation for enabling predictive digital twins at scale. *Nature Computational Science, 1*(5), 337–347. https://doi.org/10.1038/s43588-021-00069-0",
  "Knaack, A. M., & Kurama, Y. C. (2018). Modeling time-dependent deformations: Application for reinforced concrete beams with recycled concrete aggregates. *ACI Structural Journal, 115*(1), 175–190. https://doi.org/10.14359/51701153",
  "Maeck, J., & De Roeck, G. (2003). Damage assessment using vibration analysis on the Z24-Bridge. *Mechanical Systems and Signal Processing, 17*(1), 133–142. https://doi.org/10.1006/mssp.2002.1550",
  "McKay, M. D., Beckman, R. J., & Conover, W. J. (1979). A comparison of three methods for selecting values of input variables in the analysis of output from a computer code. *Technometrics, 21*(2), 239–245. https://doi.org/10.1080/00401706.1979.10489755",
  "McKenna, F. (2011). OpenSees: A framework for earthquake engineering simulation. *Computing in Science & Engineering, 13*(4), 58–66. https://doi.org/10.1109/MCSE.2011.66",
  "Musiał, M., Trapko, T., & Grosel, J. (2021). Static and dynamic stiffness of reinforced concrete beams strengthened with externally bonded CFRP strips. *Materials, 14*(4), 910. https://doi.org/10.3390/ma14040910",
  "Ozturkoglu, O., Yucel, U., Karademir, C., & Durmazgezer, E. (2024). An experimental study on the effect of GFRP and CFRP strengthening on the static and dynamic behavior of R/C beams under progressive damage. *Applied Sciences, 14*(21), 9920. https://doi.org/10.3390/app14219920",
  "Park, Y.-J., & Ang, A. H.-S. (1985). Mechanistic seismic damage model for reinforced concrete. *Journal of Structural Engineering, 111*(4), 722–739. https://doi.org/10.1061/(ASCE)0733-9445(1985)111:4(722)",
  "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830. https://dl.acm.org/doi/10.5555/1953048.2078195",
  "Peeters, B., & De Roeck, G. (2001). One-year monitoring of the Z24-Bridge: Environmental effects versus damage events. *Earthquake Engineering & Structural Dynamics, 30*(2), 149–171. https://doi.org/10.1002/1096-9845(200102)30:2<149::AID-EQE1>3.0.CO;2-Z",
  "Pesaru, S. A. R., Patlola, S. R., & Murari, B. R. (2026a). *StrucIQ Beam Damage and Retrofit Dataset* (Version 1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23769960",
  "Pesaru, S. A. R., Patlola, S. R., & Murari, B. R. (2026b). *StrucIQ: Digital twin for live condition monitoring and retrofit decision support of reinforced concrete members* [Computer software]. GitHub. https://github.com/SreekarAditya/BE-Major-Project",
  "Pešić, N., Živanović, S., Dennis, J., & Hargreaves, J. (2015). Experimental and finite element dynamic analysis of incrementally loaded reinforced concrete structures. *Engineering Structures, 103*, 15–27. https://doi.org/10.1016/j.engstruct.2015.07.037",
  "Picandet, V., Khelidj, A., & Bastian, G. (2001). Effect of axial compressive damage on gas permeability of ordinary and high-performance concrete. *Cement and Concrete Research, 31*(11), 1525–1532. https://doi.org/10.1016/S0008-8846(01)00546-4",
  "Saltelli, A., Annoni, P., Azzini, I., Campolongo, F., Ratto, M., & Tarantola, S. (2010). Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index. *Computer Physics Communications, 181*(2), 259–270. https://doi.org/10.1016/j.cpc.2009.09.018",
  "Sobol, I. M. (2001). Global sensitivity indices for nonlinear mathematical models and their Monte Carlo estimates. *Mathematics and Computers in Simulation, 55*(1–3), 271–280. https://doi.org/10.1016/S0378-4754(00)00270-6",
  "Spacone, E., Filippou, F. C., & Taucer, F. F. (1996). Fibre beam–column model for non-linear analysis of R/C frames: Part I. Formulation. *Earthquake Engineering & Structural Dynamics, 25*(7), 711–725. https://doi.org/10.1002/(SICI)1096-9845(199607)25:7<711::AID-EQE576>3.0.CO;2-9",
  "Teng, J. G., Smith, S. T., Yao, J., & Chen, J. F. (2003). Intermediate crack-induced debonding in RC beams and slabs. *Construction and Building Materials, 17*(6–7), 447–462. https://doi.org/10.1016/S0950-0618(03)00043-6",
  "Torzoni, M., Tezzele, M., Mariani, S., Manzoni, A., & Willcox, K. E. (2024). A digital twin framework for civil engineering structures. *Computer Methods in Applied Mechanics and Engineering, 418*, 116584. https://doi.org/10.1016/j.cma.2023.116584",
];
const refBlock = [
  H1("REFERENCES"),
  ...refs.map(r => new Paragraph({ children: runs(r.replace(/(https?:\/\/)(\S+)/g, (m, p, u) => p + u.replace(/([\/.):;])/g, "$1\u200B")), { size: 24 }), alignment: AlignmentType.JUSTIFIED,
    indent: { left: 480, hanging: 480 }, spacing: { after: 0, line: 360 } })),
];

const annex = [
  H1pb("ANNEXURE"),
  H2("Table A-1: Ranges of the Design-Space Population"),
  P("The model of Step 2 was applied across the range of beams found in buildings to build an open dataset (Pesaru et al., 2026a). Ten thousand simply supported beams were sampled by Latin hypercube sampling, which spreads the samples evenly over all inputs at once (McKay et al., 1979), within the ranges of Table A-1. Each beam was taken through five damage stages at 0.43, 0.62, 0.80, 0.89 and 1.00 times its hand-calculated first-yield load. After each stage it was unloaded and given a diagnostic and a service load cycle, and its first three frequencies, residual deflection, steel stress and strain, neutral axis depth and crack width (IS 456:2000 Annex F) were recorded; a final push to span/100 gave the peak load and the load-deflection curve."),
  tcaption("**Table A-1.** Ranges of the design-space population (10,000 beams)"),
  tableBook(["Variable", "Range"], [
    ["Span", "2.0 to 6.0 m"],
    ["Width; span to effective depth", "200 to 300 mm; 10 to 16 (overall depth 250 to 600 mm)"],
    ["Clear cover", "25 to 40 mm, with 8 mm stirrups"],
    ["Tension steel", "IS 456:2000 minimum to 95% of the under-reinforced limit; bars of 12 to 25 mm in one layer"],
    ["Concrete and steel grades", "M20 to M40; Fe415 and Fe500; properties sampled as in Table 3 of Chapter 3"],
    ["Loading", "Half four-point bending, half uniformly distributed"],
  ], [3000, 6026]),
  P("Because cracks close during part of each vibration cycle, the frequency that a vibration test would measure was computed with the breathing-crack relation f = 2 f_{open} f_{closed} / (f_{open} + f_{closed}), where f_{open} is the frequency of the cracked beam and f_{closed} that of the undamaged beam; no parameter was fitted. A measurement layer then added one simulated instrument reading to each stage: frequency with 0.5% scatter and a concrete temperature of 15 to 40 °C (−0.2% per °C), deflection with 0.01 mm plus 0.5% scatter, and crack width with 0.01 mm scatter. Two benchmark tasks were defined on these readings, estimating the stiffness left and detecting whether the steel has yielded, each tested on randomly held-out beams and on beams larger than any used for training."),
  P("Five condition stages were added. Strengthening was simulated on 1,000 beams by adding laminate, steel plate or concrete jacket elements after the fourth damage stage, stress-free at installation. Corrosion of the longitudinal bars at 5%, 10% and 15% mass loss was represented on 2,000 beams through the bar area, the yield strength and ductility of corroded bars (Du et al., 2005a, 2005b) and the strength of the cracked cover concrete (Coronelli & Gambarova, 2004); loss of bond was not represented. Fifty years of sustained service load were simulated on 1,000 beams with a time-dependent concrete model (Knaack & Kurama, 2018) using the IS 456:2000 creep coefficient of 1.6 and shrinkage strain of 0.0003. The fatigue life of the tension steel under repeated service loading was estimated from the computed stress range with the S–N curve (stress range against cycles to failure) of EN 1992-1-1 (European Committee for Standardization, 2004). Finally, 40 beams were reanalysed with a plane-stress continuum model as an independent cross-check. Every failed run and numerical anomaly was kept in the dataset and flagged."),

  H2("Table A-2: Stiffness Left and Vibration Fraction by Damage Stage"),
  P("Of the 10,000 beams, 9,934 completed at least three damage stages; the 66 failed runs and all flagged anomalies are kept in the dataset. Vibration again registered only a fraction of the static stiffness loss, and the fraction rose with damage, from 0.48 at the first stage to 0.62 at the last (medians; Table A-2 and Figure A-1). On the beams of Musiał et al. (2021), the breathing-crack relation predicted 76% vibration stiffness left against 78% and 83% measured, and a fraction of 0.44 against 0.42. The fraction therefore depends on the beam and on the damage level: 0.31 to 0.39 in the published tests used for the specimen and 0.48 to 0.62 across the design space. In every case vibration under-reports the loss, which extends H2, that vibration over-estimates the stiffness of a cracked beam, across the design space. In about 3% of stage records the unloaded frequency barely changed although the static stiffness fell; these appear along the horizontal axis of Figure A-1 and come from the way the model unloads cracked concrete."),
  tcaption("**Table A-2.** Stiffness left and vibration fraction by damage stage (medians, 10,000 beams)"),
  tableBook(["Stage", "Load / first-yield load", "Static stiffness left", "Vibration stiffness left", "Fraction registered by vibration", "Service crack width (mm)"], [
    ["1", "0.43", "0.83", "0.93", "0.48", "0.02"],
    ["2", "0.62", "0.58", "0.78", "0.54", "0.06"],
    ["3", "0.80", "0.43", "0.67", "0.58", "0.09"],
    ["4", "0.89", "0.39", "0.64", "0.60", "0.11"],
    ["5", "1.00", "0.36", "0.60", "0.62", "0.12"],
  ], [800, 1500, 1600, 1700, 1800, 1626]),
  P("With one noisy instrument reading per stage, a gradient-boosting model (an ensemble of decision trees) estimated the stiffness left with a mean absolute error of 2.9 percentage points when the undamaged frequency of the same beam was known and 4.3 points when it was not, against 19.9 and 27.9 points for reading the vibration result directly as stiffness. On beams larger than any used in training, the errors were 3.0 and 4.6 points, and yielded steel was detected with a balanced accuracy of 0.89 (0.94 on randomly held-out beams)."),
  H2("Figures A-1 and A-2: Vibration Against Static Loss, and Long-Term Deflection"),
  P("Figure A-1 plots the vibration stiffness loss against the static stiffness loss of every reached damage stage, with the median of each stage; Figure A-2 shows how the midspan deflection grows under 50 years of sustained load, relative to its value just after loading."),
  figPair("f47_static_vib.png", "f48_sustained.png",
    "**Figure A-1.** Static against vibration stiffness loss, 10,000 beams",
    "**Figure A-2.** Growth of deflection under sustained load (median and 5th to 95th percentile)"),
  H2("Table A-3: Condition Stages of the Design-Space Dataset"),
  P("Table A-3 summarises the condition stages. Strengthening simulated in the model raised the peak load by a median of 18% with laminates, 36% with a steel plate and 44% with a concrete jacket; on the strengthened beams of Musiał et al. (2021) the same approach predicted 79.4 and 105.9 kN against 90.2 and 116.0 kN tested, 9% to 12% on the safe side. Corrosion of 5%, 10% and 15% reduced the peak load to 0.91, 0.84 and 0.78 of the uncorroded beam, and only 32%, 12% and 4% of corroded beams could still carry the last stage load, against 79% uncorroded. Under sustained service load the deflection grew by a median of 2.7 times in 50 years (Figure A-2), 0.90 of the IS 456:2000 Annex C estimate, while the crack width grew from 0.02 to 0.09 mm. The design fatigue life of the tension steel fell from about 4 × 10^{10} cycles at the first stage to 0.9 × 10^{6} at the last."),
  tcaption("**Table A-3.** Condition stages of the design-space dataset"),
  tableBook(["Stage", "Runs", "Main result (median)", "Check"], [
    ["Strengthening", "1,000 beams × 3 schemes", "Peak-load gain: laminates 18%, plate 36%, jacket 44%", "Musiał et al. (2021) strengthened beams: 9% to 12% on the safe side"],
    ["Corrosion", "2,000 beams × 3 levels", "Peak load 0.91, 0.84, 0.78 of uncorroded at 5%, 10%, 15% mass loss", "At zero corrosion it reproduces the main model"],
    ["Sustained load", "1,000 beams × 2 cases", "50-year deflection 2.69 times (service) and 1.53 times (after overload) the initial value", "0.90 of the IS 456:2000 Annex C estimate"],
    ["Fatigue", "All reached stages", "Design life 4 × 10^{10} cycles at stage 1 to 0.9 × 10^{6} at stage 5", "Code estimate (EN 1992-1-1)"],
    ["Continuum check", "40 beams", "First frequency 0.96 of the fibre model; deflection after cracking 1.36 to 1.93 times larger", "Fibre deflections are a lower bound for short or deep beams"],
  ], [1500, 1700, 3200, 2626]),
  P("The continuum model agreed with the fibre model on the undamaged frequency but gave larger deflections after cracking, because it represents shear deformation and diagonal cracking, which the flexure-only fibre model omits. For short or deep beams, the cracked-state deflections of the fibre model should therefore be read as a lower bound."),
  H2("Table A-4: Mesh Convergence and Independent Elastic Check"),
  P("The nominal specimen was analysed with 12, 24 and 48 force-based elements, and its elastic response was recomputed in STAAD.Pro with the gross section and with the section transformed for the bars. The results are in Table A-4. The mesh does not change the response, so 24 elements were kept, and the fibre-model frequency is within 3% of the transformed-section value."),
  tcaption("**Table A-4.** Mesh convergence and independent elastic check of the specimen"),
  tableBook(["Check", "Quantity", "Value"], [
    ["Fibre model, 12 / 24 / 48 elements", "First frequency; cracking load; peak load", "52.1 Hz; 36.6 kN; 86.7 kN (identical for all three meshes)"],
    ["STAAD.Pro, gross section", "First frequency", "49.0 Hz"],
    ["STAAD.Pro, transformed section", "First frequency", "50.7 Hz (fibre model 2.7% higher)"],
    ["STAAD.Pro, 70 kN total load", "Midspan moment", "35.0 kN·m, equal to the hand value P·a/2"],
  ], [3000, 2800, 3226]),
  H2("Table A-5: Capacities of the Supporting Published Programme"),
  P("For Ozturkoglu et al. (2024), the capacities of the strengthened beams were predicted from the reported materials (Table A-5). The ultimate loads agree within 3%; the yield loads are under-predicted by 16% to 18%, because the steel properties had to be taken from nominal values in the absence of reported coupon tests. For Pešić et al. (2015), static peak and residual deflections were not published for four of the five beams, measured cracking loads and tensile properties were absent, and the reported bar depth was inconsistent, so no blind model was built; for the one beam with paired data, vibration registered about 0.18 of the static stiffness loss."),
  tcaption("**Table A-5.** Predicted and measured capacities, Ozturkoglu et al. (2024)"),
  tableBook(["Beam", "Quantity", "Predicted (kN)", "Measured (kN)", "Predicted / measured"], [
    ["Glass fibre, strengthened before damage", "Ultimate load", "50.6", "51.9", "0.97"],
    ["Carbon fibre, strengthened before damage", "Ultimate load", "64.0", "66.2", "0.97"],
    ["Glass fibre, strengthened before damage", "Yield load", "40.1", "49.2", "0.82"],
    ["Carbon fibre, strengthened before damage", "Yield load", "48.8", "58.1", "0.84"],
    ["Glass and carbon fibre, strengthened after damage", "Ultimate load", "48.5 to 64.2", "", "0.97 to 1.02"],
  ], [3000, 1500, 1500, 1500, 1526]),
  H2("Table A-6: Planned Instrumentation of the Part 2 Beam Tests"),
  P("The Part 2 beams are instrumented so that every reading the twin uses arrives automatically, with no manual entry. The sensors measure the same quantities as the simulated instrument readings of the dataset (load, deflection, acceleration, crack width and temperature), so the twin, which now runs on simulated readings, can switch to real readings without other changes. The instrumentation budget is about Rs. 20,000 to 30,000, so low-cost sensors are used, and the load is read from the load cell of the laboratory loading frame (Table A-6)."),
  tcaption("**Table A-6.** Planned instrumentation of the Part 2 beam tests"),
  tableBook(["Quantity", "Sensor", "Location", "Requirement", "Use in the twin"], [
    ["Load", "Load cell of the servo-hydraulic loading frame, through a steel spreader beam", "Two equal loads at the third points", "0.1 kN", "Stage loads; stiffness from load and deflection"],
    ["Midspan deflection", "Displacement sensor (linear potentiometer or linear variable differential transformer)", "Soffit at midspan", "0.01 mm", "Deflection stiffness; permanent set after unloading"],
    ["Support movement", "Two displacement sensors", "Over each support", "0.01 mm", "Removes support and setup movement from the midspan deflection"],
    ["Acceleration", "Low-noise digital micro-electro-mechanical accelerometer (ADXL355 class)", "Quarter span, away from the nodes of the first two modes", "Sampling at 2,000 Hz or more (first frequency about 52 Hz)", "Natural frequency after each damage stage"],
    ["Excitation", "Automatic tapper driven by the microcontroller", "Marked point on the top face", "Same tap in every test", "Repeatable free vibration"],
    ["Crack width", "Camera (5-megapixel ESP32 camera board, upgraded if the pilot test needs it) on a motorised rail, with printed scale markers", "Bottom strip of the front face along the constant-moment zone", "Checked on a printed target with lines 0.1 to 1.0 mm wide", "Crack width against the 0.3 mm limit of IS 456:2000"],
    ["Temperature", "Digital temperature sensor", "Beam surface", "0.5 °C", "Corrects the frequency for temperature"],
    ["Logging and transfer", "ESP32 microcontroller with a 4G mobile data module", "Beside the beam", "Common time stamp on all channels", "Sends readings and images to the cloud database"],
  ], [1650, 2300, 1700, 1600, 1776]),
  P("The microcontroller logs all sensors, triggers the tapper and the crack scan, and sends readings and images over the mobile network to a cloud database (PostgreSQL on Supabase), so the data reach the team without a computer in the laboratory. Crack widths are measured from the images in Python with OpenCV: each crack is found, its centre line traced and its width measured in millimetres from the scale markers; this crack finder is to be replaced by a segmentation network trained on public images of cracked concrete. The twin runs in the cloud on these readings, and a dashboard shows the stiffness estimate with its bounds and sends alerts to phones. The cloud database and the twin are built and already run on simulated readings; the sensors, the data link, the crack measurement and the dashboard are planned."),
  P("Each beam is first given a reference test at 15 kN, below its cracking load, which gives the initial stiffness from deflection and the natural frequency from a tap test. It is then taken through the damage stages. Before each 30 kN service check the twin predicts the deflection; the beam is then loaded to 30 kN, which is below the previous maximum load, the deflection is measured, the camera scans the constant-moment zone during the hold, and the twin is updated. The repair decision follows the rule of Table 7; the beam is strengthened after the 65 kN stage and finally loaded to failure in displacement control."),
];
const tail = [
  H1("CHAPTER 6: WORK PROGRESS"),
  P("Part 1 is complete: the beam model, the 300-beam Monte Carlo simulation, the blind validation and the 10,000-beam retrofit simulation were presented at Review 2 on 14 October 2026. Since then, the model has been extended to the 10,000-beam design-space dataset with strengthening, corrosion, sustained-load and fatigue stages; the dataset has been published on Zenodo and a research article has been submitted (Chapter 7). All code and results are maintained in the project repository (Pesaru et al., 2026b). Part 2 covers specimen casting, sensor installation and live monitoring (planned instrumentation in the Annexure, Table A-6), damage and failure tests, and validation of the twin on our own beams (Figure 7)."),
  fig("f61_gantt.png", 6.2),
  caption("**Figure 7.** Gantt chart of the project, July 2026 to April 2027."),
  H1("CHAPTER 7: ACHIEVEMENTS"),
  tcaption("**Table 8.** Achievements of Part 1"),
  table(["No.", "Type", "Achievement", "Date", "Proof"], [
    ["1", "Open-source contribution", "StrucIQ Beam Damage and Retrofit Dataset, version 1.0, published on Zenodo as an open dataset with code (CC BY 4.0). 10,000 simulated beams with staged damage, vibration and crack width, plus strengthening, corrosion and sustained-load stages, validated against published tests", "29 October 2026", "Zenodo record, DOI 10.5281/zenodo.23769960"],
    ["2", "Article", "Research article \u201cRelationship between static and dynamic stiffness loss in cracked reinforced concrete beams: a simulation study\u201d submitted to the Journal of Building Pathology and Rehabilitation (Springer, Scopus-indexed)", "29 October 2026", "Springer Nature submission acknowledgement, submission ID 10539f99-9693-4f56-8eb2-f3aa50b569a2"],
  ], [500, 1400, 3300, 1200, 2626]),
];

const font = { default: { document: { run: { font: FONT, size: 24 } } },
  paragraphStyles: [
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, font: FONT }, paragraph: { outlineLevel: 0 } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, font: FONT }, paragraph: { outlineLevel: 1 } },
  ] };
const numbering = { config: ["nums", "concl"].map(ref => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 480, hanging: 360 } } } }] })) };
const pgBd = { style: BorderStyle.THICK_THIN_SMALL_GAP, size: 24, color: "000000", space: 24 };
const page = { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1300, left: 1440, right: 1440, footer: 760 },
  borders: { pageBorders: { display: PageBorderDisplay.ALL_PAGES, offsetFrom: PageBorderOffsetFrom.PAGE, zOrder: PageBorderZOrder.FRONT },
    pageBorderTop: pgBd, pageBorderBottom: { ...pgBd, style: BorderStyle.THIN_THICK_SMALL_GAP }, pageBorderLeft: pgBd, pageBorderRight: { ...pgBd, style: BorderStyle.THIN_THICK_SMALL_GAP } } };
const footerR = new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT], size: 22 })] })] });

const doc = new Document({
  creator: "Team 120ABR", title: TITLE, styles: font, numbering,
  sections: [
    { properties: { page }, footers: { default: new Footer({ children: [] }) }, children: [...titlePage] },
    { properties: { page: { ...page, pageNumbers: { start: 1, formatType: NumberFormat.LOWER_ROMAN } } }, footers: { default: footerR },
      children: [...declaration, pb(), ...certificate, pb(), ...ack, pb(), ...abstract, pb(), ...toc, pb(), ...lof, pb(), ...lot, pb(), ...nom] },
    { properties: { page: { ...page, pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } }, footers: { default: footerR },
      children: [...body, ...tail, ...refBlock, ...annex] },
  ],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync("StrucIQ_Project_Part1_Report.docx", b); console.log("written"); });
