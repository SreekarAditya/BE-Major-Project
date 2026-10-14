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
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 11.6, h: 0.75, fontFace: "Calibri", fontSize: 32, bold: true, color: INK, align: "left", valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "Major project review 2  |  Batch 120ABR", options: { x: 0.6, y: 7.0, w: 6, h: 0.3, fontFace: "Calibri", fontSize: 12, color: MUTED, margin: 0 } } },
  ],
  slideNumber: { x: 12.33, y: 7.0, w: 0.5, h: 0.3, fontFace: "Calibri", fontSize: 12, color: MUTED, align: "right" },
});
pres.defineSlideMaster({ title: "TITLE", background: { color: "FFFFFF" }, objects: [] });

const content = (t, sec) => { const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: sec }); s.addText(t, { placeholder: "title" }); return s; };
const tb = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, fontFace: "Calibri", fontSize: F, color: INK, margin: 0 }, o));
const bullets = (s, items, o) => tb(s, items.map((t, i) => ({ text: t, options: { bullet: { indent: 22 }, breakLine: i < items.length - 1 } })), Object.assign({ paraSpaceAfter: 12, valign: "top" }, o));
const numbered = (s, items, o) => tb(s, items.map((t, i) => ({ text: t, options: { bullet: { type: "number", indent: 32 }, breakLine: i < items.length - 1 } })), Object.assign({ paraSpaceAfter: 10, valign: "top" }, o));
const rule = (s, x, y, w, c, pt) => s.addShape(pres.shapes.LINE, { x, y, w, h: 0, line: { color: c || RULE, width: pt || 1 } });
function table(s, rows, x, y, colW, rowH, fs, mutedLast) {
  const w = colW.reduce((a, b) => a + b, 0);
  s.addTable(rows.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: i === 0, color: (mutedLast && j === r.length - 1 && i > 0) ? MUTED : INK,
    border: [{ type: "none" }, { type: "none" }, { type: "solid", pt: i === 0 ? 1.5 : 0.75, color: i === 0 ? INK : RULE }, { type: "none" }] } }))),
    { x, y, w, colW, rowH, fontFace: "Calibri", fontSize: fs || F, valign: "middle", margin: [0, 0.08, 0, 0] });
  rule(s, x, y, w, INK, 1.5);
}

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
  numbered(s, ["Aim and objectives", "Methodology", "Specimen details and design", "Preliminary results", "Strengthening design", "Summary", "References", "Work done and work to be done"], { x: 0.6, y: 1.5, w: 9, h: 5.3, paraSpaceAfter: 8 });
}

// 3. Aim and objectives
pres.addSection({ title: "Aim and objectives" });
{
  const s = content("Aim and objectives", "Aim and objectives");
  tb(s, "Aim", { x: 0.6, y: 1.3, w: 6, h: 0.45, bold: true, color: ACC });
  tb(s, "To develop and experimentally validate a digital twin that assesses flexural damage in reinforced concrete beams and supports retrofit decisions", { x: 0.6, y: 1.75, w: 12.1, h: 0.95, valign: "top" });
  tb(s, "Objectives", { x: 0.6, y: 2.85, w: 6, h: 0.45, bold: true, color: ACC });
  numbered(s, [
    "To design under-reinforced beams as per IS 456:2000 for four-point bending",
    "To monitor load, deflection, vibration and temperature with low-cost sensors",
    "To estimate flexural stiffness (kN·m²) after each damage stage by Bayesian updating",
    "To predict service-load deflection of damaged beams and validate it by tests",
    "To design jacketing, steel plate and polymer strengthening and verify by failure tests",
  ], { x: 0.6, y: 3.3, w: 12.3, h: 3.6, paraSpaceAfter: 4 });
  s.addNotes("Polymer strengthening = fibre-reinforced polymer laminates. Codes: jacketing IS 15988:2013; polymer ACI PRC-440.2-23 (guide); steel plate by IS 456 limit-state assumptions (clause 38.1).");
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
    "Design & casting: IS 456 under-reinforced beams; cubes for actual strength.",
    "Sensors & cloud: accelerometer, deflection sensor, temperature sensor, automatic tapper; load from the 500 kN frame. ESP32 sends data over 4G to a cloud database; the twin runs in the cloud; alerts go to phones.",
    "Reference test: 15 kN load (below cracking, 26.5 kN) gives stiffness from deflection; tap test gives the natural frequency.",
    "Damage stage: 35, 50, 65, 72 kN, below yield; cracks recorded.",
    "Twin update: Bayesian inference combines the deflection and frequency estimates of stiffness with the previous estimate.",
    "Prediction check: the twin predicts the 30 kN service deflection before the test; 30 kN is below the previous maximum load.",
    "Repair decision against a target agreed with the guide; strengthening after the 65 kN stage; failure test in displacement control.",
  ].join("\n"));
}

