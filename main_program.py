'''
Control: 
    robot.move_forward()
    robot.rotate_right()
    robot.rotate_left()

Sensors:    
    robot.ultrasonicFront() -> int
    robot.ultrasonicRight() -> int
    robot.ultrasonicLeft() -> int
    robot.detectFireFront() -> bool
    robot.scanEnvironment() -> string ("fire", "people", "collapse", "clear", "safe")

Actions: 
    robot.putOutFireFront()
    robot.sendMessageExplorationBase(Coord)
    robot.sendMessageRescueBase(Coord, path)
    robot.finishExploration()
'''

def main():
    ############################################
    #Test 3: Robot apaga fuego, envía correctamente
    # mensaje de derrumbe, salva personas y regresa
    # a la base.
    ############################################
    robot.move_forward()
    robot.rotate_right()
    robot.move_forward()
    robot.rotate_left()
    print("Fire in the front:", robot.detectFireFront())
    robot.putOutFireFront()
    robot.rotate_right()
    robot.move_forward()
    robot.rotate_left()
    robot.move_forward()
    robot.move_forward()
    print("Collapse alert successfull:",robot.sendMessageExplorationBase(Coord(3,2)))
    robot.move_forward()
    robot.rotate_right()
    robot.move_forward()
    print("People saved?",robot.sendMessageRescueBase(Coord(4,3), ['N', 'N']))
    robot.rotate_left()
    robot.move_forward()
    robot.rotate_left()
    robot.putOutFireFront()
    robot.move_forward()
    robot.putOutFireFront()
    robot.move_forward()
    robot.move_forward()
    robot.rotate_left()
    robot.move_forward()
    robot.move_forward()
    robot.move_forward()
    robot.move_forward()
    robot.move_forward()
    robot.finishExploration()
    

if __name__ == "__main__":
    main()