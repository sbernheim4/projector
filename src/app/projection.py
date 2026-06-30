class Projection:
    def __init__(self, paths=None):
        self.paths = paths or []

    def __add__(self, other):
        other = to_projection(other)
        return Projection(self.paths + other.paths)


def to_projection(x):
    if isinstance(x, Projection):
        return x

    if isinstance(x, Leaf):
        return Projection([x.path])

    raise TypeError(f"Cannot convert {type(x)} to Projection")


def compile_projection(projection):
    projection = to_projection(projection)

    spec = {}

    for path in projection.paths:
        cursor = spec
        for part in path[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[path[-1]] = True

    return spec


class Leaf:
    def __init__(self, path):
        self.path = path

    def __add__(self, other):
        return to_projection(self) + to_projection(other)

    def __repr__(self):
        return ".".join(self.path)

