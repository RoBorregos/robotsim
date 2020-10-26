import pygame
import json
import math
from modules.coord import Coord
from modules.map import Map

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

crashed = False
reset = False
start = True

with open('resources/default.json') as json_file:
    map_info = json.load(json_file)


class Robot:
    def __init__(self,x,y,w,size,col,row,dir):
        self.dir = dir
        self.movements = 0
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
        print('Position:', y, x, w)

    def move_forward(self):
        # Map dir:
        #   0 -> North
        #   1 -> West
        #   2 -> South
        #   3 -> East
        if self.movements >= 300 and not self.broken:
            self.broken = True
            print('---------------->Out of movements')
        if not self.broken:
            self.movements += 1
            print('Moving forward, total movements:', self.movements)
            if self.ultrasonicFront():
                if self.dir == 0:
                    self.row -= 1
                if self.dir == 1:
                    self.col -= 1
                if self.dir == 2:
                    self.row += 1
                if self.dir == 3:
                    self.col += 1
                self.set_position(self.col,self.row,self.w)
                if map.tiles[self.row][self.col].envType == "fire":
                    #finish
                    self.broken = True
                    print('---------------->Robot eliminated by fire!')
                if map.tiles[self.row][self.col].envType == "collapse":
                    if map.tiles[self.row][self.col].envData:
                        #finish
                        self.broken = True
                        print('---------------->Robot stuck in collapsed zone!')
                    map.tiles[self.row][self.col].envData = 1
    
    def rotate_right(self):
        if self.movements >= 300 and not self.broken:
            self.broken = True
            print('---------------->Out of movements')
        if not self.broken:
            self.movements += 1
            print('Rotating right, total movements:', self.movements)
            self.dir = (self.dir - 1 + 4) % 4
            self.set_position(self.x,self.y,(self.w - 90)%360)

    def rotate_left(self):
        if self.movements >= 300 and not self.broken:
            self.broken = True
            print('---------------->Out of movements')
        if not self.broken:
            self.movements += 1
            print('Rotating left, total movements:', self.movements)
            self.dir = (self.dir + 1) % 4
            self.set_position(self.x,self.y,(self.w + 90)%360)

    def ultrasonicFront(self):
        return self.__getDistance(0)

    def ultrasonicRight(self):
        return self.__getDistance(1)

    def ultrasonicLeft(self):
        return self.__getDistance(2)

    def __getDistance(self, dir_ultrasonic):
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
                [3, 0, 1, 2],
                [1, 2, 3, 0]]
        distance = None
        start = 0
        distance_direction = dirs[dir_ultrasonic][self.dir]
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
            # col++ until 0
            for pos in range(self.col, map.width):
                if map.tiles[self.row][pos].East.status == 1:
                    distance = start
                    break
                start += 1
            if distance == None:
                return -1
        return distance

    def scanEnvironment(self):
        return map.tiles[self.row][self.col].envType

    def detectFireFront(self):
        # Map dir:
        #   0 -> North
        #   1 -> West
        #   2 -> South
        #   3 -> East
        row_directions = [-1, 0, 1, 0]
        col_directions = [0, -1, 0, 1]
        row = self.row + row_directions[self.dir]
        col = self.col + col_directions[self.dir]
        if not map.is_valid_coordinate(row, col):
                return False
        return map.tiles[row][col].envType == "fire"

    def  putOutFireFront(self):
        if self.detectFireFront():
            # Map dir:
            #   0 -> North
            #   1 -> West
            #   2 -> South
            #   3 -> East
            row_directions = [-1, 0, 1, 0]
            col_directions = [0, -1, 0, 1]
            row = self.row + row_directions[self.dir]
            col = self.col + col_directions[self.dir]
            if not map.is_valid_coordinate(row, col):
                return
            map.tiles[row][col].color = "white"
            map.tiles[row][col].envType = "clear"
            # generate_map()
            self.points += 10
            print('Fire extinguished! +10,', "Total points:", self.points)
        
    def sendMessageRescueBase(self, coordinate, path = None):
        row = coordinate.y
        col = coordinate.x
        if map.is_valid_coordinate(row, col) and map.tiles[row][col].envType == "people":
            map.tiles[row][col].envType = "clear"
            map.tiles[row][col].color = "white"
            self.points += 5
            print('Rescue message with correct data sent! +5,', "Total points:", self.points)
            if path:
                if self.__verifyPath(path):
                    self.points += 20
                    print('Valid path! +20,', "Total points:", self.points)
                else:
                    self.points -= 20
                    print('Invalid path! -20,', "Total points:", self.points)
            return True
        self.points -= 10
        print('Rescue message with incorrect data sent! -10,', "Total points:", self.points)
        return False

    def sendMessageExplorationBase(self, coordinate):
        row = coordinate.y
        col = coordinate.x
        if map.is_valid_coordinate(row, col) and map.tiles[row][col].envType == "collapse":
            self.points += 5
            print('Exploration message with correct data sent! +5,', "Total points:", self.points)
            return True
        self.points -= 10
        print('Exploration message with incorrect data sent! -10,', "Total points:", self.points)
        return False

    def __verifyPath(self,path): # path : ['N', 'S', 'E', 'W'...]
        direction_deltas = {'W': (-1,0), 'E': (1,0), 'N': (0,-1), 'S': (0,1)}
        row = self.row
        col = self.col
        for direction in path:
            row += direction_deltas[direction][1]
            col += direction_deltas[direction][0]
            if not map.is_valid_coordinate(row, col):
                return False
            if map.tiles[row][col].envType == "collapse":
                return False
            if map.tiles[row][col].envType == "fire":
                return False
        if map.tiles[row][col].envType == "safe":
            return True
        return False

    def finishExploration(self):
        if not self.broken:
            self.broken = True
            if self.col + self.row == 0:
                self.points+=20
                print("Robot returned to base successfully! +20 points," , "Total points:", self.points)
            print('Mission finished.')

    def __debugTile(self):
        print("(~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~)")
        print("Position:", self.row, self.col,)
        print("Color: ", map.tiles[self.row][self.col].color)
        print("Color: ", map.tiles[self.row][self.col].envType)
        print("North: ", map.tiles[self.row][self.col].North.status)
        print("South: ", map.tiles[self.row][self.col].South.status)
        print("East: ", map.tiles[self.row][self.col].East.status)
        print("West: ", map.tiles[self.row][self.col].West.status)
        print("Front", self.ultrasonicFront())
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


