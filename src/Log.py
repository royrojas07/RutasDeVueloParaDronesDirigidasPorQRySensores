from datetime import datetime

class Log:
    def __init__(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.file = open("../logs/" + current_time + ".txt","w+")

    def print(self, msg_type, module_name, msg):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.file.write(current_time + ' [' + msg_type + "] " + module_name + ": "+ msg + "\n")
    
    def close_file(self):
        self.file.close()