// 5. Specimen
pres.addSection({ title: "Specimen details and design" });
{
  const s = content("Specimen details", "Specimen details and design");
  s.addImage({ path: S + "c_specimen.png", x: 0.6, y: 1.25, w: 12.1, h: 12.1 / 2.814 });
  bullets(s, ["Concrete M30; main bars Fe500; stirrups Fe415; clear cover 25 mm", "Simply supported, four-point bending; shear span a = 1000 mm"], { x: 0.6, y: 5.75, w: 12.1, h: 1.15, paraSpaceAfter: 8 });
  s.addNotes("Section 230 x 300 mm uses standard formwork widths. Length 3200 mm, span 3000 mm. Load P from the 500 kN servo-hydraulic frame through a steel spreader beam, P/2 at each third point. Accelerometer at quarter span (away from nodes of modes 1 and 2), deflection sensor at midspan, tapper at a marked point. These sizes are used in all simulations; cast specimens may be scaled to lab constraints.");
}

// 6. Flexural design
{
  const s = content("Specimen design: flexure (IS 456:2000)", "Specimen details and design");
  table(s, [
    ["Step", "Expression", "Result", "Clause"],
    ["Effective depth d", "300 − 25 − 8 − 12/2", "261 mm", "26.4"],
    ["Steel area Ast", "3 × π × 12² / 4", "339 mm²", "—"],
    ["Neutral axis xu", "0.87 fy Ast / (0.36 fck b)", "59.4 mm", "38.1"],
    ["Limit xu,max", "0.46 d  (Fe500)", "120 mm", "38.1"],
    ["Moment capacity Mu", "0.87 fy Ast (d − 0.42 xu)", "34.8 kN·m", "38.1"],
    ["Jack load P", "2 Mu / a,  a = 1.0 m", "70 kN", "—"],
  ], 0.6, 1.4, [3.4, 4.9, 2.1, 1.7], 0.6, F, true);
  bullets(s, ["xu < xu,max: under-reinforced, steel yields before concrete crushes", "Mu < Mu,lim = 0.133 fck b d² = 62.5 kN·m"], { x: 0.6, y: 5.75, w: 12.1, h: 1.15, paraSpaceAfter: 8 });
  s.addNotes("fck = 30 MPa, fy = 500 MPa, b = 230 mm. In four-point bending the moment between the load points is (P/2) x a, so P = 2Mu/a. Self-weight (1.73 kN/m) adds 1.9 kN m at midspan; it is present in the test and is small (about 5% of Mu).");
}

