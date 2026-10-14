const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/root/.claude/skills/synced/c1d9558c-6b6c-4c09-9cb0-76e933c2b22f_1d389a5b-978e-4fd8-9f28-adc93546138a/pptx/scripts/apply_theme.js");

const S = "/tmp/claude-0/-home-claude/15e5c575-4bc2-5e5d-a718-921731165384/scratchpad";
const FIG = S + "/s230/";
const BANNER = S + "/ppt/abs_img_27.png"; // 1600 x 290
const LOGO = S + "/ppt/abs_img_28.png";   // 493 x 644
const BR = 1600 / 290;

const THEME = {
  name: "CBIT Review", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: "222222", lt1: "FFFFFF", dk2: "8E1B2E", lt2: "F6EFF0", accent1: "8E1B2E", accent2: "2E6B35", accent3: "8C6A22", accent4: "5B6770", accent5: "C9A9AE", accent6: "A9C8AC", hlink: "2E6B35", folHlink: "5B6770" },
};
const MAROON = "8E1B2E", GREEN = "2E6B35", GOLD = "8C6A22", GREY = "5B6770", TEXT = "222222";
const TINT = "F6EFF0", GTINT = "EEF4EE", LGREY = "D9D9D9";
const F = 26; // body font size everywhere

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Calibri", bodyFontFace: "Calibri" };
pres.title = "Digital Twin for Live Condition Monitoring and Retrofit Decision Support of Reinforced Concrete Members";
pres.author = "Batch 120ABR, CBIT";

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: "FFFFFF" },
  objects: [
    { image: { path: LOGO, x: 12.33, y: 0.3, w: 0.61, h: 0.8 } },
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.35, w: 11.6, h: 0.75, fontFace: "Calibri", fontSize: 32, bold: true, color: MAROON, align: "left", valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.33, y: 7.0, w: 0.5, h: 0.3, fontFace: "Calibri", fontSize: 14, color: GREY, align: "right" },
});
pres.defineSlideMaster({ title: "TITLE", background: { color: "FFFFFF" }, objects: [] });

function content(title, section) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  return s;
}
function tb(s, text, o) { s.addText(text, Object.assign({ isTextBox: true, fontFace: "Calibri", color: TEXT, fontSize: F, margin: 0 }, o)); }
function card(s, x, y, w, h, fill) { s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: fill } }); }
function circleNum(s, n, x, y, d, fill) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
  tb(s, String(n), { x, y, w: d, h: d, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
}
function bullets(s, items, o) {
  tb(s, items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })), Object.assign({ paraSpaceAfter: 10, valign: "top" }, o));
}
const AR = { "fig_specimen.png": 2.692, "fig_analytical_vs_simulation.png": 1.7, "fig_fe_stress_contours.png": 1.875, "fig_fe_crack_pattern.png": 1.959, "fig_damage_stages.png": 2.791, "fig_twin_prediction.png": 2.8, "fig_retrofit_comparison.png": 3.256, "fig_model_3d.png": 2.6 };
function fig(s, file, x, y, w) { const h = w / AR[file]; s.addImage({ path: FIG + file, x, y, w, h }); return h; }
function table(s, rows, o) {
  s.addTable(rows.map((r, i) => r.map((c) => ({ text: c, options: { bold: i === 0, color: i === 0 ? "FFFFFF" : TEXT, fill: { color: i === 0 ? MAROON : (i % 2 ? "FFFFFF" : TINT) } } }))),
    Object.assign({ fontFace: "Calibri", fontSize: F, valign: "middle", border: { type: "solid", pt: 0.5, color: LGREY }, margin: [0, 0.12, 0, 0.12] }, o));
}
function statCards(s, y, items, h) {
  const n = items.length, gap = 0.25, w = (12.33 - gap * (n - 1)) / n;
  items.forEach(([v, l], i) => {
    const x = 0.5 + i * (w + gap), last = i === n - 1;
    card(s, x, y, w, h, last ? GTINT : TINT);
    tb(s, [{ text: v, options: { bold: true, color: last ? GREEN : MAROON, breakLine: true } }, { text: l, options: { color: GREY } }], { x, y, w, h, align: "center", valign: "middle" });
  });
}

