
class Transform:
    __slots__ = ['origin', 'offset', 'rotation', 'scale']

    def __init__(self, origin=(0, 0), offset=(0, 0), rotation=0, scale=1):
        super().__init__()
        self.origin = origin
        self.offset = offset
        self.rotation = rotation
        self.scale = scale

    def __add__(self, other):
        if not other:
            return self
        elif type(other) is Transform:
            return Transform(origin=(self.origin[0] + other.origin[0], self.origin[1] + other.origin[1]),
                             offset=(self.offset[0] + other.offset[0], self.offset[1] + other.offset[1]),
                             rotation=self.rotation + other.rotation,
                             scale=self.scale * other.scale)
        else:
            raise TypeError