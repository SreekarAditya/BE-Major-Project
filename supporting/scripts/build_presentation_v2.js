const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/c1d9558c-6b6c-4c09-9cb0-76e933c2b22f_1d389a5b-978e-4fd8-9f28-adc93546138a/pptx/scripts/apply_theme.js");
const S = "/tmp/claude-0/-home-claude/15e5c575-4bc2-5e5d-a718-921731165384/scratchpad/ppt/";
const BANNER = S + "abs_img_27.png", LOGO = S + "abs_img_28.png", BR = 1600 / 290;

const THEME = { name: "CBIT Minimal", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: "1A1A1A", lt1: "FFFFFF", dk2: "1A1A1A", lt2: "F2F2F2", accent1: "8E1B2E", accent2: "4A6C8C", accent3: "7A7A7A", accent4: "B0B0B0", accent5: "C9C9C9", accent6: "2E6B35", hlink: "4A6C8C", folHlink: "7A7A7A" } };
const INK = "1A1A1A", MUTED = "6B6B6B", RULE = "BFBFBF", ACC = "8E1B2E", F = 26;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Calibri", bodyFontFace: "Calibri" };
pres.title = "Digital twin for live condition monitoring and retrofit decision support of reinforced concrete members";

pres.defineSlideMaster({
  title: "CONTENT", background: { color: "FFFFFF" },
  objects: [
    { image: { path: LOGO, x: 12.38, y: 0.32, w: 0.5, h: 0.65 } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 11.5, h: 0.75, fontFace: "Calibri", fontSize: 32, bold: true, color: INK, align: "left", valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "Major project review 2  |  Batch 120ABR", options: { x: 0.6, y: 7.0, w: 6, h: 0.3, fontFace: "Calibri", fontSize: 12, color: MUTED, margin: 0 } } },
  ],
  slideNumber: { x: 12.33, y: 7.0, w: 0.5, h: 0.3, fontFace: "Calibri", fontSize: 12, color: MUTED, align: "right" },
});
pres.defineSlideMaster({ title: "TITLE", background: { color: "FFFFFF" }, objects: [] });

const content = (t, sec) => { const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec }); s.addText(t, { placeholder: "title" }); return s; };
const tb = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, fontFace: "Calibri", fontSize: F, color: INK, margin: 0 }, o));
const bullets = (s, items, o) => tb(s, items.map((t, i) => ({ text: t, options: { bullet: { indent: 22 }, breakLine: i < items.length - 1 } })), Object.assign({ paraSpaceAfter: 14, valign: "top" }, o));
const numbered = (s, items, o) => tb(s, items.map((t, i) => ({ text: t, options: { bullet: { type: "number", indent: 30 }, breakLine: i < items.length - 1 } })), Object.assign({ paraSpaceAfter: 14, valign: "top" }, o));
const rule = (s, x, y, w, c, pt) => s.addShape(pres.shapes.LINE, { x, y, w, h: 0, line: { color: c || RULE, width: pt || 1 } });
function table(s, rows, x, y, colW, rowH) {
  // minimal table: bold header, dark rules top and under header, light rules between rows
  const w = colW.reduce((a, b) => a + b, 0);
  s.addTable(rows.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: i === 0, color: i === 0 ? INK : INK, align: j === 0 ? "left" : "left",
    border: [{ type: "none" }, { type: "none" }, { type: "solid", pt: i === 0 ? 1.5 : 0.75, color: i === 0 ? INK : RULE }, { type: "none" }] } }))),
    { x, y, w, colW, rowH, fontFace: "Calibri", fontSize: F, valign: "middle", margin: [0, 0.1, 0, 0] });
  rule(s, x, y, w, INK, 1.5);
}
function chart(s, file, notes) { s.addImage({ path: S + file, x: 0.5, y: 1.45, w: 8.2, h: 5.0 }); }

