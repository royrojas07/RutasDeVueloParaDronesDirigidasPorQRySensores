from djitellopy import Tello
import threading
from time import sleep
import queue
import sys
import signal
from Controller import *
from ImageCaption import *
from Sensor_reader import *
from Log import *

dron = Tello()
dron.connect()
exit_event = threading.Event()
cam_con_queue = queue.Queue() #cola entre la camara y el controlador
sen_con_queue = queue.Queue() #cola entre el sensor y el controlador

#print( dron.get_battery() )
log = Log()
log.print("INFO","Main","The program started")

def handler(signum, frame):
    print("[ABORT] Landing the Tello")
    dron.land()
    exit_event.set() # para que mate los threads
    log.close_file()
    exit()


def main():
    route_type = usage()
    if(route_type == 1): #ruta QR
        landing_distance = input("A cuanta distancia en metros está el punto de aterrizaje en frente del sensor ultrasónico?")
        threads = [Thread( target=init_Controller, args=()),
                Thread( target=init_camera, args=()),
                Thread( target=init_sensor, args=(landing_distance))]

        for thread in threads:
            thread.start()
            thread.join()
    else:
        pass
        #en este caso usaria el archivo separado por tabs
    
    signal.signal(2, handler)
    #log.close_file()

def usage():
    route_type = 0
    if len(sys.argv) == 3:
        if not (sys.argv[2].isnumeric()):
            print("Error - Invalid input in the number argument")
            print("input must be a number")
            log.print("ERROR","Main","Invalid input in the number argument")
            exit
        elif(sys.argv[1] == "QR"):
            max_height = int(sys.argv[2])
            route_type = 1
        elif(sys.argv[1] == "auto"):
            route = int(sys.argv[2])
            route_type = 2
        else:
            print("Error - Invalid input in the route type argument")
            print("route type could be: QR or auto")
            log.print("ERROR","Main","Invalid input in the route type argument")
            exit
    else:
        print("Error - Invalid input in the arguments")
        print('Example: python main.py "route type" "number"')
        print("route type could be: QR or auto")Invalid input in the route type argument
        print("number is max height in QR and which route in auto")
        log.print("ERROR","Main","Invalid input arguments")
        exit
    return route_type

def init_Controller():
    controller = Controller(dron,cam_con_queue,sen_con_queue,log)
    controller.thread_init()

def init_camera():
    imageCaption = ImageCaption(dron,cam_con_queue,max_height,log)
    imageCaption.thread_init()

def init_sensor(landing_distance):
    sensorReader = Sensor_reader(dron,sen_con_queue,landing_distance)
    sensorReader.thread_init()
    print("hilo de sensor")

if __name__ == '__main__':
	main()