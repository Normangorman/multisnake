class Vector2():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, vec):
        return Vector2(self.x + vec.x, self.y + vec.y)

    def north(self):
        return Vector2(0,1)

    def east(self):
        return Vector2(1,0)

    def south(self):
        return Vector2(0,-1)

    def west(self):
        return Vector2(-1,0)

