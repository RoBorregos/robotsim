import json
import random

height = 8
width = 6
colored_tile = ["red", "blue", "green", "magenta", "yellow", "cyan"] * 8
white = random.choice(colored_tile)
colored_tile.remove(white)
colored_tile.append("white")
posible_walls = [
    [0, 0, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 1, 0, 0],
    [0, 1, 0, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 1, 0],
    [1, 1, 0, 0],
]

game_map = {}
game_map["squareSize"] = 100
game_map["size"] = {"w": width, "h": height}
game_map["robot_start"] = {"row": 0, "col": 5, "w": 270}
game_map["tiles"] = []

for row in range(height):
    for col in range(width):
        tile = {}
        color = random.choice(colored_tile)
        colored_tile.remove(color)
        directions = random.choice(posible_walls)
        tile = {
            "row": row,
            "col": col,
            "color": color,
            "directions": directions,
        }
        game_map["tiles"].append(tile)

with open('resources/mapN.json', 'w') as outfile:
    json.dump(game_map, outfile)
