import sys
import math
import json
import pygame
from modules.map import Map

EVAL_MODE = False

pixel_constant = 50
display_width = 0
display_height = 0

COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gray': (127, 127, 127),
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'magenta': (255, 0, 255),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255)
}

game_display = None
robot = None
game_map = None

missing_color = 'white'
exit_col = 0
exit_row = 0

if not EVAL_MODE:
    pygame.init()
    robot_img = pygame.image.load('resources/images/robot_gray.png')
    robot_blue = pygame.image.load('resources/images/robot_blue.png')
    robot_red = pygame.image.load('resources/images/robot_red.png')
    robot_green = pygame.image.load('resources/images/robot_green.png')
    robot_magenta = pygame.image.load('resources/images/robot_magenta.png')
    robot_yellow = pygame.image.load('resources/images/robot_yellow.png')
    robot_cyan = pygame.image.load('resources/images/robot_cyan.png')
    run_button = pygame.image.load('resources/images/run.png')
    pygame.display.set_caption('Robot simulator')
    clock = pygame.time.Clock()

crashed = EVAL_MODE
reset = False
start = True

with open('resources/map.json') as json_file:
    map_info = json.load(json_file)


class Robot:
    def __init__(self, x: int, y: int, w: int, size: int,
                 col: int, row: int, direction: int) -> None:
        self.dir = direction
        self.x = x
        self.y = y
        self.col = col
        self.row = row
        self.w = w
        self.size = size
        self.offset = (pixel_constant - size)//2
        self.sensor_range = pixel_constant
        self.color = 'gray'
        self.movements = 0
        self.logic_calls = 0
        self.points = 0
        self.missing_color = 'white'
        self.white = False
        self.finished = False

    def set_position(self, x: int, y: int, w: int) -> None:
        if not EVAL_MODE:
            self.x = x
            self.y = y
            self.w = w
            box = [pygame.math.Vector2(p) for p in [(
                0, 0), (self.size, 0), (self.size, -self.size), (0, -self.size)]]
            box_rotate = [p.rotate(self.w) for p in box]
            min_box = (min(box_rotate, key=lambda p: p[0])[0],
                    min(box_rotate, key=lambda p: p[1])[1])
            max_box = (max(box_rotate, key=lambda p: p[0])[0],
                    max(box_rotate, key=lambda p: p[1])[1])
            pivot = pygame.math.Vector2(self.size//2, -self.size//2)
            pivot_rotate = pivot.rotate(self.w)
            pivot_move = pivot_rotate - pivot
            origin = (self.x - self.size//2 +
                    min_box[0] - pivot_move[0], self.y - self.size//2 - max_box[1] + pivot_move[1])
            if self.color == 'blue':
                rotated_image = pygame.transform.rotate(robot_blue, self.w)
            elif self.color == 'red':
                rotated_image = pygame.transform.rotate(robot_red, self.w)
            elif self.color == 'green':
                rotated_image = pygame.transform.rotate(robot_green, self.w)
            elif self.color == 'magenta':
                rotated_image = pygame.transform.rotate(robot_magenta, self.w)
            elif self.color == 'yellow':
                rotated_image = pygame.transform.rotate(robot_yellow, self.w)
            elif self.color == 'cyan':
                rotated_image = pygame.transform.rotate(robot_cyan, self.w)
            else:
                rotated_image = pygame.transform.rotate(robot_img, self.w)
            game_display.blit(rotated_image, origin)
            pygame.display.update()
            clock.tick(120)
        return
    
    def detect_white(self, old_row, olr_col) -> None:
        if self.white:
            return
        game_map.tiles[self.row][self.col].touched = True
        game_map.tiles[old_row][olr_col].touched = True
        for r in range(game_map.height):
            for c in range(game_map.width):
                if not game_map.tiles[r][c].touched:
                    return
        if game_map.tiles[self.row][self.col].color == 'white':
            self.white = True
            self.points += 30
            print('On white square after exploring the entire labyrinth: +30')
            generate_map()
        return
    
    def move_forward(self) -> None:
        # Map dir:
        #   0 -> north
        #   1 -> west
        #   2 -> south
        #   3 -> east
        if self.finished:
            return
        if self._get_distance(0):
            self.movements += 1
            factor = ((-1, 0), (0, -1), (1, 0), (0, 1))
            self.row += factor[self.dir][0]
            self.col += factor[self.dir][1]
            if not EVAL_MODE:
                for _ in range(pixel_constant):
                    rad = math.radians(self.w)
                    x1 = round(math.cos(rad)) + self.x
                    y1 = self.y - round(math.sin(rad))
                    generate_map()
                    self.set_position(x1, y1, self.w)
            self.detect_white(self.row - factor[self.dir][0], self.col - factor[self.dir][1])
        return

    def rotate_right(self) -> None:
        if self.finished:
            return
        self.movements += 1
        self.dir = (self.dir - 1 + 4) % 4
        if not EVAL_MODE:
            for _ in range(30):
                generate_map()
                self.set_position(self.x, self.y, self.w - 3)
        return

    def rotate_left(self) -> None:
        if self.finished:
            return
        self.movements += 1
        self.dir = (self.dir + 1) % 4
        if not EVAL_MODE:
            for _ in range(30):
                generate_map()
                self.set_position(self.x, self.y, self.w + 3)
        return

    def ultrasonic_front(self) -> int:
        if self.finished:
            return -1
        self.logic_calls += 1
        return self._get_distance(0)

    def ultrasonic_right(self) -> int:
        if self.finished:
            return -1
        self.logic_calls += 1
        return self._get_distance(1)

    def ultrasonic_left(self) -> int:
        if self.finished:
            return -1
        self.logic_calls += 1
        return self._get_distance(2)

    def _get_distance(self, dir_ultrasonic: int) -> int:
        # dir:
        #   Front: 0
        #   Right: 1
        #   Left: 2
        # Map dir:
        #   0 -> north
        #   1 -> west
        #   2 -> south
        #   3 -> east
        dirs = [[0, 1, 2, 3],
                [3, 0, 1, 2],
                [1, 2, 3, 0]]

        distance = None
        start_dist = 0
        distance_direction = dirs[dir_ultrasonic][self.dir]

        if distance_direction == 0:
            # row-- until 0
            for row in range(self.row, -1, -1):
                if game_map.tiles[row][self.col].north.status == 1:
                    distance = start_dist
                    break
                start_dist += 1
            if distance is None:
                return -1

        if distance_direction == 1:
            # col-- until 0
            for col in range(self.col, -1, -1):
                if game_map.tiles[self.row][col].west.status == 1:
                    distance = start_dist
                    break
                start_dist += 1
            if distance is None:
                return -1

        if distance_direction == 2:
            # row++ until max
            for row in range(self.row, game_map.height):
                if game_map.tiles[row][self.col].south.status == 1:
                    distance = start_dist
                    break
                start_dist += 1
            if distance is None:
                return -1

        if distance_direction == 3:
            # col++ until max
            for col in range(self.col, game_map.width):
                if game_map.tiles[self.row][col].east.status == 1:
                    distance = start_dist
                    break
                start_dist += 1
            if distance is None:
                return -1
        if not EVAL_MODE:
            pygame.display.update()
            clock.tick(120)
        return distance

    def get_color(self) -> str:
        if self.finished:
            return ''
        self.logic_calls += 1
        row = self.row
        col = self.col
        if game_map.tiles[row][col].color:
            return game_map.tiles[row][col].color
        return 'white'

    def display_color(self, color: str) -> None:
        if self.finished:
            return
        self.logic_calls += 1
        row = self.row
        col = self.col
        tile_color = game_map.tiles[row][col].color
        if not game_map.tiles[row][col].color_identified and tile_color == 'white' and color == missing_color:
            game_map.tiles[row][col].color_identified = True
            self.points += 20
            print(f'Missing color successfully identified: {missing_color} +5')
            self.color = color
            self.set_position(self.x, self.y, self.w)
            self.color = 'gray'
            if not EVAL_MODE:
                pygame.time.delay(500)
                self.set_position(self.x, self.y, self.w)
        elif not game_map.tiles[row][col].color_identified and color == tile_color and color != 'white':
            game_map.tiles[row][col].color_identified = True
            self.points += 5
            print(f'Color successfully identified: {color} +5')
            self.color = color
            self.set_position(self.x, self.y, self.w)
            self.color = 'gray'
            if not EVAL_MODE:
                pygame.time.delay(500)
                self.set_position(self.x, self.y, self.w)
        return

    def finish_round(self) -> None:
        self.logic_calls -= 1
        if self.col == exit_col and self.row == exit_row:
            self.points += 30
            print('Arrived correctly to exit: +30')
        generate_map()
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('Program finished!')
        print("Total points: ", self.points)
        print("Total movements: ", self.movements)
        print("Total logic calls: ", self.logic_calls)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        self.finished = True
        return

    def debug_tile(self) -> None:
        print("(~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~)")
        print("Color: ", game_map.tiles[self.row][self.col].color)
        print("north: ", game_map.tiles[self.row][self.col].north.status,
              game_map.tiles[self.row][self.col].north.data)
        print("south: ", game_map.tiles[self.row][self.col].south.status,
              game_map.tiles[self.row][self.col].south.data)
        print("east: ", game_map.tiles[self.row][self.col].east.status,
              game_map.tiles[self.row][self.col].east.data)
        print("west: ", game_map.tiles[self.row][self.col].west.status,
              game_map.tiles[self.row][self.col].west.data)
        print("(~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~)")
        return


def generate_map() -> None:
    if EVAL_MODE:
        return
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    game_display.fill(COLORS['white'])

    for row in range(game_map.height):
        for col in range(game_map.width):
            # Tile color
            if game_map.tiles[row][col].color:
                x = col * pixel_constant
                y = row * pixel_constant
                c = COLORS[game_map.tiles[row][col].color]
                pygame.draw.rect(
                    game_display, c, (x, y, pixel_constant, pixel_constant))

            # Tile walls in north, south, east and west order
            x1 = [0, 0, 1, 0]
            y1 = [0, 1, 0, 0]
            x2 = [1, 1, 1, 0]
            y2 = [0, 1, 1, 1]
            wall_colors = [None, ['red', 'blue', 'black']]
            direction = ["north", "south", "east", "west"]
            # Wall shifting towards the center
            shift_x = [0, 0, -1, 1]
            shift_y = [1, -1, 0, 0]
            for wall_order in range(4):
                direction_status = getattr(
                    getattr(game_map.tiles[row][col], direction[wall_order]), "status")
                if direction_status != 0:
                    x1_pixel = (col + x1[wall_order]) * pixel_constant + \
                        shift_x[wall_order] * pixel_constant * 0.02
                    x2_pixel = (col + x2[wall_order]) * pixel_constant + \
                        shift_x[wall_order] * pixel_constant * 0.02
                    y1_pixel = (row + y1[wall_order]) * pixel_constant + \
                        shift_y[wall_order] * pixel_constant * 0.02
                    y2_pixel = (row + y2[wall_order]) * pixel_constant + \
                        shift_y[wall_order] * pixel_constant * 0.02
                    color = wall_colors[direction_status]
                    if isinstance(color, list):
                        color = color[-1]
                    pygame.draw.line(game_display, COLORS[color], 
                                     (x1_pixel, y1_pixel), (x2_pixel, y2_pixel), 5)

    movements = robot.movements if robot else 0
    logic_calls = robot.logic_calls if robot else 0
    points = robot.points if robot else 0

    myfont = pygame.font.SysFont('Arial', 12)
    textsurface = myfont.render(f'Movements = {movements}', False, (0, 0, 0))
    game_display.blit(textsurface, (pixel_constant * (map_info['size']['w'] + 0.2),
                                    pixel_constant*0.2))
    textsurface = myfont.render(f'Logic calls = {logic_calls}', False, (0, 0, 0))
    game_display.blit(textsurface, (pixel_constant * (map_info['size']['w'] + 0.2),
                                    1.2*pixel_constant))
    textsurface = myfont.render(f'Points = {points}', False, (0, 0, 0))
    game_display.blit(textsurface, (pixel_constant * (map_info['size']['w'] + 0.2),
                                    2.2*pixel_constant))
    return


def is_valid_coordinate(row: int, col: int) -> bool:
    if row >= game_map.height or row < 0:
        return False
    if col >= game_map.width or col < 0:
        return False
    return True


def setup_map() -> None:
    global display_width
    global display_height
    global pixel_constant
    global game_display
    global game_map
    global missing_color
    global exit_col
    global exit_row

    if not EVAL_MODE:
        pixel_constant = map_info['squareSize'] if map_info['squareSize'] else pixel_constant
        display_width = map_info['size']['w'] * pixel_constant
        display_height = map_info['size']['h'] * pixel_constant
        game_display = pygame.display.set_mode(
            (display_width + int(pixel_constant*2), display_height))

    # Map initialization
    game_map = Map(map_info['size']['w'], map_info['size']['h'])
    direction = ["north", "south", "east", "west"]
    dir_reflection = ["south", "north", "west", "east"]
    dir_reflection_xy = [(-1, 0), (1, 0), (0, 1), (0, -1)]

    color_count = {'blue': 0, 'red': 0, 'green': 0, 'magenta': 0, 'yellow': 0, 'cyan': 0, 'white': 0}

    for tile in map_info['tiles']:
        game_map.tiles[tile['row']][tile['col']].color = tile['color']
        color_count[tile['color']] += 1
        for dir_index in range(len(direction)):
            if getattr(getattr(game_map.tiles[tile['row']][tile['col']],
                               direction[dir_index]), "status") == 0:
                setattr(getattr(game_map.tiles[tile['row']][tile['col']],
                                direction[dir_index]), "status", tile['directions'][dir_index])
            if tile['directions'][dir_index]:
                new_row = tile['row'] + dir_reflection_xy[dir_index][0]
                new_col = tile['col'] + dir_reflection_xy[dir_index][1]
                if is_valid_coordinate(new_row, new_col):
                    setattr(getattr(game_map.tiles[new_row][new_col],
                                    dir_reflection[dir_index]), "status", 1)
    for i in range(map_info['size']['w']):
        game_map.tiles[0][i].north.status = 1
        game_map.tiles[map_info['size']['h']-1][i].south.status = 1
    for i in range(map_info['size']['h']):
        game_map.tiles[i][0].west.status = 1
        game_map.tiles[i][map_info['size']['w']-1].east.status = 1

    for key, val in color_count.items():
        if val == 7:
            missing_color = key
            break

    exit_col = 0
    exit_row = 0

    for i in range(map_info['size']['w']):
        color_diff = set()
        color_count = {'blue': 0, 'red': 0, 'green': 0, 'magenta': 0, 'yellow': 0, 'cyan': 0, 'white': 0}
        for j in range(map_info['size']['h']):
            color_diff.add(game_map.tiles[j][i].color)
            color_count[game_map.tiles[j][i].color] += 1
        for key, val in color_count.items():
            if val >= 3:
                exit_col += 1
                break
        color_diff.discard('white')
        exit_col += len(color_diff) == 6

    for j in range(map_info['size']['h']):
        color_diff = set()
        color_count = {'blue': 0, 'red': 0, 'green': 0, 'magenta': 0, 'yellow': 0, 'cyan': 0, 'white': 0}
        for i in range(map_info['size']['w']):
            color_diff.add(game_map.tiles[j][i].color)
            color_count[game_map.tiles[j][i].color] += 1
        for key, val in color_count.items():
            if val >= 3:
                exit_row += 2
                break
        color_diff.discard('white')
        exit_row += (len(color_diff) == 6) * 2
    generate_map()
    return


def setup_robot() -> None:
    global robot
    robot_size = 0
    if not EVAL_MODE:
        global robot_img
        global robot_blue
        global robot_red
        global robot_green
        global robot_magenta
        global robot_yellow
        global robot_cyan

        robot_size = int(pixel_constant * 0.5)
        robot_img = pygame.transform.scale(robot_img, (robot_size, robot_size))
        robot_blue = pygame.transform.scale(robot_blue, (robot_size, robot_size))
        robot_red = pygame.transform.scale(robot_red, (robot_size, robot_size))
        robot_green = pygame.transform.scale(robot_green, (robot_size, robot_size))
        robot_magenta = pygame.transform.scale(robot_magenta, (robot_size, robot_size))
        robot_yellow = pygame.transform.scale(robot_yellow, (robot_size, robot_size))
        robot_cyan = pygame.transform.scale(robot_cyan, (robot_size, robot_size))
        gameIcon = pygame.image.load('resources/images/roborregos_logo.PNG')
        pygame.display.set_icon(gameIcon)

    col = map_info['robot_start']['col']
    row = map_info['robot_start']['row']

    start_x = col * pixel_constant + robot_size
    start_y = row * pixel_constant + robot_size
    angle = map_info['robot_start']['w']
    dic_dir = {0: 3, 90: 0, 180: 1, 270: 2}
    direction = dic_dir[angle]

    robot = Robot(start_x, start_y, angle, robot_size, col, row, direction)
    robot.set_position(start_x, start_y, angle)
    return


def main() -> None:
    setup_map()
    setup_robot()
    with open("main_program.py") as f:
        code = compile(f.read(), "main_program.py", 'exec')
        exec(code)
    return


if __name__ == "__main__":
    if EVAL_MODE:
        print('Round start')
        try:
            main()
        except Exception as e:
            print("Error:", e)
            print("Program crashes")
        if EVAL_MODE:
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print('Eval Results')
            print("Total points: ", robot.points)
            print("Total movements: ", robot.movements)
            print("Total logic calls: ", robot.logic_calls)
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('Round end')

    while not crashed:
        if start:
            setup_map()
            setup_robot()
            start = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[0] < pixel_constant * 0.5 and pos[1] < pixel_constant * 0.5:
                    if not reset:
                        reset = True

        if reset:
            print('Round start')
            main()
            print('Round end')
            reset = False
        else:
            run_button = pygame.transform.scale(
                run_button, (int(pixel_constant*0.5), int(pixel_constant*0.5)))
            game_display.blit(run_button, (0, 0))
            pygame.display.update()
            clock.tick(120)
    
    if not EVAL_MODE:
        pygame.quit()
    sys.exit()