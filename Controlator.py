

class Controlator:
    def __init__(self,dron,cam_con_queue,sen_con_queue):
        self.dron = dron
        self.cam_con_queue = cam_con_queue
        self.sen_con_queue = sen_con_queue
        self.last_QR = False
        #self.commands_dic = {'R': self.dron.move_right, 'L': self.dron.move_left, 'F' : self.dron.move_forward, 
                         #    'B' : self.dron.move_back, 'U': self.dron.move_up, 'D': self.dron.move_down, 
                   #          'RR': self.dron.rotate_clockwise, 'RL': self.dron.rotate_counter_clockwise}

    def start_processing(self):
        while not self.last_QR:
            instruction = self.cam_con_queue.get()
            #print(instruction)
            #send_commands(instruction)
        instruction = self.sen_con_queue.get()
        send_commands(instruction)

    def send_commands(self,QRcode):
        actions = QRcode.split(',')
        print(actions)
        for action in actions:
            actions_and_numbers = action.split(':')
            print(actions_and_numbers)
            print("executing " + actions_and_numbers[0])
            #self.commands_dic[actions_and_numbers[0]](int(actions_and_numbers[1]))
