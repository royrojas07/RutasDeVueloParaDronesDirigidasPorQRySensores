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

log = Log()
log.print("INFO","Main","The program started")
log.print("INFO","Main","Tello battery: "+str(dron.get_battery()))
print("[INFO] Main: Tello battery level: "+str(dron.get_battery()))

def handler(signum, frame):
    print("[ABORT] Landing the Tello")
    dron.end() #dron.land() #funcionan parecido
    exit_event.set() # para que mate los threads
    log.close_file()
    exit()


def main():
    route_type, max_height, landing_distance, sensor_height = usage()
    if(route_type == 1): #ruta QR
        threads = [Thread( target=init_Controller, args=()),
                Thread( target=init_camera, args=(max_height,))]

        for thread in threads:
            thread.start()
            thread.join()
    elif(route_type == 2):
        pass
        #en este caso usaria el archivo separado por tabs
    else:#en este caso se usarian los sensores 
        threads = [Thread( target=init_Controller, args=()),
                Thread( target=init_camera, args=(max_height,)),
                Thread( target = init_sensor, args=(landing_distance,max_height,sensor_height,))]
        for thread in threads:
            thread.start()
            thread.join()
    signal.signal(2, handler)
    #log.close_file()

def usage():
    route_type = 0
    max_height = 0
    landing_distance = 0
    sensor_height = 0
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
    elif len(sys.argv) == 5:
        if not (sys.argv[2].isnumeric() and sys.argv[3].isnumeric() and sys.argv[4].isnumeric()):
            print("Error - Invalid input in the number argument")
            print("input must be a number")
            log.print("ERROR","Main","Invalid input in the number argument")
            exit
        elif(sys.argv[1] == "QRsen"):
            max_height = int(sys.argv[2])
            landing_distance = int(sys.argv[3])
            sensor_height = int(sys.argv[4])
            route_type = 3
    else:
        print("Error - Invalid input in the arguments")
        print('Example: python main.py "route type" "number"')
        print("route type could be: QR or auto Invalid input in the route type argument")
        print("number is max height in QR and which route in auto")
        log.print("ERROR","Main","Invalid input arguments")
        exit
    return route_type, max_height, landing_distance, sensor_height

def init_Controller():
    controller = Controller(dron,cam_con_queue,sen_con_queue,log)
    controller.thread_init()

def init_camera(max_height):
    imageCaption = ImageCaption(dron,cam_con_queue,max_height,log)
    imageCaption.thread_init()

def init_sensor(landing_distance,max_height,sensor_height):
    sensorReader = Sensor_reader(dron,sen_con_queue,landing_distance,max_height,sensor_height,log)
    sensorReader.thread_init()
    print("hilo de sensor")

if __name__ == '__main__':
    if dron.get_battery() > 10:
        main()
    else:
        print("Battery is low: "+str(dron.get_battery())+"%")