// 1. Title
pres.addSection({ title: "Title" });
{
  const s = pres.addSlide({ masterName: "TITLE", sectionTitle: "Title" });
  const w = 10.4; s.addImage({ path: BANNER, x: (13.333 - w) / 2, y: 0.3, w, h: w / BR });
  tb(s, "Department of Civil Engineering  |  Major project review 2", { x: 0.6, y: 2.35, w: 12.13, h: 0.5, color: MUTED, align: "center" });
  tb(s, "Digital twin for live condition monitoring and retrofit decision support of reinforced concrete members", { x: 1.0, y: 2.95, w: 11.33, h: 1.3, fontSize: 32, bold: true, align: "center", valign: "middle" });
  rule(s, 3.67, 4.5, 6.0, RULE, 1);
  tb(s, [
    { text: "Submitted by", options: { bold: true, breakLine: true } },
    { text: "P. Sahasra Reddy (1601-23-732-015)", options: { breakLine: true } },
    { text: "M. Bhagirath Reddy (1601-23-732-046)", options: { breakLine: true } },
    { text: "P. Sreekar Aditya Reddy (1601-23-732-048)" },
  ], { x: 0.6, y: 4.75, w: 6.6, h: 2.0, valign: "top" });
  tb(s, [
    { text: "Under the guidance of", options: { bold: true, breakLine: true } },
    { text: "Dr. A. Balaji Rao", options: { breakLine: true } },
    { text: "Associate professor, CED", options: { breakLine: true } },
    { text: "Batch 120ABR  |  14-10-2026", options: { color: MUTED } },
  ], { x: 7.6, y: 4.75, w: 5.13, h: 2.0, valign: "top" });
}

// 2. Contents
pres.addSection({ title: "Contents" });
{
  const s = content("Contents", "Contents");
  numbered(s, ["Aim and objectives", "Methodology", "Preliminary results", "Summary", "References", "Work done and work to be done", "Gantt chart"], { x: 0.6, y: 1.55, w: 8, h: 5.2, paraSpaceAfter: 12 });
}

// 3. Aim and objectives
pres.addSection({ title: "Aim and objectives" });
{
  const s = content("Aim and objectives", "Aim and objectives");
  tb(s, "Aim", { x: 0.6, y: 1.45, w: 6, h: 0.5, bold: true, color: ACC });
  tb(s, "To develop and experimentally validate a digital twin that measures damage in reinforced concrete beams and recommends retrofitting", { x: 0.6, y: 1.95, w: 12.1, h: 0.95, valign: "top" });
  tb(s, "Objectives", { x: 0.6, y: 3.1, w: 6, h: 0.5, bold: true, color: ACC });
  numbered(s, ["Record load, deflection, vibration and temperature live", "Estimate beam stiffness after each damage stage", "Predict deflection and validate it with tests", "Detect loading, lasting change and sensor faults", "Recommend and verify the best repair scheme"], { x: 0.6, y: 3.62, w: 12.1, h: 3.3, paraSpaceAfter: 6 });
  s.addNotes("1 Sensing: low-cost sensors on IS 456 beams. 2 Condition: flexural stiffness with uncertainty by Bayesian updating. 3 Prediction: deflection for any applied load from the updated stiffness. 4 Alerts: automatic, sent to phones. 5 Retrofit: concrete jacketing, steel plate bonding and fibre-reinforced polymer against a target agreed with the guide, verified by failure tests.");
}

// 4. Methodology flowchart
pres.addSection({ title: "Methodology" });
{
  const s = content("Methodology", "Methodology");
  const xs = [0.75, 4.97, 9.19], bw = 3.4, bh = 0.9;
  const box = (x, y, t, strong) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: bh, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: strong ? ACC : INK, width: strong ? 2.25 : 1.25 } });
    tb(s, t, { x, y, w: bw, h: bh, bold: !!strong, color: strong ? ACC : INK, align: "center", valign: "middle" });
  };
  const arrowH = (x1, x2, y) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y, w: Math.abs(x2 - x1), h: 0, line: { color: INK, width: 1.5, beginArrowType: x2 < x1 ? "triangle" : undefined, endArrowType: x2 > x1 ? "triangle" : undefined } });
  const arrowV = (x, y1, y2) => s.addShape(pres.shapes.LINE, { x, y: y1, w: 0, h: y2 - y1, line: { color: INK, width: 1.5, endArrowType: "triangle" } });
  const y1 = 1.6, y2 = 3.6, y3 = 5.6;
  ["Design & casting", "Sensors & cloud", "Reference test"].forEach((t, i) => box(xs[i], y1, t));
  ["Prediction check", "Twin update", "Damage stage"].forEach((t, i) => box(xs[i], y2, t, true));
  ["Repair decision", "Strengthening", "Failure test"].forEach((t, i) => box(xs[i], y3, t));
  [y1, y3].forEach((y) => { arrowH(xs[0] + bw + 0.1, xs[1] - 0.1, y + bh / 2); arrowH(xs[1] + bw + 0.1, xs[2] - 0.1, y + bh / 2); });
  arrowH(xs[2] - 0.1, xs[1] + bw + 0.1, y2 + bh / 2); arrowH(xs[1] - 0.1, xs[0] + bw + 0.1, y2 + bh / 2);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: y2 - 0.6, w: 12.33, h: bh + 0.85, rectRadius: 0.1, fill: { color: "FFFFFF", transparency: 100 }, line: { color: ACC, width: 1.25, dashType: "dash" } });
  tb(s, "Repeated for each damage stage", { x: 0.75, y: y2 - 0.58, w: 7, h: 0.5, color: ACC, italic: true, valign: "middle" });
  arrowV(xs[2] + bw / 2, y1 + bh + 0.05, y2 - 0.05);
  arrowV(xs[0] + bw / 2, y2 + bh + 0.05, y3 - 0.05);
  s.addNotes([
    "Design & casting: IS 456 under-reinforced beams, 230 x 300 mm, 3.0 m span for simulation; cubes for actual strength.",
    "Sensors & cloud: accelerometer (ADXL345), deflection (linear potentiometer with ADS1115), temperature (DS18B20), load from the 500 kN frame, solenoid tapper. ESP32 sends data over 4G to a cloud database; the twin runs in the cloud; alerts go to phones.",
    "Reference test: 15 kN load gives stiffness from deflection, EI = 23PL^3/(1296 delta); tap test gives frequency, EI proportional to f squared.",
    "Damage stage: 35, 50, 65, 72 kN, below yield; cracks recorded.",
    "Twin update: Bayesian inference combines deflection and frequency estimates with the previous estimate.",
    "Prediction check: twin predicts deflection for any applied load from its fixed stiffness; checked in a 30 kN service test below the previous maximum.",
    "Repair decision: jacketing, steel plate, fibre-reinforced polymer against the target agreed with the guide. Strengthening after the 65 kN stage, then a new reference. Failure test in displacement control.",
  ].join("\n"));
}

