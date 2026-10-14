"""Decision tree learned from the retrofit simulation (retrofit_sim.csv).
Inputs are only quantities known in practice: twin stiffness left (lower bound), measured crack width / code limit,
live load factor (change of use), span / effective depth, steel ratio, design utilisation, dead load fraction.
Trained on 70% of the beams, tested on the 30% it never saw. Classes are weighted (class_weight="balanced") because
plate or jacket beams are rare (4%) and sending one of them to polymer laminates would be the unsafe error. Writes retrofit_tree.txt and retrofit_sim_summary.json."""
import csv, json, numpy as np
from collections import Counter
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, balanced_accuracy_score

R = list(csv.DictReader(open('retrofit_sim.csv')))
FEAT = [('stiffness_left_lower', 'Stiffness left (twin, lower bound)'), ('crack_ratio', 'Crack width / code limit'),
        ('strength_ratio', 'Moment demand / capacity'), ('deflection_ratio', 'Deflection / span/250 limit'),
        ('live_load_factor', 'Live load factor (change of use)'), ('span_depth', 'Span / effective depth'),
        ('pt', 'Steel ratio (%)'), ('utilisation', 'Design utilisation'), ('dead_fraction', 'Dead load fraction')]
merge = {'Concrete jacket': 'Steel plate or jacket', 'Steel plate': 'Steel plate or jacket'}
X = np.array([[float(r[k]) for k, _ in FEAT] for r in R]); y = np.array([merge.get(r['best'], r['best']) for r in R])
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=7, stratify=y)
out = {}
for depth in (3, 4, 5):
    t = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=20, random_state=7, class_weight='balanced').fit(Xtr, ytr)
    u = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=20, random_state=7).fit(Xtr, ytr)
    out[depth] = (accuracy_score(ytr, t.predict(Xtr)), accuracy_score(yte, t.predict(Xte)), t,
                  balanced_accuracy_score(yte, t.predict(Xte)), accuracy_score(yte, u.predict(Xte)), balanced_accuracy_score(yte, u.predict(Xte)))
    print('depth', depth, 'train %.3f test %.3f balanced %.3f | unweighted test %.3f balanced %.3f' % (out[depth][:2] + out[depth][3:]))
DEPTH = 3; tree = out[DEPTH][2]
labels = list(tree.classes_)
cm = confusion_matrix(yte, tree.predict(Xte), labels=labels)
rules = export_text(tree, feature_names=[n for _, n in FEAT], decimals=2)
open('retrofit_tree.txt', 'w').write(rules)
imp = dict(zip([n for _, n in FEAT], tree.feature_importances_.round(3).tolist()))
c = Counter(r['best'] for r in R)
summ = dict(beams=len(R), best_counts=dict(c), share={k: round(v / len(R), 3) for k, v in c.items()},
            success_rate={s: round(np.mean([r[s + '_ok'] == 'True' for r in R]), 3) for s in ('polymer', 'plate', 'jacket')},
            polymer_gate_fail=round(np.mean([r['polymer_gate'] == 'False' for r in R]), 3),
            propped=dict(Counter(r['best'] for r in R if r['propped'] == 'True')),
            failing_before=dict(Counter(r['fails'] for r in R).most_common(12)),
            tree=dict(depth=DEPTH, class_weight='balanced', train_accuracy=round(out[DEPTH][0], 3), test_accuracy=round(out[DEPTH][1], 3),
                      test_balanced_accuracy=round(out[DEPTH][3], 3), test_beams=len(yte),
                      labels=labels, confusion_test=cm.tolist(), importance=imp),
            depth_study={d: dict(train=round(v[0], 3), test=round(v[1], 3), test_balanced=round(v[3], 3), unweighted_test=round(v[4], 3), unweighted_balanced=round(v[5], 3)) for d, v in out.items()})
json.dump(summ, open('retrofit_sim_summary.json', 'w'), indent=1)
print(rules); print(json.dumps(summ, indent=1)[:2500])
