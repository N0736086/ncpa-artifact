import pytest
from hypothesis import given, strategies as st

# ============================================================
# Global Path Registry (authoritative state)
# ============================================================

# ============================================================
# Epoch Manager
# ============================================================

class EpochManager:
    def __init__(self):
        self.current = 0

    def advance(self):
        self.current += 1
# ============================================================
# Global Path Registry (authoritative state)
# ============================================================

class PathRegistry:
    def __init__(self):
        self.state = {}  # path_id -> (epoch, expected_step)

    def init(self, path_id, epoch):
        if path_id not in self.state:
            self.state[path_id] = (epoch, 0)

    def check_and_advance(self, path_id, epoch, step):
        stored_epoch, expected = self.state[path_id]
        if epoch != stored_epoch:
            return False
        if step != expected:
            return False
        self.state[path_id] = (epoch, expected + 1)
        return True

# ============================================================
# Allocator
# ============================================================
from enum import Enum

class CollisionPolicy(Enum):
    STRICT = "strict"
    RELAXED = "relaxed"



class Allocator:
    def __init__(self, policy=CollisionPolicy.RELAXED):
        self.policy = policy
        self.reserved = set()  # (epoch, node, step)

    def allocate(self, epoch):
        paths = [
            ["S", "A", "C", "T"],
            ["S", "B", "D", "T"]
        ]

        for path in paths:
            last = len(path) - 1
            ok = True

            for step, node in enumerate(path):
                if self.policy == CollisionPolicy.RELAXED:
                    if step == 0 or step == last:
                        continue  # shared entry/exit allowed

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

# ============================================================
# Validator
# ============================================================

class Validator:
    def __init__(self, node, step_index, registry):
        self.node = node
        self.step_index = step_index
        self.registry = registry

    def validate(self, path_id, epoch, step, node):
        if node != self.node:
            return False

        if step != self.step_index:
            return False

        self.registry.init(path_id, epoch)
        return self.registry.check_and_advance(path_id, epoch, step)

#==========================================================
#Byzantine validator cannot skip steps
class ByzantineValidator(Validator):
    def validate(self, path_id, epoch, step, node):
        # Lies: always claims to be correct
        self.registry.init(path_id, epoch)
        return self.registry.check_and_advance(
            path_id,
            epoch,
            step + 1  # malicious skip
        )


# ========================================================
# ============================================================
# Hypothesis Strategy
# ============================================================

paths = [
    ["S", "A", "C", "T"],
    ["S", "B", "D", "T"]
]

path_strategy = st.sampled_from(paths)

# ============================================================
# Properties
# ============================================================

@given(path_strategy)
def test_no_replay(path):
    epoch = 0
    registry = PathRegistry()

    validators = {
        node: Validator(node, i, registry)
        for i, node in enumerate(path)
    }

    pid = "pid"

    for step, node in enumerate(path):
        assert validators[node].validate(pid, epoch, step, node)

    # replay last step
    assert not validators[path[-1]].validate(
        pid, epoch, len(path) - 1, path[-1]
    )


@given(path_strategy)
def test_no_skip(path):
    epoch = 0
    registry = PathRegistry()
    validators = {
        node: Validator(node, i, registry)
        for i, node in enumerate(path)
    }
    pid = "pid"

    assert not validators[path[2]].validate(pid, epoch, 2, path[2])

@given(path_strategy)
def test_wrong_node_rejected(path):
    epoch = 0
    registry = PathRegistry()
    validators = {
        node: Validator(node, i, registry)
        for i, node in enumerate(path)
    }
    pid = "pid"

    assert not validators[path[1]].validate(pid, epoch, 0, path[1])


@given(path_strategy)
def test_parallel_use_fails(path):
    epoch = 0
    registry = PathRegistry()
    validators = {
        node: Validator(node, i, registry)
        for i, node in enumerate(path)
    }
    pid = "pid"

    assert validators[path[0]].validate(pid, epoch, 0, path[0])
    assert validators[path[1]].validate(pid, epoch, 1, path[1])
    assert not validators[path[1]].validate(pid, epoch, 1, path[1])


def test_allocator_no_collision():
    allocator = Allocator()
    epoch = 0

    p1 = allocator.allocate(epoch)
    p2 = allocator.allocate(epoch)

    last = len(p1) - 1
    for step in range(1, last):
        assert p1[step] != p2[step]

def test_allocator_exhaustion():
    allocator = Allocator()
    epoch = 0

    allocator.allocate(epoch)
    allocator.allocate(epoch)

    with pytest.raises(RuntimeError):
        allocator.allocate(epoch)

def test_strict_allocator_single_path():
    allocator = Allocator(policy=CollisionPolicy.STRICT)
    epoch = 0

    allocator.allocate(epoch)

    with pytest.raises(RuntimeError):
        allocator.allocate(epoch)

def test_relaxed_allocator_two_paths():
    allocator = Allocator(policy=CollisionPolicy.RELAXED)
    epoch = 0

    p1 = allocator.allocate(epoch)
    p2 = allocator.allocate(epoch)

    last = len(p1) - 1
    for step in range(1, last):
        assert p1[step] != p2[step]

def test_epoch_rollover_restores_capacity():
    allocator = Allocator()
    epoch_mgr = EpochManager()

    allocator.allocate(epoch_mgr.current)
    allocator.allocate(epoch_mgr.current)

    with pytest.raises(RuntimeError):
        allocator.allocate(epoch_mgr.current)

    epoch_mgr.advance()
    allocator.allocate(epoch_mgr.current)  # must succeed

def test_old_epoch_path_rejected():
    registry = PathRegistry()
    pid = "pid"

    registry.init(pid, epoch=0)
    assert registry.check_and_advance(pid, 0, 0)

    # same PathID cannot advance in new epoch
    assert not registry.check_and_advance(pid, 1, 1)

def test_byzantine_double_advance_fails():
    registry = PathRegistry()
    epoch = 0
    pid = "pid"

    honest = Validator("S", 0, registry)
    byzantine = ByzantineValidator("A", 1, registry)

    assert honest.validate(pid, epoch, 0, "S")
    assert not byzantine.validate(pid, epoch, 1, "A")
    assert not byzantine.validate(pid, epoch, 1, "A")

def test_byzantine_epoch_confusion_fails():
    registry = PathRegistry()
    pid = "pid"

    registry.init(pid, epoch=0)
    assert registry.check_and_advance(pid, 0, 0)

    # Byzantine attempts to continue in new epoch
    assert not registry.check_and_advance(pid, 1, 1)