// 5. Design calculations
pres.addSection({ title: "Preliminary results" });
{
  const s = content("Results: design calculations (IS 456)", "Preliminary results");
  table(s, [
    ["Quantity", "Hand calculation", "Fibre model"],
    ["Cracking load", "26.5 kN", "—"],
    ["Yield load", "81 kN", "89 kN"],
    ["Peak load", "82 kN", "91 kN"],
    ["IS 456 design capacity", "70 kN", "—"],
    ["Shear capacity", "94.5 kN", "—"],
    ["First natural frequency", "50.0 Hz", "49.1 Hz"],
  ], 0.6, 1.5, [5.4, 3.4, 3.33], 0.58);
  bullets(s, ["Under-reinforced: neutral axis 45.5 mm < 120 mm", "Flexure governs: shear demand only 41.1 kN"], { x: 0.6, y: 5.75, w: 12.1, h: 1.1 });
  s.addNotes("Beam 230 x 300 mm, 3.0 m span, M30, 3 bars of 12 mm bottom, 2 of 10 mm top, 8 mm stirrups at 150 mm. Loads are total jack load in four-point bending. Design values use IS 456 partial safety factors; expected values use mean strengths.");
}

// 6. Load-deflection
{
  const s = content("Results: load–deflection response", "Preliminary results");
  chart(s, "c_load_deflection.png");
  bullets(s, ["Hand: 82 kN", "Fibre model: 91 kN", "Continuum: 86 kN", "Agree within 10%"], { x: 9.1, y: 1.9, w: 3.8, h: 4.5, paraSpaceAfter: 20 });
}

// 7. Stress and cracks
{
  const s = content("Results: stress and crack pattern", "Preliminary results");
  s.addImage({ path: S + "c_stress_cracks.png", x: 0.6, y: 1.4, w: 12.1, h: 12.1 / 2.69 });
  tb(s, "Continuum model at 76 kN, approaching yield", { x: 0.6, y: 6.3, w: 12.1, h: 0.5, color: MUTED });
}

// 8. Damage stages
{
  const s = content("Results: damage stages", "Preliminary results");
  chart(s, "c_damage.png");
  bullets(s, ["Frequency 49 → 33 Hz", "Deflection: 42% left", "Frequency: 46% left", "Methods agree"], { x: 9.1, y: 1.9, w: 3.8, h: 4.5, paraSpaceAfter: 20 });
  s.addNotes("Damage stages 35, 50, 65 and 72 kN, all below yield. Stiffness from deflection under the 15 kN check load: 42% remaining after 72 kN. From frequency, (33.2/49.0)^2 = 46%. Two independent routes agree within 4 points.");
}

