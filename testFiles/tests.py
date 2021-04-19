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
    ###################################################
    #Test 0: Debugging de mapa y ultrasónicos
    ###################################################
    # robot.move_forward()
    # robot.rotate_right()
    # robot.move_forward()
    # robot.rotate_left()
    # robot.putOutFireFront()
    # robot.move_forward()
    # robot.debugTile()
    # robot.rotate_right()
    # robot.debugTile()
    # robot.rotate_right()
    # robot.debugTile()
    # robot.rotate_right()
    # robot.debugTile()
    

    ###################################
    #Test 1: Robot eliminado por fuego
    ###################################
    # robot.move_forward()
    # robot.rotate_right()
    # robot.move_forward()
    # robot.rotate_left()
    # robot.move_forward()
    # robot.move_forward()
    # robot.move_forward()


    ###################################
    #Test 2: Robot atrapado en derrumbe
    ###################################
    # robot.move_forward()
    # robot.move_forward()
    # robot.move_forward()
    # robot.rotate_right()
    # robot.move_forward()
    # robot.move_forward()
    # robot.rotate_right()
    # robot.move_forward()
    # robot.rotate_right()
    # robot.rotate_right()
    # robot.move_forward()
    # robot.rotate_right()
    # robot.move_forward()


    ############################################
    #Test 3: Robot apaga fuego, envía correctamente
    # mensaje de derrumbe, salva personas y regresa
    # a la base.
    ############################################
    # robot.move_forward()
    # robot.rotate_right()
    # robot.move_forward()
    # robot.rotate_left()
    # print("Fire in the front:", robot.detectFireFront())
    # robot.putOutFireFront()
    # robot.rotate_right()
    # robot.move_forward()
    # robot.rotate_left()
    # robot.move_forward()
    # robot.move_forward()
    # print("Collapse alert successfull:",robot.sendMessageExplorationBase(Coord(3,2)))
    # robot.move_forward()
    # robot.rotate_right()
    # robot.move_forward()
    # print("People saved?",robot.sendMessageRescueBase(Coord(4,3), ["N", "N"]))
    # robot.rotate_left()
    # robot.move_forward()
    # robot.rotate_left()
    # robot.putOutFireFront()
    # robot.move_forward()
    # robot.putOutFireFront()
    # robot.move_forward()
    # robot.move_forward()
    # robot.rotate_left()
    # robot.move_forward()
    # robot.move_forward()
    # robot.move_forward()
    # robot.move_forward()
    # robot.move_forward()
    # robot.finishExploration()
    

    ###################################################
    #Test 4: Robot apaga fuego y envía path incorrecto
    ###################################################
    # robot.rotate_right()
    # robot.move_forward()
    # robot.move_forward()
    # robot.move_forward()
    # robot.putOutFireFront()
    # robot.rotate_left()
    # robot.move_forward()
    # robot.move_forward()
    # robot.move_forward()
    # robot.sendMessageRescueBase(Coord(4,3), ["L", "L", "L", "D", "D"])
    

if __name__ == "__main__":
    main()