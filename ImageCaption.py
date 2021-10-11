from threading import Thread
import queue
import cv2
from time import sleep
from pyzbar.pyzbar import decode
import re
from datetime import datetime

class ImageCaption:
    def __init__( self, tello, queue, max_height ):
        # tello instance
        self.tello = tello
        # Queue for communication
        self.controller_comm = queue
        self.src_thread = Thread( target=self.routine, args=() )
        self.max_height = max_height
    
    def thread_init( self ):
        self.src_thread.start()
    
    def routine( self ):
        exit_thread = False
        end = False
        while not exit_thread and not end:
            print("[INFO] ImageCaption: Waiting message from Controller")
            # espera pasiva de mensaje de controlador
            self.controller_comm.get()
            print("[INFO] ImageCaption: Message taken from Controller")
            instruction = self.search_qr()
            value = self.check_instruction( instruction )
            if( value == 1 ):
                self.controller_comm.put( instruction )
            elif( value == 0 ):
                self.controller_comm.put( "ERROR: no QR found" )
                exit_thread = True
            else:
                self.controller_comm.put( instruction.split( ",END" )[0] )
                end = True
            sleep(1) # para esperar a que el controlador agarre el mensaje primero
        self.controller_comm.get() # esperar a que se completen las ultimas acciones antes del END
        self.controller_comm.put( "END" )
    
    def search_qr( self ):
        decoded_instruction = None
        # inicia toma de video
        self.tello.streamon()
        # se toma la foto
        frame_reader = self.tello.get_frame_read()
        img = frame_reader.frame
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        cv2.imwrite("picture " + current_time + ".jpg", img)
        # decode qr image
        dec_img = decode( img )
        if( len(dec_img) != 0 ):
            decoded_instruction = dec_img[0].data.decode( 'utf8' )
            print("[INFO] ImageCaption: QR found in front")
        else:
            # inicia rutina de búsqueda
            decoded_instruction = self.look_up( frame_reader )
            if( decoded_instruction == None ):
                decoded_instruction = self.look_down( frame_reader )
        self.tello.streamoff()
        return decoded_instruction

    def look_up( self, frame_reader ):
        decoded_instruction = None
        # se obtiene la altura actual
        curr_height = self.tello.get_height()
        # seguir subiendo mientras no se encuentre QR o no se sobrepase el limite
        while( self.max_height - curr_height > 40 and decoded_instruction == None ):
            print("[INFO] ImageCaption: current height: " + str(curr_height))
            t = Thread( target=self.move, args=(1, 20) )
            t.start()
            # se busca QR mientras el dron se mueve
            while t.is_alive():
                img = frame_reader.frame
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                cv2.imwrite("picture " + current_time + ".jpg", img)
                dec_img = decode( img )
                if( len(dec_img) != 0 ):
                    decoded_instruction = dec_img[0].data.decode( 'utf8' )
                    print("[INFO] ImageCaption: QR found when looking up")
                    break
            # se actualiza altura actual
            curr_height = self.tello.get_height()
        return decoded_instruction
    
    def look_down( self, frame_reader ):
        decoded_instruction = None
        # se obtiene la altura actual
        curr_height = self.tello.get_height()
        # seguir bajando mientras no se aterrice o no se encuentre QR
        while( curr_height > 30 and decoded_instruction == None ): # reconsiderar 30
            print("[INFO] ImageCaption: current height: " + str(curr_height))
            t = Thread( target=self.move, args=(0, 20) )
            t.start()
            # se busca QR mientras el dron se mueve
            while t.is_alive():
                img = frame_reader.frame
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                cv2.imwrite("picture " + current_time + ".jpg", img)
                dec_img = decode( img )
                if( len(dec_img) != 0 ):
                    decoded_instruction = dec_img[0].data.decode( 'utf8' )
                    print("[INFO] ImageCaption: QR found when looking down")
                    break
            # se actualiza altura actual
            curr_height = self.tello.get_height()
        return decoded_instruction

    def check_instruction( self, instruction ):
        if( instruction == None ):
            return 0
        elif( re.search( "^((([RLFUB]|R(R|L)):[2-9]\d+,)+(([RLFUB]|R(R|L)):[2-9]\d+))$",
            instruction ) ):
                return 1
        elif( re.search( "^(([RLFUB]|R(R|L)):[2-9]\d+)$",
            instruction ) ):
                return 1
        elif( re.search( "^((([RLFUB]|R(R|L)):[2-9]\d+,)+END)$",
            instruction ) ):
                return 2
        return 0
    
    def move( self, direction, cm ):
        print("[INFO] ImageCaption: Tello is moving")
        if direction == 1:
            self.tello.move_up( cm )
        else:
            self.tello.move_down( cm )