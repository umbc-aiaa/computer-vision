from collections import Counter
import os

label_dir = "datasets/SUAS2025/labels/train"
counts = Counter()

for file in os.listdir(label_dir):
    with open(os.path.join(label_dir, file)) as f:
        for line in f:
            cls_id = int(line.strip().split()[0])
            counts[cls_id] += 1

print("Class Frequencies in Train Labels:")
for cid, count in sorted(counts.items()):
    print(f"Class {cid}: {count} labels")
