from threading import Thread
from time import sleep
#from playsound import playsound 

class Controller:
    def __init__(self,dron,cam_con_queue,sen_con_queue,log,cam_stop_queue):
        self.dron = dron
        self.cam_con_queue = cam_con_queue
        self.sen_con_queue = sen_con_queue
        self.cam_stop_queue = cam_stop_queue

        self.last_QR = False
        self.land = False
        self.log = log
        self.commands_dic = {'R': self.dron.move_right, 'L': self.dron.move_left, 'F' : self.dron.move_forward, 
                             'B' : self.dron.move_back, 'U': self.dron.move_up, 'D': self.dron.move_down, 
                             'RR': self.dron.rotate_clockwise, 'RL': self.dron.rotate_counter_clockwise}
        self.src_thread = Thread( target=self.start_processing, args=() )

    def thread_init( self ):
        self.src_thread.start()

    def send_commands(self,QRcode):
        if(QRcode == "END"):
            self.last_QR = True 
            #self.sen_con_queue.put("Wake up")
            print("LLEGO CON EXITOS EL END")
        elif(QRcode == "NOQR"):
            self.log.print("ERROR","Controller", "Program ended, it doesn't found a QR, landing...")
            self.log.close_file()
            self.dron.land()
            exit(1)
        elif(QRcode == "STOP"):
            self.log.print("INFO","Controller", "Program ended by a stop event, landing...")
            self.log.close_file()
            self.dron.land()
            self.cam_stop_queue.put("Termine")
            exit(0)
        else:
            print("[INFO] Controller: Executing " + QRcode)
            self.log.print("INFO","Controller","Executing " + QRcode)
            actions = QRcode.split(',')
            print(actions)
            for action in actions:
                actions_and_numbers = action.split(':')
                if(actions[0] == "ERROR"):
                    print("[ERROR] Controller: Error detected from ImageCaption " + actions[1])
                    self.log.print("ERROR","Controller", "Error detected from ImageCaption " + actions[1])
                else:
                    self.commands_dic[actions_and_numbers[0]](int(actions_and_numbers[1]))
    
    def start_processing(self):
        self.dron.takeoff()
        self.cam_con_queue.put("Start")
        sleep(1)
        while not self.last_QR:
            print("[INFO] Controller: Waiting message from ImageCaption")
            self.log.print("INFO","Controller", "Waiting message from ImageCaption")
            instruction = self.cam_con_queue.get()
            print("[INFO] Controller: Message taken from ImageCaption")
            self.log.print("INFO","Controller", "Message taken from ImageCaption")
            self.send_commands(instruction)
            #playsound('sonido de notificacion pikachu.mp3')  #para prueba con sonido
            self.cam_con_queue.put("Next")
            self.log.print("INFO","Controller", "Requesting for the next instruction")
            sleep(1)
        #instruction = self.sen_con_queue.get()
        #send_commands(instruction)
        #self.process_sen(self)
        self.log.print("INFO","Controller", "Program ended, landing...")
        self.log.close_file()
        self.dron.land()
    
    def process_sen(self):
        self.sen_con_queue.put("Start")
        sleep(1)
        self.sen_con_queue.put("Next")
        print("[INFO] Controller: Waiting for message from SensorReader")
        instruction = self.sen_con_queue.get()
        print("[INFO] Controller: Message received from SensorReader " + instruction)
        while not self.land:
            self.send_commands_sen(instruction)
            self.sen_con_queue.put("Next")
            instruction = self.sen_con_queue.get()
            sleep(1)

    def send_commands_sen(self,instruction):
        if(instruction == "LAND"):
            print("[INFO] Controller: Executing Sensor_reader" + instruction)
            self.land = True

