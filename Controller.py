
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
    
    def start_processing(self):
        while not self.last_QR:
            instruction = self.cam_con_queue.get()
            send_commands(instruction)
        instruction = self.sen_con_queue.get()
        send_commands(instruction)

    def send_commands(self,QRcode):
        if(QRcode == "END"):
            last_QR = True 
            self.sen_con_queue("Despierte")
        else:
            actions = QRcode.split(',')
            if(action[0] == "ERROR"):
                print(action[1])
            else:
                print(actions)
                for action in actions:
                    actions_and_numbers = action.split(':')
                    print(actions_and_numbers)
                    print("executing " + actions_and_numbers[0])
                    self.commands_dic[actions_and_numbers[0]](int(actions_and_numbers[1]))
