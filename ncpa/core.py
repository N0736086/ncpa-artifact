# ncpa/core.py

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
