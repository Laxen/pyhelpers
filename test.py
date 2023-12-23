from pyhelpers import intersect

cube1 = [(0, 10), (0, 10)]
cube2 = [(2, 8), (9, 30)]
overlap, non_overlaps = intersect(cube1, cube2)
assert overlap == [(2, 8), (9, 10)]
assert non_overlaps == [[(0, 2), (0, 10)], [(8, 10), (0, 10)], [(0, 10), (0, 9)]]

cube1 = [(0, 10), (0, 12)]
cube2 = [(5, 15), (7, 15)]
overlap, non_overlaps = intersect(cube1, cube2)
print(overlap)
print(non_overlaps)
