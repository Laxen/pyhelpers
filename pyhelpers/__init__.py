class Coord:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __repr__(self):
        return "({},{})".format(self.x, self.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    @classmethod
    def from_string(cls, string):
        x, y = string.split(",")
        return cls(x, y)

class Grid2D:
    def __init__(self, width, height, element):
        self.width = width
        self.height = height

        self.grid = dict()
        for y in range(self.height):
            for x in range(self.width):
                self[x, y] = element

    def __repr__(self):
        string = ""
        for y in range(self.height):
            for x in range(self.width):
                string += str(self[x, y]) + " "
            string += "\n"

        return string

    def __iter__(self):
        for y in range(self.height):
            for x in range(self.width):
                yield Coord(x,y), self[x, y]

    def __getitem__(self, keys):
        if isinstance(keys, tuple):
            return self.grid[Coord(keys[0], keys[1])]
        elif isinstance(keys, Coord):
            return self.grid[keys]
        else:
            raise TypeError("Grid can't get element with key type {}".format(type(keys)))

    def __setitem__(self, keys, item):
        if isinstance(keys, tuple):
            self.grid[Coord(keys[0], keys[1])] = item
        elif isinstance(keys, Coord):
            self.grid[keys] = item
        else:
            raise TypeError("Grid can't set element with key type {}".format(type(keys)))

    def neighbors(self, coord, diagonal=True):
        n = dict()
        x = coord.x
        y = coord.y

        if y > 0:
            n[Coord(x, y-1)] = self[x, y-1]
            if diagonal and x > 0:
                n[Coord(x-1, y-1)] = self[x-1, y-1]
            if diagonal and x < self.width - 1:
                n[Coord(x+1, y-1)] = self[x+1, y-1]
        if y < self.height - 1:
            n[Coord(x, y+1)] = self[x, y+1]
            if diagonal and x > 0:
                n[Coord(x-1, y+1)] = self[x-1, y+1]
            if diagonal and x < self.width - 1:
                n[Coord(x+1, y+1)] = self[x+1, y+1]
        if x > 0:
            n[Coord(x-1, y)] = self[x-1, y]
        if x < self.width - 1:
            n[Coord(x+1, y)] = self[x+1, y]

        return n