// 1. Title
pres.addSection({ title: "Title" });
{
  const s = pres.addSlide({ masterName: "TITLE", sectionTitle: "Title" });
  const w = 11.0, h = w / BR;
  s.addImage({ path: BANNER, x: (13.333 - w) / 2, y: 0.25, w, h });
  tb(s, "Department of Civil Engineering  |  Major Project Review 2", { x: 0.5, y: 2.35, w: 12.33, h: 0.5, color: GOLD, bold: true, align: "center" });
  tb(s, "Digital Twin for Live Condition Monitoring and Retrofit Decision Support of Reinforced Concrete Members", { x: 0.8, y: 2.95, w: 11.73, h: 1.25, fontSize: 32, bold: true, color: MAROON, align: "center", valign: "middle" });
  card(s, 0.5, 4.45, 6.6, 2.35, TINT);
  card(s, 7.33, 4.45, 5.5, 2.35, GTINT);
  tb(s, [
    { text: "Submitted by", options: { bold: true, color: MAROON, breakLine: true } },
    { text: "P. Sahasra Reddy (160123732015)", options: { breakLine: true } },
    { text: "M. Bhagirath Reddy (160123732046)", options: { breakLine: true } },
    { text: "P. Sreekar Aditya Reddy (160123732048)" },
  ], { x: 0.75, y: 4.45, w: 6.2, h: 2.35, valign: "middle" });
  tb(s, [
    { text: "Guide", options: { bold: true, color: GREEN, breakLine: true } },
    { text: "Dr. A. Balaji Rao", options: { bold: true, breakLine: true } },
    { text: "Associate Professor, CED", options: { breakLine: true } },
    { text: "Batch 120ABR  |  14-10-2026", options: { color: GREY } },
  ], { x: 7.58, y: 4.45, w: 5.1, h: 2.35, valign: "middle" });
}

// 2. Contents
pres.addSection({ title: "Contents" });
{
  const s = content("Contents", "Contents");
  ["Objectives", "Methodology", "Preliminary Results", "Summary", "References", "Work Done and Work to Be Done", "Gantt Chart"].forEach((t, i) => {
    const y = 1.55 + i * 0.75;
    circleNum(s, i + 1, 0.6, y, 0.58, i % 2 ? GREEN : MAROON);
    tb(s, t, { x: 1.4, y, w: 5.6, h: 0.58, valign: "middle" });
  });
  fig(s, "fig_model_3d.png", 7.2, 2.6, 5.6);
}

// 3. Objectives
pres.addSection({ title: "Objectives" });
{
  const s = content("Objectives", "Objectives");
  ["Record load, deflection, vibration and temperature live", "Estimate beam stiffness after each damage stage", "Predict deflection and validate it with tests", "Detect loading, lasting change and sensor faults", "Recommend and verify the best repair scheme"].forEach((t, i) => {
    const y = 1.6 + i * 1.05;
    card(s, 0.5, y, 12.33, 0.85, i % 2 ? GTINT : TINT);
    circleNum(s, i + 1, 0.7, y + 0.11, 0.63, i % 2 ? GREEN : MAROON);
    tb(s, t, { x: 1.6, y, w: 11.0, h: 0.85, valign: "middle" });
  });
  s.addNotes("1 Sensing: low-cost sensors on IS 456 beams. 2 Condition: flexural stiffness with uncertainty by Bayesian updating. 3 Prediction: deflection for any applied load from the updated stiffness. 4 Alerts: automatic, sent to phones. 5 Retrofit: concrete jacketing, steel plate bonding and fibre-reinforced polymer against a target agreed with the guide, verified by failure tests.");
}

