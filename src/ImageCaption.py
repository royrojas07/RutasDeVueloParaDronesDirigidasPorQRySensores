from threading import Thread
import queue
import cv2
from time import sleep
from pyzbar.pyzbar import decode
import re
from datetime import datetime

class ImageCaption:
    def __init__( self, tello, queue, max_height, log, cam_stop_queue ):
        # tello instance
        self.tello = tello
        # Queue for communication
        self.controller_comm = queue
        self.stop_queue = cam_stop_queue
        self.src_thread = Thread( target=self.routine, args=() )
        self.max_height = max_height
        self.log = log
    
    def thread_init( self ):
        self.src_thread.start()
        self.src_thread.join()
    
    def routine( self ):
        end = False
        while not end:
            qr_found = False
            retries = 0

            print("[INFO] ImageCaption: Waiting message from Controller")
            self.log.print("INFO","ImageCaption","Waiting message from Controller")
            # espera pasiva por mensaje desde controlador
            self.controller_comm.get()
            print("[INFO] ImageCaption: Message taken from Controller")
            self.log.print("INFO","ImageCaption","Message taken from Controller")
            
            # inicia toma de video
            self.tello.streamon()
            
            while not qr_found:
                # se revisa si hay que detener la ejecucion del hilo
                if not (self.stop_queue.empty()):
                    self.controller_comm.put("STOP")
                    self.log.print("INFO","ImageCaption","Received a stop event")
                    exit(0)
                
                # se empieza a buscar el QR
                instruction = self.search_qr()
                # se chequea la instruccion decodificada
                value = self.check_instruction( instruction )
                if value == 1: # instruccion correcta
                    self.controller_comm.put( instruction )
                    qr_found = True
                elif value == 2: # instruccion con END correcta
                    self.controller_comm.put( instruction.split( ",END" )[0] )
                    end = True
                    qr_found = True
                if retries < 1: # se reintenta encontrar el QR
                    retries = retries + 1
                else: # se desiste en buscar el QR
                    end = True
                    break
            sleep(1) # para esperar a que el controlador tome el mensaje primero
        if not qr_found:
            print("[INFO] ImageCaption: No QR found")
            self.log.print("INFO","ImageCaption","No QR found")
            self.controller_comm.put( "NOQR" )
        else:
            # se espera a que se completen los ultimos comandos
            self.controller_comm.get()
            self.controller_comm.put( "END" )
    
    def search_qr( self ):
        decoded_instruction = None

        frame_reader = self.tello.get_frame_read()
        # se captura imagen
        img = frame_reader.frame

        #now = datetime.now()
        #current_time = now.strftime("%H:%M:%S")
        #cv2.imwrite("picture " + current_time + ".jpg", img)

        # se intenta decodificar algun QR
        decoded_instruction = self.try_to_decode( img )
        if decoded_instruction == None:
            # se empieza a buscar el QR hacia arriba
            decoded_instruction = self.look_up( frame_reader )
            if( decoded_instruction == None ):
                # se empieza a buscar el QR hacia abajo
                decoded_instruction = self.look_down( frame_reader )
        return decoded_instruction

    def look_up( self, frame_reader ):
        decoded_instruction = None
        # se obtiene la altura actual del dron
        curr_height = self.tello.get_height()
        # seguir subiendo mientras no se encuentre QR o no se sobrepase el limite
        while( self.max_height - curr_height > 40 and decoded_instruction == None ):
            print("[INFO] ImageCaption: current height: " + str(curr_height))
            self.log.print("INFO","ImageCaption","current height: "+str(curr_height))
            
            # el dron se eleva 20 centimetros
            self.tello.move_up( 20 )
            
            # se revisa si hay que detener la ejecucion del hilo
            if not(self.stop_queue.empty()):
                self.controller_comm.put("STOP")
                self.log.print("INFO","ImageCaption","Received a stop event")
                exit(0)
            
            # se captura imagen
            img = frame_reader.frame

            #now = datetime.now()
            #current_time = now.strftime("%H:%M:%S")
            #cv2.imwrite("picture " + current_time + ".jpg", img)
            
            # se intenta decodificar algun QR
            decoded_instruction = self.try_to_decode( img )

            # se actualiza altura actual
            curr_height = self.tello.get_height()
            sleep(1)
        return decoded_instruction
    
    def look_down( self, frame_reader ):
        decoded_instruction = None
        # se obtiene la altura actual
        curr_height = self.tello.get_height()
        # seguir bajando mientras no se aterrice o no se encuentre QR
        while( curr_height > 30 and decoded_instruction == None ):
            print("[INFO] ImageCaption: current height: " + str(curr_height))
            self.log.print("INFO","ImageCaption","current height: "+str(curr_height))
            
            # el dron desciende 20 centimetros
            self.tello.move_down( 20 )
            
            # se revisa si hay que detener la ejecucion del hilo
            if not(self.stop_queue.empty()):
                self.controller_comm.put("STOP")
                self.log.print("INFO","ImageCaption","Received a stop event")
                exit(0)

            # se captura imagen
            img = frame_reader.frame

            #now = datetime.now()
            #current_time = now.strftime("%H:%M:%S")
            #cv2.imwrite("picture " + current_time + ".jpg", img)
            
            # se intenta decodificar algun QR
            decoded_instruction = self.try_to_decode( img )

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
    
    def try_to_decode( self, image ):
        # se intenta decodificar algun QR
        dec_img = decode( image )
        if( len(dec_img) != 0 ):
            decoded_instruction = dec_img[0].data.decode( 'utf8' )
            # se chequea la instruccion decodificada
            if self.check_instruction( decoded_instruction ):
                print("[INFO] ImageCaption: QR found and decoded!")
                self.log.print("INFO","ImageCaption","QR found and decoded!")
                return decoded_instruction
        return None