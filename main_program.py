'''
Control: 
    robot.move_forward()
    robot.rotate_right()
    robot.rotate_left()

Sensors:    
    robot.ultrasonicFront() -> int
'''

def main():
    ############################################
    #Test movimiento
    ############################################
    robot.move_forward()
    robot.rotate_right()
    robot.move_forward()
    robot.rotate_left()
    robot.move_forward()
    robot.move_forward()

if __name__ == "__main__":
    main()