// 4. Methodology flowchart
pres.addSection({ title: "Methodology" });
{
  const s = content("Methodology", "Methodology");
  const xs = [0.75, 4.97, 9.19], bw = 3.4, bh = 0.95;
  const box = (x, y, t, c) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: bw, h: bh, rectRadius: 0.1, fill: { color: c }, line: { color: c } });
    tb(s, t, { x, y, w: bw, h: bh, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  };
  const harrow = (x, y, left) => s.addShape(left ? pres.shapes.LEFT_ARROW : pres.shapes.RIGHT_ARROW, { x, y: y + bh / 2 - 0.18, w: 0.55, h: 0.36, fill: { color: GREY }, line: { color: GREY } });
  const varrow = (x, y1, y2) => s.addShape(pres.shapes.DOWN_ARROW, { x: x + bw / 2 - 0.18, y: y1, w: 0.36, h: y2 - y1, fill: { color: GREY }, line: { color: GREY } });
  const y1 = 1.6, cy = 2.9, y2 = 3.5, y3 = 5.55;
  ["Design & casting", "Sensors & cloud", "Reference test"].forEach((t, i) => box(xs[i], y1, t, MAROON));
  harrow(xs[0] + bw + 0.135, y1); harrow(xs[1] + bw + 0.135, y1);
  card(s, 0.5, cy, 12.33, 1.8, GTINT);
  tb(s, "Repeated for each damage stage", { x: 0.75, y: cy + 0.05, w: 7.5, h: 0.5, color: GREEN, bold: true, italic: true, valign: "middle" });
  ["Prediction check", "Twin update", "Damage stage"].forEach((t, i) => box(xs[i], y2, t, GREEN));
  harrow(xs[0] + bw + 0.135, y2, true); harrow(xs[1] + bw + 0.135, y2, true);
  varrow(xs[2], y1 + bh + 0.05, y2 - 0.05);
  ["Repair decision", "Strengthening", "Failure test"].forEach((t, i) => box(xs[i], y3, t, GOLD));
  harrow(xs[0] + bw + 0.135, y3); harrow(xs[1] + bw + 0.135, y3);
  varrow(xs[0], y2 + bh + 0.05, y3 - 0.05);
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
pres.addSection({ title: "Preliminary Results" });
{
  const s = content("Results: Design Calculations (IS 456)", "Preliminary Results");
  table(s, [
    ["Quantity", "Hand calculation", "Fibre model"],
    ["Cracking load", "26.5 kN", "—"],
    ["Yield load", "81 kN", "89 kN"],
    ["Peak load", "82 kN", "91 kN"],
    ["IS 456 design capacity", "70 kN", "—"],
    ["Shear capacity", "94.5 kN", "—"],
    ["First natural frequency", "50.0 Hz", "49.1 Hz"],
  ], { x: 0.5, y: 1.6, w: 12.33, colW: [5.33, 3.5, 3.5], rowH: 0.6 });
  bullets(s, ["Under-reinforced: neutral axis 45.5 mm < 120 mm", "Flexure governs: shear demand only 41.1 kN"], { x: 0.5, y: 5.95, w: 12.33, h: 1.0 });
  s.addNotes("Beam 230 x 300 mm, 3.0 m span, M30, 3 bars of 12 mm bottom, 2 of 10 mm top, 8 mm stirrups at 150 mm. Loads are total jack load in four-point bending. Design values use IS 456 partial safety factors; expected values use mean strengths.");
}

// 6. Load-deflection
{
  const s = content("Results: Load–Deflection Response", "Preliminary Results");
  fig(s, "fig_analytical_vs_simulation.png", 0.5, 1.6, 8.0);
  bullets(s, ["Hand: peak 82 kN", "Fibre model: 91 kN", "Continuum: 86 kN", "Capacity within 10%", "Frequency within 2%"], { x: 8.85, y: 1.9, w: 4.0, h: 4.5, paraSpaceAfter: 18 });
}

// 7. Stress and cracks
{
  const s = content("Results: Stress and Crack Pattern", "Preliminary Results");
  fig(s, "fig_fe_stress_contours.png", 0.5, 1.6, 6.0);
  fig(s, "fig_fe_crack_pattern.png", 6.83, 1.6, 6.0);
  bullets(s, ["Compression top, tension in bars"], { x: 0.5, y: 5.3, w: 6.0, h: 0.6 });
  bullets(s, ["Cracks between the load points"], { x: 6.83, y: 5.3, w: 6.0, h: 0.6 });
  bullets(s, ["Two-dimensional continuum model (OpenSeesPy)"], { x: 0.5, y: 6.1, w: 12.33, h: 0.6 });
}

// 8. Damage stages
{
  const s = content("Results: Damage Stages", "Preliminary Results");
  fig(s, "fig_damage_stages.png", 1.4, 1.55, 10.5);
  statCards(s, 5.55, [["49 → 33 Hz", "Frequency"], ["1.09 → 2.54 mm", "Service deflection"], ["57%", "Stiffness loss"]], 1.2);
  s.addNotes("Damage stages 35, 50, 65 and 72 kN, all below yield. Stiffness from deflection falls from about 13,100 to about 5,700 kN m^2 (43% remaining); frequency gives (33/49)^2 = 45%, a close match.");
}

// 9. Twin prediction
{
  const s = content("Results: Twin Prediction", "Preliminary Results");
  fig(s, "fig_twin_prediction.png", 1.4, 1.55, 10.5);
  statCards(s, 5.55, [["≤ 58%", "No updating"], ["≤ 8.5%", "Vibration only"], ["≤ 1%", "Static only"], ["≤ 1.2%", "Combined"]], 1.2);
  s.addNotes("Maximum error in predicting the 30 kN service deflection, made before each service cycle was run. Combined means deflection and frequency together by Bayesian updating.");
}

// 10. Repair comparison
{
  const s = content("Results: Repair Schemes", "Preliminary Results");
  fig(s, "fig_retrofit_comparison.png", 1.83, 1.5, 9.67);
  table(s, [
    ["Scheme", "Design", "Expected", "Failure"],
    ["Fibre-reinforced polymer", "107 kN", "126 kN", "Debonding"],
    ["Steel plate", "125 kN", "147 kN", "Plate yield"],
    ["Concrete jacket", "131 kN", "154 kN", "Flexure"],
  ], { x: 0.5, y: 4.62, w: 12.33, colW: [4.73, 2.4, 2.6, 2.6], rowH: 0.55 });
  s.addNotes("Standard sizes: two carbon laminates 50 x 1.2 mm (ACI 440.2R debonding strain 0.0045); flat 100 x 5 mm Fe250 plate; 75 mm jacket with 2 bars of 12 mm (IS 15988). Unstrengthened beam: design 70 kN, expected 82 kN.");
}

// 11. Summary
pres.addSection({ title: "Summary" });
{
  const s = content("Summary", "Summary");
  ["Twin loop: measure, update, predict, decide, verify", "Beam: design 70 kN, expected 82 kN", "Models agree within 10% on capacity", "Damage: frequency 49 → 33 Hz", "Twin predicts service deflection within 1.2%", "Repairs raise capacity to 126–154 kN"].forEach((t, i) => {
    const y = 1.6 + i * 0.88;
    card(s, 0.5, y, 12.33, 0.72, i % 2 ? GTINT : TINT);
    tb(s, t, { x: 0.85, y, w: 11.8, h: 0.72, valign: "middle" });
  });
}

// 12. References
pres.addSection({ title: "References" });
{
  const s = content("References", "References");
  const refs = [
    "Maeck et al. (2000), Engineering Structures, 22(10)",
    "Xu and Castel (2016), J. Sound and Vibration, 368",
    "Capozucca (2013), Composites Part B, 46",
    "Lu et al. (2005), Engineering Structures, 27(6)",
    "Kapteyn et al. (2021), Nature Comput. Science, 1(5)",
    "Torzoni et al. (2024), Comput. Methods Appl. Mech. Eng., 418",
    "IS 456:2000, IS 15988:2013, ACI 440.2R-17",
  ];
  tb(s, refs.map((r, i) => ({ text: r, options: { bullet: { type: "number" }, breakLine: i < refs.length - 1 } })), { x: 0.5, y: 1.6, w: 12.33, h: 5.3, paraSpaceAfter: 12, valign: "top" });
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
pres.addSection({ title: "Work Done and Work to Be Done" });
{
  const s = content("Work Done and Work to Be Done", "Work Done and Work to Be Done");
  card(s, 0.5, 1.55, 6.0, 5.35, GTINT);
  card(s, 6.83, 1.55, 6.0, 5.35, TINT);
  tb(s, "Work done", { x: 0.8, y: 1.65, w: 5.4, h: 0.55, bold: true, color: GREEN });
  tb(s, "Work to be done", { x: 7.13, y: 1.65, w: 5.4, h: 0.55, bold: true, color: MAROON });
  bullets(s, ["Literature review", "Methodology", "IS 456 design", "Fibre and continuum models", "Damage-stage simulation", "Twin prediction test", "Repair scheme design", "ANSYS input files"], { x: 0.8, y: 2.3, w: 5.5, h: 4.5, paraSpaceAfter: 4 });
  bullets(s, ["Sensor assembly", "Twin software and cloud", "Casting and material tests", "Pilot test", "Damage-stage tests", "Strengthening", "Failure tests", "Thesis"], { x: 7.13, y: 2.3, w: 5.5, h: 4.5, paraSpaceAfter: 4 });
}

// 14. Gantt
pres.addSection({ title: "Gantt Chart" });
{
  const s = content("Gantt Chart (2026–27)", "Gantt Chart");
  const months = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"];
  const gx = 4.75, gw = 8.08, mw = gw / months.length, top = 1.5, hh = 0.5, rh = 0.55;
  months.forEach((m, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x: gx + i * mw, y: top, w: mw, h: hh, fill: { color: i < 6 ? MAROON : GREEN }, line: { color: "FFFFFF", width: 1 } });
    tb(s, m, { x: gx + i * mw, y: top, w: mw, h: hh, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
  });
  const pos = (m, d) => gx + (m + (d - 1) / 30) * mw;
  const tasks = [
    ["Literature review", [0, 1], [3, 14], true],
    ["Design and simulation", [2, 1], [3, 14], true],
    ["Sensors and cloud", [3, 15], [5, 30], false],
    ["Casting and curing", [4, 1], [5, 15], false],
    ["Pilot and damage tests", [5, 1], [7, 15], false],
    ["Strengthening", [7, 1], [8, 15], false],
    ["Failure tests", [8, 1], [8, 30], false],
    ["Analysis and thesis", [8, 1], [9, 30], false],
  ];
  tasks.forEach(([name, a, b, done], i) => {
    const y = top + hh + i * rh;
    if (i % 2 === 0) s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y, w: 12.33, h: rh, fill: { color: "F5F5F5" }, line: { color: "F5F5F5" } });
    tb(s, name, { x: 0.6, y, w: 4.1, h: rh, valign: "middle" });
    const x1 = pos(a[0], a[1]), x2 = pos(b[0], b[1] + 1);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x1, y: y + 0.12, w: x2 - x1, h: rh - 0.24, rectRadius: 0.05, fill: { color: done ? GREEN : GOLD }, line: { color: done ? GREEN : GOLD } });
  });
  const endY = top + hh + tasks.length * rh;
  const rx = pos(3, 14);
  s.addShape(pres.shapes.LINE, { x: rx, y: top + hh, w: 0, h: endY - top - hh + 0.1, line: { color: MAROON, width: 2.5, dashType: "dash" } });
  const ly = endY + 0.25;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: ly + 0.14, w: 0.5, h: 0.28, rectRadius: 0.04, fill: { color: GREEN }, line: { color: GREEN } });
  tb(s, "Completed", { x: 1.25, y: ly, w: 2.0, h: 0.55, valign: "middle" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3.4, y: ly + 0.14, w: 0.5, h: 0.28, rectRadius: 0.04, fill: { color: GOLD }, line: { color: GOLD } });
  tb(s, "Planned", { x: 4.05, y: ly, w: 1.8, h: 0.55, valign: "middle" });
  s.addShape(pres.shapes.LINE, { x: 6.1, y: ly + 0.28, w: 0.5, h: 0, line: { color: MAROON, width: 2.5, dashType: "dash" } });
  tb(s, "Review 2 (14 Oct)", { x: 6.75, y: ly, w: 3.2, h: 0.55, valign: "middle", color: MAROON, bold: true });
  s.addNotes("Thesis submission April 2027. Casting in November allows 28-day curing before the pilot test; jacket curing (28 days) falls in February to March.");
}

// 15. Thank you
pres.addSection({ title: "Close" });
{
  const s = pres.addSlide({ masterName: "TITLE", sectionTitle: "Close" });
  const w = 11.0, h = w / BR;
  s.addImage({ path: BANNER, x: (13.333 - w) / 2, y: 0.25, w, h });
  tb(s, "Thank You", { x: 0.5, y: 3.2, w: 12.33, h: 1.1, fontSize: 54, bold: true, color: MAROON, align: "center", valign: "middle" });
  tb(s, "Batch 120ABR  |  Department of Civil Engineering", { x: 0.5, y: 4.6, w: 12.33, h: 0.6, color: GREY, align: "center", valign: "middle" });
}

(async () => {
  const out = S + "/ppt/StrucIQ_Review2_120ABR.pptx";
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("written", out);
})();