// 7. Cracking, shear, deflection
{
  const s = content("Specimen design: cracking and shear (IS 456:2000)", "Specimen details and design");
  table(s, [
    ["Step", "Expression", "Result", "Clause"],
    ["Cracking stress fcr", "0.7 √fck", "3.83 MPa", "6.2.2"],
    ["Cracking moment Mcr", "fcr Ig / yt", "13.2 kN·m", "C-2.1"],
    ["Cracking load Pcr", "2 Mcr / a", "26.5 kN", "—"],
    ["Shear demand at 70 kN", "Vu = P / 2", "34.8 kN", "—"],
    ["Concrete shear stress τc", "pt = 0.57%,  M30", "0.52 MPa", "Table 19"],
    ["Shear capacity", "Vc + Vus = 31.4 + 63.2", "94.6 kN", "40.4"],
    ["Span / effective depth", "3000 / 261", "11.5 < 20", "23.2.1"],
  ], 0.6, 1.4, [3.9, 4.4, 2.1, 1.7], 0.56, F, true);
  bullets(s, ["Shear capacity is 2.7 times demand: flexure governs"], { x: 0.6, y: 6.15, w: 12.1, h: 0.6 });
  s.addNotes("Ig = b h^3 / 12 = 5.18 x 10^8 mm^4, yt = 150 mm. Stirrups 2-legged 8 mm Fe415 at 150 mm: Vus = 0.87 fy Asv d / sv = 63.2 kN; spacing 150 mm < 0.75d = 196 mm (26.5.1.5); Asv = 100.5 mm2 > minimum 38.2 mm2 (26.5.1.6).");
}

// 8. Stiffness and frequency
{
  const s = content("How the twin measures damage: stiffness", "Specimen details and design");
  table(s, [
    ["Quantity", "Expression", "Result", "Source"],
    ["Elastic modulus Ec", "5000 √fck", "27,386 MPa", "IS 456 6.2.3.1"],
    ["Second moment Ig", "b h³ / 12", "5.18 × 10⁸ mm⁴", "Gross section"],
    ["Flexural stiffness EI", "Ec × Ig", "14,172 kN·m²", "Undamaged"],
    ["Mass per metre m", "2500 × 0.23 × 0.30", "172.5 kg/m", "Density"],
    ["First frequency f₁", "(π / 2L²) √(EI / m)", "50.0 Hz", "Beam theory"],
    ["Deflection δ", "23 P L³ / (1296 EI)", "0.51 mm at 15 kN", "Beam theory"],
  ], 0.6, 1.4, [3.3, 3.6, 2.9, 2.3], 0.6);
  bullets(s, ["Damage lowers EI: deflection rises, frequency falls", "Twin works back from measured δ and f₁ to current EI"], { x: 0.6, y: 5.75, w: 12.1, h: 1.15, paraSpaceAfter: 8 });
  s.addNotes("Stiffness cannot be measured directly. From a measured deflection under a known load: EI = 23 P L^3 / (1296 delta). From a measured frequency: EI = m (2 L^2 f1 / pi)^2, so EI is proportional to f1 squared. The twin combines both by Bayesian inference.");
}

// 9. Damage stages
pres.addSection({ title: "Preliminary results" });
{
  const s = content("Results: stiffness loss with damage (simulation)", "Preliminary results");
  s.addImage({ path: S + "c_damage.png", x: 0.5, y: 1.4, w: 7.7, h: 7.7 / 1.64 });
  bullets(s, ["Loaded to 35, 50, 65, 72 kN, then unloaded", "15 kN load and tap test after each", "EI from δ: 42% left", "EI from f₁: 46% left", "Two methods agree"], { x: 8.45, y: 1.6, w: 4.4, h: 5.2, paraSpaceAfter: 14 });
  s.addNotes("Fibre beam model of the 230 x 300 mm beam (OpenSeesPy). Damage stages below yield (81 kN). First frequency falls from 49.0 to 33.2 Hz; (33.2/49.0)^2 = 46%. Deflection under 15 kN rises from 0.53 to 1.27 mm; 0.53/1.27 = 42%.");
}

// 10. Twin prediction
{
  const s = content("Results: twin prediction (simulated tests)", "Preliminary results");
  s.addImage({ path: S + "c_twin.png", x: 0.5, y: 1.4, w: 7.7, h: 7.7 / 1.64 });
  bullets(s, ["Twin predicts 30 kN deflection", "Prediction saved before test", "Sensor data simulated", "Combined error ≤ 1.3%", "No updating: up to 58%"], { x: 8.45, y: 1.6, w: 4.4, h: 5.2, paraSpaceAfter: 14 });
  s.addNotes("The 'measurements' come from the fibre model with sensor noise added (frequency repeatability 0.3 Hz, displacement 0.01 mm). This checks the updating method before real tests. Static-only is equally accurate here; combining both protects against a faulty or noisy sensor.");
}

