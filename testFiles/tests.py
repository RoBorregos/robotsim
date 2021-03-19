'''
Control: 
    robot.move_forward()
    robot.rotate_right()
    robot.rotate_left()

Sensors:    
    robot.ultrasonicFront() -> int
'''

def main():
    ###################################################
    #Respuesta actividad progra
    ###################################################
    def moverAdelante():
        robot.izqAdelante(1)
        robot.izqAtras(0)
        robot.derAdelante(1)
        robot.derAtras(0)
        robot.prenderMotor()

    def moverAtras():
        robot.izqAdelante(0)
        robot.izqAtras(1)
        robot.derAdelante(0)
        robot.derAtras(1)
        robot.prenderMotor()

    def girarIzq():
        robot.izqAdelante(0)
        robot.izqAtras(1)
        robot.derAdelante(1)
        robot.derAtras(0)
        robot.prenderMotor()

    def girarDer():
        robot.izqAdelante(1)
        robot.izqAtras(0)
        robot.derAdelante(0)
        robot.derAtras(1)
        robot.prenderMotor()

    while(True):
        if(robot.distanciaFrente()):
            moverAdelante()
        else:
            girarDer()
    

if __name__ == "__main__":
    main()