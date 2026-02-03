import csv
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict

###################################################
# Input CSV (from authorsFileTouches.py)
###################################################

repo = "scottyab/rootbeer"
input_csv = f"data/authors_file_touches_{repo.split('/')[1]}.csv"

###################################################
# Read CSV
###################################################

rows = []
with open(input_csv, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

###################################################
# Map files and authors to indices
###################################################

files = sorted(set(r["Filename"] for r in rows))
authors = sorted(set(r["Author"] for r in rows))

file_index = {f: i for i, f in enumerate(files)}
author_index = {a: i for i, a in enumerate(authors)}

###################################################
# Convert dates → weeks since project start
###################################################

dates = [datetime.fromisoformat(r["Date"]) for r in rows if r["Date"] != "Unknown"]
start_date = min(dates)

def weeks_since_start(date_str):
    d = datetime.fromisoformat(date_str)
    return (d - start_date).days // 7

###################################################
# Build plotting arrays
###################################################

x = []  # file indices
y = []  # weeks
c = []  # author indices

for r in rows:
    if r["Date"] == "Unknown":
        continue
    x.append(file_index[r["Filename"]])
    y.append(weeks_since_start(r["Date"]))
    c.append(author_index[r["Author"]])

###################################################
# Plot
###################################################

plt.figure(figsize=(12, 7))

scatter = plt.scatter(
    x,
    y,
    c=c,
    cmap="tab10",     # good categorical colormap
    alpha=0.75,
    edgecolors="none"
)

plt.xlabel("File")
plt.ylabel("Weeks")
plt.title("File Touches Over Time (Colored by Author)")

###################################################
# Legend (author → color)
###################################################

handles = []
for author, idx in author_index.items():
    handles.append(
        plt.Line2D(
            [], [], marker='o', linestyle='',
            label=author,
            color=plt.cm.tab10(idx % 10)
        )
    )

plt.legend(
    handles=handles,
    title="Author",
    bbox_to_anchor=(1.05, 1),
    loc="upper left"
)

plt.tight_layout()
plt.show()