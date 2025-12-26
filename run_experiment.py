from synthetic_dataset import generate_dataset
from ncpa_tester import run_dataset

dataset = generate_dataset(
    num_paths=100,
    attack_ratio=0.4,
)

ok = run_dataset(dataset)

print("Dataset validation:", "PASSED" if ok else "FAILED")

