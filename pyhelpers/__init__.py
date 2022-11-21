import math

class Coord:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    # Returns a Coord from a string with format "x,y"
    @classmethod
    def from_string(cls, string):
        x, y = string.split(",")
        return cls(x, y)

    # Returns the squared distance from this Coord to another Coord
    def distance2_to(self, other):
        return (self.x - other.x)**2 + (self.y - other.y)**2

    def __repr__(self):
        return "({},{})".format(self.x, self.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        if isinstance(other, Coord):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]
        else:
            raise TypeError("Can't compare Coord to type {}".format(type(other)))

    def __hash__(self):
        return hash((self.x, self.y))

class Grid2D:
    def __init__(self, width, height, element):
        self.width = width
        self.height = height

        self.grid = dict()
        for y in range(self.height):
            for x in range(self.width):
                self[x, y] = element

    # Returns a Grid2D with elements initialized from a 2D list
    @classmethod
    def from_2d_list(cls, list_2d):
        grid = Grid2D(len(list_2d[0]), len(list_2d), 0)
        for c, _ in grid:
            grid[c] = list_2d[c.y][c.x]
        return grid

    # Returns a Grid2D with Coords from coords_list set to element and the rest
    # set to 0
    @classmethod
    def from_coords(cls, coords_list, element):
        grid = Grid2D(0, 0, 0)
        for c in coords_list:
            grid.width = max(grid.width, c.x + 1)
            grid.height = max(grid.height, c.y + 1)
            grid[c] = element

        return grid

    # Returns a dict with the neighbors for a given Coord
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

    # Returns the number of times an element occurs in the grid
    def count(self, element):
        count = 0
        for _, d in self:
            if d == element:
                count += 1
        return count

    # Returns a list of Coords containing the shortest path from start to end
    def find_path(self, start, end):
        class Node:
            def __init__(self, coords, cost):
                self.coords = coords
                self.parent = None
                self.g = math.inf
                self.h = 0
                self.cost = cost

            def __lt__(self, other):
                return self.f < other.f

            def __repr__(self):
                return str(self.coords) + ": " + str(self.cost)

            @property
            def f(self):
                return self.g + self.h

        # Make a grid of nodes that contain the coords and costs
        path_grid = Grid2D(self.width, self.height, 0)
        for c, _ in path_grid:
            n = Node(c, self[c])
            n.h = start.distance2_to(end)
            path_grid[c] = n

        # Init the openset with the start node
        openset = [path_grid[start]]
        path_grid[start].g = 0

        while len(openset) > 0:
            # Sorts the openset so the cheapest node is at the end, then we pop it off
            list.sort(openset, reverse=True)
            current = openset.pop()

            if current.coords == end:
                break

            for c, n in path_grid.neighbors(current.coords, diagonal=False).items():
                new_g = current.g + n.cost

                # This is a cheaper way to reach this node, update it
                if new_g < n.g:
                    n.parent = current
                    n.g = new_g

                    if n not in openset:
                        openset.append(n)

        path = [end]
        n = path_grid[end].parent
        while n != None:
            path.append(n.coords)
            n = n.parent

        return path

    # Returns the grid as a list
    def flatten(self):
        flat = []
        for _, e in self:
            flat.append(e)
        return flat

    def __repr__(self):
        string = ""
        for y in range(self.height):
            for x in range(self.width):
                e = self[x, y]
                if e is not None:
                    string += str(e) + " "
                else:
                    string += ". "
            string += "\n"

        return string

    def __iter__(self):
        for y in range(self.height):
            for x in range(self.width):
                yield Coord(x,y), self[x, y]

    def __getitem__(self, keys):
        if isinstance(keys, tuple):
            # Tuple can be both (x,y) and a slice
            if isinstance(keys[0], slice):
                # Slice
                xslice = keys[0].indices(self.width)
                yslice = keys[1].indices(self.height)

                matrix = []
                for y in range(yslice[0], yslice[1]):
                    row = []
                    for x in range(xslice[0], xslice[1]):
                        row.append(self[x, y])
                    matrix.append(row)

                new_grid = Grid2D.from_2d_list(matrix)
                return new_grid
            else:
                # Tuple
                if keys in self.grid:
                    return self.grid[Coord(keys[0], keys[1])]
            return None
        elif isinstance(keys, Coord):
            # Coord
            if keys in self.grid:
                return self.grid[keys]
            return None
        else:
            raise TypeError("Grid can't get element with key type {}".format(type(keys)))

    def __setitem__(self, keys, item):
        if isinstance(keys, tuple):
            self.grid[Coord(keys[0], keys[1])] = item
        elif isinstance(keys, Coord):
            self.grid[keys] = item
        else:
            raise TypeError("Grid can't set element with key type {}".format(type(keys)))
