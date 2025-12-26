# ncpa_tester.py

from ncpa.core import Validator, PathRegistry

def run_dataset(dataset):
    registry = PathRegistry()
    results = []

    for row in dataset:
        v = Validator(
            node=row["node"],
            step_index=row["step"],
            registry=registry,
        )

        ok = v.validate(
            row["path_id"],
            row["epoch"],
            row["step"],
            row["node"],
        )

        results.append(ok == row["expected_valid"])

    return all(results)