// 9. Twin prediction
{
  const s = content("Results: twin prediction (simulated tests)", "Preliminary results");
  chart(s, "c_twin.png");
  bullets(s, ["Predicted before test", "No updating: 58%", "Vibration only: 8.8%", "Combined: 1.3%"], { x: 9.1, y: 1.9, w: 3.8, h: 4.5, paraSpaceAfter: 20 });
  s.addNotes("Largest error in predicting the 30 kN service deflection, made before each service cycle. The 'measurements' come from the fibre model with sensor noise added, so this verifies the updating method before real tests. Combined = deflection and frequency together by Bayesian updating.");
}

// 10. Repair schemes
{
  const s = content("Results: repair schemes", "Preliminary results");
  chart(s, "c_repair.png");
  bullets(s, ["Jacket: 154 kN", "Steel plate: 147 kN", "Polymer: 126 kN", "Polymer: debonding"], { x: 9.1, y: 1.9, w: 3.8, h: 4.5, paraSpaceAfter: 20 });
  s.addNotes("Standard sizes: two carbon laminates 50 x 1.2 mm (ACI 440.2R debonding strain 0.0045); flat 100 x 5 mm Fe250 plate; 75 mm jacket with 2 bars of 12 mm (IS 15988). The twin chooses against the performance target agreed with the guide, checking flexure, shear, bond and anchorage.");
}

// 11. Summary
pres.addSection({ title: "Summary" });
{
  const s = content("Summary", "Summary");
  bullets(s, ["Twin loop: measure, update, predict, decide, verify", "Beam: design 70 kN, expected 82 kN", "Three models agree within 10%", "Damage: frequency 49 → 33 Hz", "Combined twin error within 1.3% (simulated)", "Repairs raise capacity to 126–154 kN"], { x: 0.6, y: 1.55, w: 12.1, h: 5.3, paraSpaceAfter: 16 });
}

// 12. References
pres.addSection({ title: "References" });
{
  const s = content("References", "References");
  numbered(s, [
    "Maeck et al. (2000), Engineering Structures, 22(10)",
    "Xu and Castel (2016), J. Sound and Vibration, 368",
    "Capozucca (2013), Composites Part B, 46",
    "Lu et al. (2005), Engineering Structures, 27(6)",
    "Kapteyn et al. (2021), Nature Comput. Science, 1(5)",
    "Torzoni et al. (2024), Comput. Methods Appl. Mech. Eng., 418",
    "IS 456:2000, IS 15988:2013, ACI 440.2R-17",
  ], { x: 0.6, y: 1.55, w: 12.1, h: 5.3, paraSpaceAfter: 10 });
  s.addNotes([
    "1. Maeck, J. et al. (2000). Damage identification in reinforced concrete structures by dynamic stiffness determination. Engineering Structures, 22(10), 1339-1349.",
    "2. Xu, T. and Castel, A. (2016). Modeling the dynamic stiffness of cracked reinforced concrete beams under low-amplitude vibration loads. Journal of Sound and Vibration, 368, 135-147.",
    "3. Capozucca, R. (2013). Assessment of CFRP strengthened RC beams through dynamic tests. Composites Part B: Engineering, 46, 69-80.",
    "4. Lu, X.Z., Teng, J.G., Ye, L.P. and Jiang, J.J. (2005). Bond-slip models for FRP sheets/plates bonded to concrete. Engineering Structures, 27(6), 920-937.",
    "5. Kapteyn, M.G., Pretorius, J.V.R. and Willcox, K.E. (2021). A probabilistic graphical model foundation for enabling predictive digital twins at scale. Nature Computational Science, 1(5), 337-347.",
    "6. Torzoni, M. et al. (2024). A digital twin framework for civil engineering structures. Computer Methods in Applied Mechanics and Engineering, 418, 116584.",
    "7. IS 456:2000; IS 15988:2013; ACI 440.2R-17.",
  ].join("\n"));
}

// 13. Work done / to be done
pres.addSection({ title: "Work done and work to be done" });
{
  const s = content("Work done and work to be done", "Work done and work to be done");
  tb(s, "Work done", { x: 0.6, y: 1.45, w: 5.6, h: 0.5, bold: true, color: ACC });
  tb(s, "Work to be done", { x: 6.9, y: 1.45, w: 5.8, h: 0.5, bold: true, color: ACC });
  s.addShape(pres.shapes.LINE, { x: 6.55, y: 1.5, w: 0, h: 5.2, line: { color: RULE, width: 1 } });
  bullets(s, ["Literature review", "Methodology", "IS 456 design", "Fibre and continuum models", "Damage-stage simulation", "Twin prediction test", "Repair scheme design", "ANSYS input files"], { x: 0.6, y: 2.05, w: 5.8, h: 4.8, paraSpaceAfter: 5 });
  bullets(s, ["Sensor assembly", "Twin software and cloud", "Casting and material tests", "Pilot test", "Damage-stage tests", "Strengthening", "Failure tests", "Thesis"], { x: 6.9, y: 2.05, w: 5.8, h: 4.8, paraSpaceAfter: 5 });
}

