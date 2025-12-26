import random
from ncpa.core import Validator, PathRegistry

PATHS = [
    ["S", "A", "C", "T"],
    ["S", "B", "D", "T"],
]

ATTACKS = [
    "replay",
    "skip",
    "wrong_node",
    "parallel",
    "epoch_confusion",
]

def generate_dataset(
    num_paths=50,
    max_epoch=5,
    attack_ratio=0.3,
    seed=42
):
    random.seed(seed)
    dataset = []
    event_id = 0
    timestamp = 0

    for pid in range(num_paths):
        path = random.choice(PATHS)
        epoch = random.randint(0, max_epoch)
        path_id = f"pid-{pid}"

        attack = random.choice(ATTACKS) if random.random() < attack_ratio else None

        # normal execution
        for step, node in enumerate(path):
            dataset.append({
                "event_id": event_id,
                "path_id": path_id,
                "epoch": epoch,
                "step": step,
                "node": node,
                "path_type": "adversarial" if attack else "normal",
                "attack_type": attack or "none",
                "timestamp": timestamp,
                "expected_valid": True,
            })
            event_id += 1
            timestamp += 1

        # inject adversarial behavior
        if attack == "replay":
            # replay last valid step
            dataset.append({
                "event_id": event_id,
                "path_id": path_id,
                "epoch": epoch,
                "step": len(path) - 1,
                "node": path[-1],
                "path_type": "adversarial",
                "attack_type": "replay",
                "timestamp": timestamp,
                "expected_valid": False,
            })
            event_id += 1
            timestamp += 1

        elif attack == "skip":
            # jump directly to step 2
            dataset.append({
                "event_id": event_id,
                "path_id": path_id,
                "epoch": epoch,
                "step": 2,
                "node": path[2],
                "path_type": "adversarial",
                "attack_type": "skip",
                "timestamp": timestamp,
                "expected_valid": False,
            })
            event_id += 1
            timestamp += 1

        elif attack == "wrong_node":
            dataset.append({
                "event_id": event_id,
                "path_id": path_id,
                "epoch": epoch,
                "step": 1,
                "node": "X",
                "path_type": "adversarial",
                "attack_type": "wrong_node",
                "timestamp": timestamp,
                "expected_valid": False,
            })
            event_id += 1
            timestamp += 1

        elif attack == "epoch_confusion":
            dataset.append({
                "event_id": event_id,
                "path_id": path_id,
                "epoch": epoch + 1,
                "step": 1,
                "node": path[1],
                "path_type": "adversarial",
                "attack_type": "epoch_confusion",
                "timestamp": timestamp,
                "expected_valid": False,
            })
            event_id += 1
            timestamp += 1

        elif attack == "parallel":
            dataset.append({
                "event_id": event_id,
                "path_id": path_id,
                "epoch": epoch,
                "step": 1,
                "node": path[1],
                "path_type": "adversarial",
                "attack_type": "parallel",
                "timestamp": timestamp,
                "expected_valid": False,
            })
            event_id += 1
            timestamp += 1

    return dataset