// 11. Strengthening design
pres.addSection({ title: "Strengthening design" });
{
  const s = content("Strengthening design (design capacities)", "Strengthening design");
  table(s, [
    ["Scheme", "Size", "Basis", "Capacity"],
    ["Unstrengthened", "—", "IS 456 cl 38.1", "70 kN"],
    ["Polymer laminates", "2 strips 50 × 1.2 mm", "ACI PRC-440.2-23", "107 kN"],
    ["Steel plate", "100 × 5 mm, Fe250", "IS 456 cl 38.1", "125 kN"],
    ["Concrete jacket", "75 mm, 2 bars 12 mm", "IS 15988:2013", "131 kN"],
  ], 0.6, 1.4, [3.3, 3.6, 3.2, 2.0], 0.62);
  bullets(s, ["Capacities by strain compatibility, IS 456 cl 38.1 assumptions", "Polymer limited by debonding at strain 0.0045", "Twin selects against the target agreed with the guide"], { x: 0.6, y: 4.75, w: 12.1, h: 2.1, paraSpaceAfter: 10 });
  s.addNotes("Polymer: carbon laminates, E = 165 GPa; debonding strain epsilon_fd = 0.41 sqrt(f'c / (n Ef tf)) with f'c = 24 MPa (cylinder, 0.8 x cube), as in the ACI 440 guide; ACI PRC-440.2-23 supersedes 440.2R-17 and is a guide, not a code. Steel plate treated as additional tension steel. Jacket: 75 mm on soffit and sides with 2 bars of 12 mm; detailing per IS 15988:2013.");
}

// 12. Summary
pres.addSection({ title: "Summary" });
{
  const s = content("Summary", "Summary");
  bullets(s, ["Specimen designed to IS 456: under-reinforced", "Design capacity 70 kN; cracking at 26.5 kN", "Shear capacity 2.7 × demand: flexure governs", "Damage measured by both deflection and frequency", "Twin predicted deflection within 1.3% (simulated)", "Strengthening raises capacity by 53–87%"], { x: 0.6, y: 1.45, w: 12.1, h: 5.4, paraSpaceAfter: 14 });
}

// 13. References
pres.addSection({ title: "References" });
{
  const s = content("References", "References");
  numbered(s, [
    "IS 456:2000, Plain and reinforced concrete, BIS",
    "IS 15988:2013, Seismic evaluation and strengthening, BIS",
    "ACI PRC-440.2-23, Externally bonded polymer systems (guide)",
    "Maeck et al. (2000), Engineering Structures, 22(10)",
    "Xu and Castel (2016), J. Sound and Vibration, 368",
    "Capozucca (2013), Composites Part B, 46",
    "Lu et al. (2005), Engineering Structures, 27(6)",
    "Torzoni et al. (2024), Comput. Methods Appl. Mech. Eng., 418",
  ], { x: 0.6, y: 1.45, w: 12.1, h: 5.4, paraSpaceAfter: 6 });
  s.addNotes([
    "1. IS 456:2000. Plain and Reinforced Concrete: Code of Practice. Bureau of Indian Standards.",
    "2. IS 15988:2013. Seismic Evaluation and Strengthening of Existing Reinforced Concrete Buildings: Guidelines. Bureau of Indian Standards.",
    "3. ACI PRC-440.2-23. Design and Construction of Externally Bonded Fiber-Reinforced Polymer (FRP) Systems for Strengthening Concrete Structures: Guide. American Concrete Institute (supersedes ACI 440.2R-17).",
    "4. Maeck, J. et al. (2000). Damage identification in reinforced concrete structures by dynamic stiffness determination. Engineering Structures, 22(10), 1339-1349.",
    "5. Xu, T. and Castel, A. (2016). Modeling the dynamic stiffness of cracked reinforced concrete beams under low-amplitude vibration loads. Journal of Sound and Vibration, 368, 135-147.",
    "6. Capozucca, R. (2013). Assessment of CFRP strengthened RC beams through dynamic tests. Composites Part B: Engineering, 46, 69-80.",
    "7. Lu, X.Z., Teng, J.G., Ye, L.P. and Jiang, J.J. (2005). Bond-slip models for FRP sheets/plates bonded to concrete. Engineering Structures, 27(6), 920-937.",
    "8. Torzoni, M. et al. (2024). A digital twin framework for civil engineering structures. Computer Methods in Applied Mechanics and Engineering, 418, 116584.",
  ].join("\n"));
}

