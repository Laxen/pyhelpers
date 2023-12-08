import math
import re

class Coord:
    def __init__(self, x, y, z=None):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z) if z != None else None

    # Returns a Coord from a string with format "x,y(,z)"
    @classmethod
    def from_string(cls, string):
        s = string.split(",")
        if len(s) == 3:
            return cls(s[0], s[1], s[2])
        else:
            return cls(s[0], s[1])

    # Returns the squared distance from this Coord to another Coord
    def distance2_to(self, other):
        if self.z == None and other.z == None:
            return (self.x - other.x)**2 + (self.y - other.y)**2
        return (self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2

    def __repr__(self):
        if self.z == None:
            return "({},{})".format(self.x, self.y)
        return "({},{},{})".format(self.x, self.y, self.z)

    def __sub__(self, other):
        if self.z == None and other.z == None:
            return Coord(self.x - other.x, self.y - other.y)
        return Coord(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other):
        if self.z == None and other.z == None:
            return Coord(self.x + other.x, self.y + other.y)
        return Coord(self.x + other.x, self.y + other.y, self.z + other.z)

    def __eq__(self, other):
        if isinstance(other, Coord):
            return self.x == other.x and self.y == other.y and self.z == other.z
        elif isinstance(other, tuple):
            if self.z == None and len(other) == 2:
                return self.x == other[0] and self.y == other[1]
            return self.x == other[0] and self.y == other[1] and self.z == other[2]
        else:
            raise TypeError("Can't compare Coord to type {}".format(type(other)))

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            raise KeyError()

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise KeyError()

class Grid:
    def __init__(self, element, width, height, depth=None):
        self.width = width
        self.height = height
        self.depth = depth

        self.grid = dict()
        for z in range(depth if depth != None else 1):
            for y in range(self.height):
                for x in range(self.width):
                    if depth == None:
                        self[x, y] = element
                    else:
                        self[x, y, z] = element

    # Returns a Grid with elements initialized from a 2D list
    @classmethod
    def from_2d_list(cls, list_2d):
        grid = Grid(0, len(list_2d[0]), len(list_2d))
        for c, _ in grid:
            grid[c] = list_2d[c.y][c.x]
        return grid

    # Returns a Grid with Coords from coords_list set to element and the rest
    # set to 0
    @classmethod
    def from_coords(cls, coords_list, element):
        if coords_list[0].z == None:
            grid = Grid(0, 0, 0)
        else:
            grid = Grid(0, 0, 0, 0)

        for c in coords_list:
            grid.width = max(grid.width, c.x + 1)
            grid.height = max(grid.height, c.y + 1)
            if grid.depth != None:
                grid.depth = max(grid.depth, c.z + 1)
            grid[c] = element

        return grid

    # Returns a dict with the neighbors for a given Coord
    # TODO: Fix for 3D
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
    # TODO: Fix for 3D
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
        path_grid = Grid(0, self.width, self.height)
        for c, _ in path_grid:
            n = Node(c, self[c])
            n.h = start.distance2_to(end)
            path_grid[c] = n

        # Init the openset with the start node
        openset = [path_grid[start]]
        path_grid[start].g = 0

        foundpath = False
        while len(openset) > 0:
            # Sorts the openset so the cheapest node is at the end, then we pop it off
            list.sort(openset, reverse=True)
            current = openset.pop()

            if current.coords == end:
                foundpath = True
                break

            for c, n in path_grid.neighbors(current.coords, diagonal=False).items():
                new_g = current.g + n.cost

                # This is a cheaper way to reach this node, update it
                if new_g < n.g:
                    n.parent = current
                    n.g = new_g

                    if n not in openset:
                        openset.append(n)

        if not foundpath:
            return None

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
        for z in range(self.depth if self.depth != None else 1):
            if self.depth != None:
                string += "z: " + str(z) + "\n"
            for y in range(self.height):
                for x in range(self.width):
                    e = self[x, y] if self.depth == None else self[x, y, z]
                    if e is not None:
                        string += str(e) + " "
                    else:
                        string += ". "
                string += "\n"

        return string

    def __iter__(self):
        for z in range(self.depth if self.depth != None else 1):
            for y in range(self.height):
                for x in range(self.width):
                    if self.depth == None:
                        yield Coord(x, y), self[x, y]
                    else:
                        yield Coord(x, y, z), self[x, y, z]

    def __getitem__(self, key):
        if isinstance(key, tuple):
            # Tuple can be (x,y), (x, y, z) or a slice
            if isinstance(key[0], slice):
                # Slice
                xslice = key[0].indices(self.width)
                yslice = key[1].indices(self.height)

                if self.depth == None:
                    new_grid = Grid(0, xslice[1] - xslice[0], yslice[1] - yslice[0])
                    for new_y, grid_y in enumerate(range(yslice[0], yslice[1])):
                        for new_x, grid_x in enumerate(range(xslice[0], xslice[1])):
                            new_grid[new_x, new_y] = self[grid_x, grid_y]
                else:
                    zslice = key[2].indices(self.depth)
                    new_grid = Grid(0, xslice[1] - xslice[0], yslice[1] - yslice[0], zslice[1] - zslice[0])
                    for new_z, grid_z in enumerate(range(zslice[0], zslice[1])):
                        for new_y, grid_y in enumerate(range(yslice[0], yslice[1])):
                            for new_x, grid_x in enumerate(range(xslice[0], xslice[1])):
                                new_grid[new_x, new_y, new_z] = self[grid_x, grid_y, grid_z]
                return new_grid
            else:
                # Tuple
                c = Coord(*key)
                if c in self.grid:
                    return self.grid[c]
            return None
        elif isinstance(key, Coord):
            # Coord
            if key in self.grid:
                return self.grid[key]
            return None
        else:
            raise TypeError("Grid can't get element with key type {}".format(type(key)))

    def __setitem__(self, key, item):
        if isinstance(key, tuple):
            # Tuple can be (x,y), (x, y, z) or a slice
            if isinstance(key[0], slice):
                # Slice
                xslice = key[0].indices(self.width)
                yslice = key[1].indices(self.height)

                if self.depth == None:
                    for grid_y in range(yslice[0], yslice[1]):
                        for grid_x in range(xslice[0], xslice[1]):
                            self.grid[grid_x, grid_y] = item
                else:
                    zslice = key[2].indices(self.depth)
                    for grid_z in range(zslice[0], zslice[1]):
                        for grid_y in range(yslice[0], yslice[1]):
                            for grid_x in range(xslice[0], xslice[1]):
                                self.grid[grid_x, grid_y, grid_z] = item
            else:
                # Tuple
                self.grid[Coord(*key)] = item
        elif isinstance(key, Coord):
            self.grid[key] = item
        else:
            raise TypeError("Grid can't set element with key type {}".format(type(key)))

class Cube:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    # Calculate the intersecting Cube between two Cubes
    # other: The Cube to intersect with
    # returns: The intersecting Cube
    def intersect(self, other):
        intersect = Cube(Coord(0,0,0), Coord(0,0,0))

        for d in range(3):
            # Case 1, 2, 3 (other to the right of, or inside, self)
            if other.start[d] >= self.start[d]:
                # Case 1 (other fully to the right of self, no intersection)
                if other.start[d] >= self.end[d]:
                    return None

                # Case 3 (other fully inside self)
                if other.end[d] <= self.end[d]:
                    intersect.start[d] = other.start[d]
                    intersect.end[d] = other.end[d]
                    continue

                # Case 2 (other partially inside self)
                intersect.start[d] = other.start[d]
                intersect.end[d] = self.end[d]
            # Case 4, 5, 6 (self to the right of, or inside, other)
            else:
                # Case 6 (self fully to the right of other, no intersection)
                if self.start[d] >= other.end[d]:
                    return None

                # Case 4 (self fully inside other)
                if self.end[d] <= other.end[d]:
                    intersect.start[d] = self.start[d]
                    intersect.end[d] = self.end[d]
                    continue

                # Case 5 (self partially inside other)
                intersect.start[d] = self.start[d]
                intersect.end[d] = other.end[d]
        return intersect

    # Subtract other from self
    # other: Cube that is guaranteed to be inside self
    # return: List of Cubes making up self after subtraction
    def subtract(self, other):
        res = []

        def subtract_1d(self, other, d):
            cubes = []

            c1 = Cube(Coord(0,0,0), Coord(0,0,0))
            c1.start[d] = self.start[d]
            c1.end[d] = other.start[d]
            if c1.start[d] != c1.end[d]:
                cubes.append(c1)

            c2 = Cube(Coord(0,0,0), Coord(0,0,0))
            c2.start[d] = other.end[d]
            c2.end[d] = self.end[d]
            if c2.start[d] != c2.end[d]:
                cubes.append(c2)

            return cubes

        sub_x = subtract_1d(self, other, 0)
        for c in sub_x:
            c.start.y = self.start.y
            c.end.y = self.end.y
            c.start.z = self.start.z
            c.end.z = self.end.z
            res.append(c)

        sub_y = subtract_1d(self, other, 1)
        for c in sub_y:
            c.start.x = other.start.x
            c.end.x = other.end.x
            c.start.z = self.start.z
            c.end.z = self.end.z
            res.append(c)

        sub_z = subtract_1d(self, other, 2)
        for c in sub_z:
            c.start.x = other.start.x
            c.end.x = other.end.x
            c.start.y = other.start.y
            c.end.y = other.end.y
            res.append(c)

        return res

    @property
    def area(self):
        return abs(self.start.x - self.end.x) * \
               abs(self.start.y - self.end.y) * \
               abs(self.start.z - self.end.z)

    def __repr__(self):
        return "{} -> {}".format(self.start, self.end)

class Parser():
    # Parse each row as an int, return as list
    def row_to_int(input_file):
        with open(input_file) as file:
            ret = [int(line) for line in file]
        return ret

    # Find all ints in a row, return as list
    def ints_to_list(input_file):
        with open(input_file) as file:
            return [int(m) for m in re.findall(r'-?\d+', file.read())]

    def to_grid(input_file):
        matrix = []
        with open(input_file) as file:
            for line in file:
                row = [int(e) if e.isdigit() else e for e in line.rstrip()]
                matrix.append(row)
        return Grid.from_2d_list(matrix)

    def regex(input_file, regex):
        pattern = re.compile(regex)

        with open(input_file) as file:
            for line in file:
                search = pattern.search(line.rstrip())

                if search:
                    yield search.groups()

class HashGrid:
    def __init__(self):
        self.grid = {}

    def find(self, value):
        ret = []
        for key, val in self.grid.items():
            if val == value:
                ret.append(key)
        return ret

    def __repr__(self):
        max_x = max(key[0] for key in self.grid.keys())
        max_y = max(key[1] for key in self.grid.keys())
        min_x = min(key[0] for key in self.grid.keys())
        min_y = min(key[1] for key in self.grid.keys())

        array = [[0] * (max_x - min_x + 1) for _ in range(max_y - min_y + 1)]
        for key, value in self.grid.items():
            array[key[1] - min_y][key[0] - min_x] = value

        return "\n".join("".join(str(x) for x in row) for row in array)

    def __contains__(self, key):
        return key in self.grid

    def __getitem__(self, key):
        if key not in self.grid:
            return None
        return self.grid[key]

    def __setitem__(self, key, value):
        self.grid[key] = value

