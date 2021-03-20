import pygame
import json
import math
from modules.coord import Coord
from modules.map import Map
import sys

pixel_constant = 50
display_width = 0
display_height = 0

black = (0,0,0)
white = (255,255,255)
gray = (127,127,127)
red = (255,0,0)
blue = (0,0,255)
green = (0,255,0)
magenta = (255,0,255)
yellow = (255,255,0)
cyan = (0,255,255)

colors = {
    'black' : (0,0,0),
    'white' : (255,255,255),
    'gray' : (127,127,127),
    'red' : (255,0,0),
    'blue' : (0,0,255),
    'green' : (0,255,0),
    'pink' : (255,105,180),
    'yellow' : (255,255,0),
    'cyan' : (0,255,255)
}

gameDisplay = None
robot = None
map = None

pygame.init()
robotImg = pygame.image.load('images/robot.png')
run_button = pygame.image.load('images/run.png')
pygame.display.set_caption('Robot simulator')
clock = pygame.time.Clock()

crashed = False
reset = False
start = True

with open('resources/map.json') as json_file:
    map_info = json.load(json_file)


class Robot:
    def __init__(self,x,y,w,size,col,row,dir):
        self.dir = dir
        self.points = 0
        self.x = x
        self.y = y
        self.col = col
        self.row = row
        self.w = w
        self.size = size
        self.offset = (pixel_constant - size)//2
        self.sensor_range = pixel_constant
        self.set_position(x,y,w)
        self.broken = False
        
    def set_position(self,x,y,w):
        self.x = x
        self.y = y
        self.w = w
        box = [pygame.math.Vector2(p) for p in [(0, 0), (self.size, 0), (self.size, -self.size), (0, -self.size)]]
        box_rotate = [p.rotate(self.w) for p in box]
        min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
        max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])
        pivot = pygame.math.Vector2(self.size//2, -self.size//2)
        pivot_rotate = pivot.rotate(self.w)
        pivot_move = pivot_rotate - pivot
        origin = (self.x - self.size//2 + min_box[0] - pivot_move[0], self.y - self.size//2 - max_box[1] + pivot_move[1])
        rotated_image = pygame.transform.rotate(robotImg, self.w)
        gameDisplay.blit(rotated_image, origin)
        pygame.display.update()
        clock.tick(120)

    def move_forward(self):
        # Map dir:
        #   0 -> North
        #   1 -> West
        #   2 -> South
        #   3 -> East
        if self.distanciaFrente():
            if self.dir == 0:
                self.row -= 1
            if self.dir == 1:
                self.col -= 1
            if self.dir == 2:
                self.row += 1
            if self.dir == 3:
                self.col += 1
            for _ in range(pixel_constant):
                angle = self.w
                x1 = self.x 
                y1 = self.y 
                rad = math.radians(angle)
                x2 = round(math.cos(rad)) + x1
                y2 = y1 - round(math.sin(rad))
                generate_map()
                self.set_position(x2,y2,angle)

    def move_backward(self):
        # Map dir:
        #   0 -> North
        #   1 -> West
        #   2 -> South
        #   3 -> East
        if self.distanciaAtras():
            if self.dir == 0:
                self.row += 1
            if self.dir == 1:
                self.col += 1
            if self.dir == 2:
                self.row -= 1
            if self.dir == 3:
                self.col -= 1
            for _ in range(pixel_constant):
                angle = self.w
                x1 = self.x 
                y1 = self.y 
                rad = math.radians(angle)
                x2 = x1 - round(math.cos(rad))
                y2 = y1 + round(math.sin(rad))
                generate_map()
                self.set_position(x2,y2,angle)
    
    def rotate_right(self):
        self.dir = (self.dir - 1 + 4) % 4
        for _ in range(30):
            generate_map()
            self.set_position(self.x,self.y,self.w - 3)

    def rotate_left(self):
        self.dir = (self.dir + 1) % 4
        for _ in range(30):
            generate_map()
            self.set_position(self.x,self.y,self.w + 3)

    def distanciaFrente(self):
        return self.__getDistance(0)

    def distanciaAtras(self):
        return self.__getDistance(1)

    def izqAdelante(self, value):
        self.izqFront = bool(value)

    def izqAtras(self, value):
        self.izqBack = bool(value)

    def derAdelante(self, value):
        self.derFront = bool(value)

    def derAtras(self, value):
        self.derBack = bool(value)

    # pins: [left_front, left_back, right_front, right_back]
    def prenderMotor(self):
        # move forward
        power_pins = [self.izqFront, self.izqBack, self.derFront, self.derBack]
        if power_pins == [True,False,True,False]:
            self.move_forward()
        elif power_pins == [False,True,False,True]:
            self.move_backward()
        elif power_pins == [True,False,False,True]:
            self.rotate_right()
        elif power_pins == [False,True,True,False]:
            self.rotate_left()


    def __getDistance(self, val):
        # dir:
        #   Front: 0
        #   Right: 1
        #   Left: 2
        # Map dir:
        #   0 -> North
        #   1 -> West
        #   2 -> South
        #   3 -> East
        dirs = [[0, 1, 2, 3],
                [2, 3, 0, 1]]

        distance = None
        start = 0
        distance_direction = dirs[val][self.dir]

        if distance_direction == 0:
            # row-- until 0
            for pos in range(self.row, -1, -1):
                if map.tiles[pos][self.col].North.status == 1:
                    distance = start
                    break
                start += 1
            if distance == None:
                return -1 
            
        if distance_direction == 1:
            # col-- until 0 
            for pos in range(self.col, -1, -1):
                if map.tiles[self.row][pos].West.status == 1:
                    distance = start
                    break
                start += 1
            if distance == None:
                return -1 

        if distance_direction == 2:
            # row++ until max
            for pos in range(self.row, map.height):
                if map.tiles[pos][self.col].South.status == 1:
                    distance = start
                    break
                start += 1
            if distance == None:
                return -1

        if distance_direction == 3:
            # col++ until max
            for pos in range(self.col, map.width):
                if map.tiles[self.row][pos].East.status == 1:
                    distance = start
                    break
                start += 1
            if distance == None:
                return -1 
        pygame.display.update()
        clock.tick(120)
        return distance

    def __debugTile(self):
        print("(~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~)")
        print("Position:", self.row, self.col,)
        print("Color: ", map.tiles[self.row][self.col].color)
        print("Color: ", map.tiles[self.row][self.col].envType)
        print("North: ", map.tiles[self.row][self.col].North.status)
        print("South: ", map.tiles[self.row][self.col].South.status)
        print("East: ", map.tiles[self.row][self.col].East.status)
        print("West: ", map.tiles[self.row][self.col].West.status)
        print("Front", self.distanciaFrente())
        print("Left", self.ultrasonicLeft())
        print("Right", self.ultrasonicRight())
        print("(~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~)")

    def __debugSpecificTile(self, row, col):
        print("(~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~)")
        print("Position:", row, col,)
        print("Color: ", map.tiles[row][col].color)
        print("Color: ", map.tiles[row][col].envType)
        print("North: ", map.tiles[row][col].North.status)
        print("South: ", map.tiles[row][col].South.status)
        print("East: ", map.tiles[row][col].East.status)
        print("West: ", map.tiles[row][col].West.status)
        print("(~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~)")

    

def generate_map():
    gameDisplay.fill(white)

    for row in range(map.height):
        for col in range(map.width):
            #Tile walls in North, South, East and West order
            x1 = [0, 0, 1, 0]
            y1 = [0, 1, 0, 0]
            x2 = [1, 1, 1, 0]
            y2 = [0, 1, 1, 1]
            dir = ["North","South","East","West"]
            #Wall shifting towards the center
            shift_x = [0, 0, -1, 1]
            shift_y = [1, -1, 0, 0]
            for wall_order in range(4):
                direction_status = getattr(getattr(map.tiles[row][col], dir[wall_order]),"status")
                if direction_status  != 0 :
                    x1_pixel = (col + x1[wall_order]) * pixel_constant + shift_x[wall_order] * pixel_constant * 0.02
                    x2_pixel = (col + x2[wall_order]) * pixel_constant + shift_x[wall_order] * pixel_constant * 0.02
                    y1_pixel = (row + y1[wall_order]) * pixel_constant + shift_y[wall_order] * pixel_constant * 0.02
                    y2_pixel = (row + y2[wall_order]) * pixel_constant + shift_y[wall_order] * pixel_constant * 0.02
                    color = "black"
                    pygame.draw.line(gameDisplay, colors[color], (x1_pixel, y1_pixel), (x2_pixel, y2_pixel),5)


def setup_map():
    global display_width 
    global display_height 
    global pixel_constant
    global gameDisplay
    global map

    pixel_constant = map_info['squareSize'] if map_info['squareSize'] else pixel_constant
    display_width = map_info['size']['w'] * pixel_constant
    display_height = map_info['size']['h'] * pixel_constant

    gameDisplay = pygame.display.set_mode((display_width, display_height))

    #Map initialization
    map = Map(map_info['size']['w'],map_info['size']['h'])
    dir = ["North","South","East","West"]
    dir_reflection = ["South","North","West","East"]
    dir_reflection_xy = [(-1,0),(1,0),(0,1),(0,-1)]
    for tile in map_info['tiles']:
        for dir_index in range(len(dir)):
            if getattr(getattr(map.tiles[tile['row']][tile['col']], dir[dir_index]), "status") == 0:
                setattr(getattr(map.tiles[tile['row']][tile['col']], dir[dir_index]), "status", tile['directions'][dir_index])
            if tile['directions'][dir_index] == 1:
                new_row = tile['row'] + dir_reflection_xy[dir_index][0]
                new_col = tile['col'] + dir_reflection_xy[dir_index][1]
                if map.is_valid_coordinate(new_row, new_col):
                    setattr(getattr(map.tiles[new_row][new_col], dir_reflection[dir_index]), "status", 1)
    generate_map()


def setup_robot():
    # Map dir:
        #   0 -> North
        #   1 -> West
        #   2 -> South
        #   3 -> East
    global robot
    global robotImg

    robot_size = int(pixel_constant * 0.5)
    robotImg = pygame.transform.scale(robotImg, (robot_size, robot_size))
    gameIcon = pygame.image.load('images/roborregos_logo.PNG')
    pygame.display.set_icon(gameIcon)
    
    col = map_info['robot_start']['col']
    row = map_info['robot_start']['row']

    start_x = col * pixel_constant + robot_size
    start_y = row * pixel_constant + robot_size
    angle = map_info['robot_start']['w']
    dic_dir = {0:3, 90:0, 180:1, 270:2}
    dir = dic_dir[angle]
    
    robot = Robot(start_x,start_y,angle,robot_size,col,row,dir)


def main():
    setup_map()
    setup_robot()
    with open("main_program.py") as f:
        code = compile(f.read(), "main_program.py", 'exec')
        exec(code)


if __name__ == "__main__":
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
            main()
            reset = False
        else:
            run_button = pygame.transform.scale(run_button, (int(pixel_constant*0.5), int(pixel_constant*0.5)))
            gameDisplay.blit(run_button, (0, 0))
            pygame.display.update()
            clock.tick(120)

    pygame.quit()
    quit()
