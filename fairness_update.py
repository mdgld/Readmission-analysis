import json
import csv
import pathlib

portfolio = pathlib.Path("portfolio")
figures = pathlib.Path("figures")

with open(figures / "AdvStats_fairness_disparities.csv") as f:
    new_fairness = list(csv.DictReader(f))

data = json.loads((portfolio / "data.json").read_text())
data["fairness"] = new_fairness
(portfolio / "data.json").write_text(json.dumps(data, indent=2))
print("Updated fairness:", [r["Pairing"] for r in new_fairness])
