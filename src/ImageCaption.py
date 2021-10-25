from threading import Thread
import queue
import cv2
from time import sleep
from pyzbar.pyzbar import decode
import re
from datetime import datetime

class ImageCaption:
    def __init__( self, tello, queue, max_height, log ):
        # tello instance
        self.tello = tello
        # Queue for communication
        self.controller_comm = queue
        self.src_thread = Thread( target=self.routine, args=() )
        self.max_height = max_height
        self.log = log
    
    def thread_init( self ):
        self.src_thread.start()
    
    def routine( self ):
        end = False
        while not end:
            qr_found = False
            print("[INFO] ImageCaption: Waiting message from Controller")
            self.log.print("INFO","ImageCaption","Waiting message from Controller")
            # espera pasiva de mensaje de controlador
            self.controller_comm.get()
            print("[INFO] ImageCaption: Message taken from Controller")
            self.log.print("INFO","ImageCaption","Message taken from Controller")
            # inicia toma de video
            self.tello.streamon()
            retries = 0
            while not qr_found:
                instruction = self.search_qr()
                value = self.check_instruction( instruction )
                if value == 1:
                    self.controller_comm.put( instruction )
                    qr_found = True
                elif value == 2:
                    self.controller_comm.put( instruction.split( ",END" )[0] )
                    end = True
                    qr_found = True
                if retries < 2:
                    retries = retries + 1 # como limite temporal para pruebas
                else:
                    break
            sleep(1) # para esperar a que el controlador agarre el mensaje primero
        if not end:
            print("[INFO] ImageCaption: No QR found")
            self.log.print("INFO","ImageCaption","No QR found")
        self.controller_comm.get() # esperar a que se completen las ultimas acciones antes del END
        self.controller_comm.put( "END" )
    
    def search_qr( self ):
        decoded_instruction = None
        # se toma la foto
        frame_reader = self.tello.get_frame_read()
        img = frame_reader.frame

        #now = datetime.now()
        #current_time = now.strftime("%H:%M:%S")
        #cv2.imwrite("picture " + current_time + ".jpg", img)

        # decode qr image
        dec_img = decode( img )
        if( len(dec_img) != 0 ):
            decoded_instruction = dec_img[0].data.decode( 'utf8' )
            if self.check_instruction( decoded_instruction ):
                print("[INFO] ImageCaption: QR found in front")
                self.log.print("INFO","ImageCaption","QR found in front")
        else:
            # inicia rutina de búsqueda
            decoded_instruction = self.look_up( frame_reader )
            if( decoded_instruction == None ):
                decoded_instruction = self.look_down( frame_reader )
        return decoded_instruction

    def look_up( self, frame_reader ):
        decoded_instruction = None
        # se obtiene la altura actual
        curr_height = self.tello.get_height()
        # seguir subiendo mientras no se encuentre QR o no se sobrepase el limite
        while( self.max_height - curr_height > 40 and decoded_instruction == None ):
            print("[INFO] ImageCaption: current height: " + str(curr_height))
            self.log.print("INFO","ImageCaption","current height: "+str(curr_height))
            self.tello.move_up( 20 )
            img = frame_reader.frame

            #now = datetime.now()
            #current_time = now.strftime("%H:%M:%S")
            #cv2.imwrite("picture " + current_time + ".jpg", img)

            dec_img = decode( img )
            if( len(dec_img) != 0 ):
                decoded_instruction = dec_img[0].data.decode( 'utf8' )
                if self.check_instruction( decoded_instruction ):
                    print("[INFO] ImageCaption: QR found when looking up")
                    self.log.print("INFO","ImageCaption","QR found when looking up")
                    break
            # se actualiza altura actual
            curr_height = self.tello.get_height()
            sleep(1)
        return decoded_instruction
    
    def look_down( self, frame_reader ):
        decoded_instruction = None
        # se obtiene la altura actual
        curr_height = self.tello.get_height()
        # seguir bajando mientras no se aterrice o no se encuentre QR
        while( curr_height > 30 and decoded_instruction == None ): # reconsiderar 30
            print("[INFO] ImageCaption: current height: " + str(curr_height))
            self.log.print("INFO","ImageCaption","current height: "+str(curr_height))
            self.tello.move_down( 20 )
            img = frame_reader.frame

            #now = datetime.now()
            #current_time = now.strftime("%H:%M:%S")
            #cv2.imwrite("picture " + current_time + ".jpg", img)
            
            dec_img = decode( img )
            if( len(dec_img) != 0 ):
                decoded_instruction = dec_img[0].data.decode( 'utf8' )
                if self.check_instruction( decoded_instruction ):
                    print("[INFO] ImageCaption: QR found when looking down")
                    self.log.print("INFO","ImageCaption","QR found when looking down")
                    break
            # se actualiza altura actual
            curr_height = self.tello.get_height()
            sleep(1)
        return decoded_instruction

    def check_instruction( self, instruction ):
        if( instruction == None ):
            return 0
        elif( re.search( "^((([RLFUB]|R(R|L)):\d+,)+(([RLFUB]|R(R|L)):\d+))$",
            instruction ) ):
                return 1
        elif( re.search( "^(([RLFUB]|R(R|L)):\d+)$",
            instruction ) ):
                return 1
        elif( re.search( "^((([RLFUB]|R(R|L)):\d+,)+END)$",
            instruction ) ):
                return 2
        return 0