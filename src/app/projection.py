from typing import Generic, TypeVar

T = TypeVar("T")


class Projection:
    def __init__(self, paths=None, required: bool | None = None):
        self.paths = paths or []
        self.required_flag = required

    def __add__(self, other):
        other = to_projection(other)
        required = self.required_flag if self.required_flag is not None else other.required_flag
        return Projection(self.paths + other.paths, required=required)

    def required(self):
        return Projection(self.paths, required=True)

    def optional(self):
        return Projection(self.paths, required=False)


class ProjectionSpec:
    def __init__(self, children=None, required: bool | None = None):
        self.children = children or {}
        self.required = required

    def __eq__(self, other):
        if isinstance(other, bool):
            return other is True and not self.children
        if isinstance(other, dict):
            if self.children:
                return self.children == other
            return other is True
        if isinstance(other, ProjectionSpec):
            return self.children == other.children and self.required == other.required
        return NotImplemented

    def __repr__(self):
        return repr(self.children) if self.children else "True"


def to_projection(x):
    if isinstance(x, Projection):
        return x

    if isinstance(x, Leaf):
        return Projection([(x.path, x.required_flag)], required=x.required_flag)

    if isinstance(x, list):
        return Projection([(path, None) for path in x])

    raise TypeError(f"Cannot convert {type(x)} to Projection")


def compile_projection(projection):
    projection = to_projection(projection)

    spec: dict[str, ProjectionSpec] = {}

    for item in projection.paths:
        if len(item) == 2 and isinstance(item[1], (bool, type(None))):
            path, required = item
        else:
            path, required = item, None

        cursor = spec
        for part in path[:-1]:
            node = cursor.get(part)
            if node is None:
                node = ProjectionSpec()
                cursor[part] = node
            if required is not None:
                node.required = required
            cursor = node.children
        leaf = cursor.get(path[-1])
        if leaf is None:
            leaf = ProjectionSpec(required=required)
            cursor[path[-1]] = leaf
        elif required is not None:
            leaf.required = required

    return spec


class Leaf(Generic[T]):
    def __init__(self, path, required: bool | None = None):
        self.path = path
        self.required_flag = required

    def __add__(self, other):
        return to_projection(self) + to_projection(other)

    def __getattr__(self, name):
        return Leaf(self.path + [name], required=self.required_flag)

    def required(self):
        return Leaf(self.path, required=True)

    def optional(self):
        return Leaf(self.path, required=False)

    def __repr__(self):
        return ".".join(self.path)