def setup_map():
    global display_width 
    global display_height 
    global pixel_constant
    global gameDisplay
    global map

    pixel_constant = map_info['squareSize'] if map_info['squareSize'] else pixel_constant
    display_width = map_info['size']['w'] * pixel_constant
    display_height = map_info['size']['h'] * pixel_constant

    #Map initialization
    map = Map(map_info['size']['w'],map_info['size']['h'])
    dir = ["North","South","East","West"]
    dir_reflection = ["South","North","West","East"]
    dir_reflection_xy = [(-1,0),(1,0),(0,1),(0,-1)]
    #fire", "people", "collapse", "clear", "safe"
    env_colors = {"pink":"collapse", "yellow":"fire", "white":"clear", "cyan":"safe", "red":"people"}
    for tile in map_info['tiles']:
        map.tiles[tile['row']][tile['col']].color = tile['color']
        map.tiles[tile['row']][tile['col']].envType = env_colors[tile['color']]
        for dir_index in range(len(dir)):
            if getattr(getattr(map.tiles[tile['row']][tile['col']], dir[dir_index]), "status") == 0:
                setattr(getattr(map.tiles[tile['row']][tile['col']], dir[dir_index]), "status", tile['directions'][dir_index])
            if tile['directions'][dir_index] == 1:
                new_row = tile['row'] + dir_reflection_xy[dir_index][0]
                new_col = tile['col'] + dir_reflection_xy[dir_index][1]
                if map.is_valid_coordinate(new_row, new_col):
                    setattr(getattr(map.tiles[new_row][new_col], dir_reflection[dir_index]), "status", 1)


def setup_robot():
    # Map dir:
        #   0 -> North
        #   1 -> West
        #   2 -> South
        #   3 -> East
    global robot
    global robotImg

    robot_size = int(pixel_constant * 0.5)
    
    col = map_info['robot_start']['col']
    row = map_info['robot_start']['row']

    start_x = col * pixel_constant + robot_size
    start_y = row * pixel_constant + robot_size
    angle = map_info['robot_start']['w']
    dic_dir = {0:3, 90:0, 180:1, 270:2}
    dir = dic_dir[angle]
    
    robot = Robot(start_x,start_y,angle,robot_size,col,row,dir)


def main():
    global robot
    setup_map()
    setup_robot()
    with open("main_program.py") as f:
        code = compile(f.read(), "main_program.py", 'exec')
        exec(code)
    print("(~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~)")
    print('Final score:', robot.points)
    print('Movements:', robot.movements)
    print("(~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~)")


if __name__ == "__main__":
    setup_map()
    setup_robot()
    main()
    quit()
