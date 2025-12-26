# ncpa/allocator.py

from enum import Enum

class CollisionPolicy(Enum):
    STRICT = "strict"
    RELAXED = "relaxed"


class EpochManager:
    def __init__(self):
        self.current = 0

    def advance(self):
        self.current += 1


class Allocator:
    def __init__(self, policy=CollisionPolicy.RELAXED):
        self.policy = policy
        self.reserved = set()  # (epoch, node, step)

    def allocate(self, epoch):
        paths = [
            ["S", "A", "C", "T"],
            ["S", "B", "D", "T"],
        ]

        for path in paths:
            last = len(path) - 1
            ok = True

            for step, node in enumerate(path):
                if self.policy == CollisionPolicy.RELAXED:
                    if step == 0 or step == last:
                        continue
                if (epoch, node, step) in self.reserved:
                    ok = False
                    break

            if ok:
                for step, node in enumerate(path):
                    if self.policy == CollisionPolicy.RELAXED:
                        if step == 0 or step == last:
                            continue
                    self.reserved.add((epoch, node, step))
                return path

        raise RuntimeError("Allocator exhausted")