// 14. Gantt
pres.addSection({ title: "Gantt chart" });
{
  const s = content("Gantt chart (2026–27)", "Gantt chart");
  const months = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"];
  const gx = 4.85, gw = 7.98, mw = gw / months.length, top = 1.45, hh = 0.5, rh = 0.52;
  months.forEach((m, i) => {
    tb(s, m, { x: gx + i * mw, y: top, w: mw, h: hh, bold: true, align: "center", valign: "middle" });
    if (i > 0) s.addShape(pres.shapes.LINE, { x: gx + i * mw, y: top + hh, w: 0, h: 8 * rh, line: { color: "E6E6E6", width: 0.75 } });
  });
  rule(s, 0.6, top + hh, 12.23, INK, 1.5);
  const pos = (m, d) => gx + (m + (d - 1) / 30) * mw;
  const tasks = [
    ["Literature review", [0, 1], [3, 14], true], ["Design and simulation", [2, 1], [3, 14], true],
    ["Sensors and cloud", [3, 15], [5, 30], false], ["Casting and curing", [4, 1], [5, 15], false],
    ["Pilot and damage tests", [5, 1], [7, 15], false], ["Strengthening", [7, 1], [8, 15], false],
    ["Failure tests", [8, 1], [8, 30], false], ["Analysis and thesis", [8, 1], [9, 30], false],
  ];
  tasks.forEach(([name, a, b, done], i) => {
    const y = top + hh + i * rh;
    tb(s, name, { x: 0.6, y, w: 4.2, h: rh, valign: "middle" });
    const x1 = pos(a[0], a[1]), x2 = pos(b[0], b[1] + 1);
    s.addShape(pres.shapes.RECTANGLE, { x: x1, y: y + 0.15, w: x2 - x1, h: rh - 0.3, fill: { color: done ? "4D4D4D" : ACC }, line: { color: done ? "4D4D4D" : ACC } });
  });
  const endY = top + hh + tasks.length * rh;
  rule(s, 0.6, endY, 12.23, RULE, 0.75);
  const rx = pos(3, 14);
  s.addShape(pres.shapes.LINE, { x: rx, y: top + hh, w: 0, h: endY - top - hh, line: { color: INK, width: 1.5, dashType: "dash" } });
  const ly = endY + 0.2;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: ly + 0.16, w: 0.45, h: 0.22, fill: { color: "4D4D4D" }, line: { color: "4D4D4D" } });
  tb(s, "Completed", { x: 1.15, y: ly, w: 2.0, h: 0.55, valign: "middle" });
  s.addShape(pres.shapes.RECTANGLE, { x: 3.4, y: ly + 0.16, w: 0.45, h: 0.22, fill: { color: ACC }, line: { color: ACC } });
  tb(s, "Planned", { x: 3.95, y: ly, w: 1.8, h: 0.55, valign: "middle" });
  s.addShape(pres.shapes.LINE, { x: 6.0, y: ly + 0.27, w: 0.45, h: 0, line: { color: INK, width: 1.5, dashType: "dash" } });
  tb(s, "Review 2 (14 Oct)", { x: 6.6, y: ly, w: 3.3, h: 0.55, valign: "middle" });
  s.addNotes("Thesis submission April 2027. Casting in November allows 28-day curing before the pilot test; jacket curing (28 days) falls in February to March.");
}

// 15. Thank you
pres.addSection({ title: "Close" });
{
  const s = pres.addSlide({ masterName: "TITLE", sectionTitle: "Close" });
  const w = 10.4; s.addImage({ path: BANNER, x: (13.333 - w) / 2, y: 0.3, w, h: w / BR });
  tb(s, "Thank you", { x: 0.6, y: 3.3, w: 12.13, h: 1.1, fontSize: 54, bold: true, align: "center", valign: "middle" });
  tb(s, "Batch 120ABR  |  Department of Civil Engineering", { x: 0.6, y: 4.6, w: 12.13, h: 0.6, color: MUTED, align: "center", valign: "middle" });
}

(async () => {
  const out = S + "StrucIQ_Review2_120ABR_v2.pptx";
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("written", out);
})();
