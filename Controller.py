from threading import Thread
from time import sleep

class Controller:
    def __init__(self,dron,cam_con_queue,sen_con_queue):
        self.dron = dron
        self.cam_con_queue = cam_con_queue
        self.sen_con_queue = sen_con_queue
        self.last_QR = False
        self.commands_dic = {'R': self.dron.move_right, 'L': self.dron.move_left, 'F' : self.dron.move_forward, 
                             'B' : self.dron.move_back, 'U': self.dron.move_up, 'D': self.dron.move_down, 
                             'RR': self.dron.rotate_clockwise, 'RL': self.dron.rotate_counter_clockwise}
        self.src_thread = Thread( target=self.start_processing, args=() )

    def thread_init( self ):
        self.src_thread.start()

    def send_commands(self,QRcode):
        print("[INFO] Controller: Executing" + QRcode)
        if(QRcode == "END"):
            last_QR = True 
            self.sen_con_queue.put("Wake up")
        else:
            actions = QRcode.split(',')
            print(actions)
            for action in actions:
                actions_and_numbers = action.split(':')
                if(actions[0] == "ERROR"):
                    print("[ERROR] Controller: Error detected from ImageCaption " + actions[1])
                else:
                    self.commands_dic[actions_and_numbers[0]](int(actions_and_numbers[1]))
    
    def start_processing(self):
        self.dron.takeoff()
        self.cam_con_queue.put("Start")
        sleep(1)
        while not self.last_QR:
            print("[INFO] Controller: Waiting message from ImageCaption")
            instruction = self.cam_con_queue.get()
            print("[INFO] Controller: Message taken from ImageCaption")
            self.send_commands(instruction)
            self.cam_con_queue.put("Next")
            sleep(1)
        #instruction = self.sen_con_queue.get()
        #send_commands(instruction)
        self.dron.land()

    