// 14. Work done and work to be done (Gantt)
pres.addSection({ title: "Work done and work to be done" });
{
  const s = content("Work done and work to be done (2026–27)", "Work done and work to be done");
  const months = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"];
  const gx = 4.85, gw = 7.98, mw = gw / months.length, top = 1.4, hh = 0.5, rh = 0.47;
  months.forEach((m, i) => {
    tb(s, m, { x: gx + i * mw, y: top, w: mw, h: hh, bold: true, align: "center", valign: "middle" });
    if (i > 0) s.addShape(pres.shapes.LINE, { x: gx + i * mw, y: top + hh, w: 0, h: 9 * rh, line: { color: "E6E6E6", width: 0.75 } });
  });
  rule(s, 0.6, top + hh, 12.23, INK, 1.5);
  const pos = (m, d) => gx + (m + (d - 1) / 30) * mw;
  const tasks = [
    ["Literature review", [0, 1], [3, 14], true], ["Design and simulation", [2, 1], [3, 14], true],
    ["Sensors and cloud", [3, 15], [5, 30], false], ["Casting and curing", [4, 1], [5, 15], false],
    ["Pilot test", [5, 1], [5, 30], false], ["Damage-stage tests", [6, 1], [7, 15], false],
    ["Strengthening", [7, 1], [8, 15], false], ["Failure tests", [8, 1], [8, 30], false], ["Analysis and thesis", [8, 1], [9, 30], false],
  ];
  tasks.forEach(([name, a, b, done], i) => {
    const y = top + hh + i * rh;
    tb(s, name, { x: 0.6, y, w: 4.2, h: rh, valign: "middle" });
    const x1 = pos(a[0], a[1]), x2 = pos(b[0], b[1] + 1);
    s.addShape(pres.shapes.RECTANGLE, { x: x1, y: y + 0.14, w: x2 - x1, h: rh - 0.28, fill: { color: done ? "4D4D4D" : ACC }, line: { color: done ? "4D4D4D" : ACC } });
  });
  const endY = top + hh + tasks.length * rh;
  rule(s, 0.6, endY, 12.23, RULE, 0.75);
  const rx = pos(3, 14);
  s.addShape(pres.shapes.LINE, { x: rx, y: top + hh, w: 0, h: endY - top - hh, line: { color: INK, width: 1.5, dashType: "dash" } });
  const ly = endY + 0.15;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: ly + 0.16, w: 0.45, h: 0.22, fill: { color: "4D4D4D" }, line: { color: "4D4D4D" } });
  tb(s, "Work done", { x: 1.15, y: ly, w: 2.0, h: 0.55, valign: "middle" });
  s.addShape(pres.shapes.RECTANGLE, { x: 3.4, y: ly + 0.16, w: 0.45, h: 0.22, fill: { color: ACC }, line: { color: ACC } });
  tb(s, "To be done", { x: 3.95, y: ly, w: 2.0, h: 0.55, valign: "middle" });
  s.addShape(pres.shapes.LINE, { x: 6.2, y: ly + 0.27, w: 0.45, h: 0, line: { color: INK, width: 1.5, dashType: "dash" } });
  tb(s, "Review 2 (14 Oct)", { x: 6.8, y: ly, w: 3.3, h: 0.55, valign: "middle" });
  s.addNotes("Work done: literature review, methodology, IS 456 design, fibre and continuum simulations, damage-stage simulation, twin prediction test, strengthening design, ANSYS input files. Thesis submission April 2027. Casting in November allows 28-day curing before the pilot test; jacket curing falls in February to March.");
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
  const out = S + "StrucIQ_Review2_120ABR_v4.pptx";
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("written", out);
})();
