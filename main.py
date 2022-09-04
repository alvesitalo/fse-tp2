import serial
import time
import struct

from threading import Event, Thread 
from rpi_lcd import LCD

from connection.uart import UART
from utils.pid import PID
from connection.forno import Forno

class AirFryer:
    port = '/dev/serial0'
    baudrate = 9600
    timeout = 0.5
    matricula = [3, 6, 6, 6]

    ligado = Event()
    aquecendo = Event()
    resfriando = Event()
    enviando = Event()
    menu = -1
    lcd = LCD()
    temp_inter = 0
    temp_ref = 0
    tempo = 0

    def __init__(self):
        self.uart = UART(self.port, self.baudrate, self.timeout)
        self.pid = PID()
        self.forno = Forno()
        self.inicia_servicos()

    def liga(self):
        self.enviando.set()
        comando_estado = b'\x01\x23\xd3'

        self.uart.envia(comando_estado, self.matricula, b'\x01', 8)
        dados = self.uart.recebe()

        if dados is not None:
            self.para()
            self.ligado.set()

        self.enviando.clear()

    def desliga(self):
        self.enviando.set()
        comando_estado = b'\x01\x23\xd3'

        self.uart.envia(comando_estado, self.matricula, b'\x00', 8)
        dados = self.uart.recebe()

        if dados is not None:
            self.para()
            self.ligado.clear()

        self.enviando.clear()

    def inicia(self):
        self.enviando.set()
        comando_estado = b'\x01\x23\xd5'

        self.uart.envia(comando_estado, self.matricula, b'\x01', 8)
        dados = self.uart.recebe()

        if dados is not None:
            self.aquecendo.set()
            self.resfriando.clear()

        self.enviando.clear()

    def para(self):
        self.enviando.set()
        comando_estado = b'\x01\x23\xd5'

        self.uart.envia(comando_estado, self.matricula, b'\x00', 8)
        dados = self.uart.recebe()

        if dados is not None:
            if self.aquecendo.is_set():
                self.aquecendo.clear()
                self.resfriando.set()

        self.enviando.clear()

    def abre_menu(self):
        pass

    def seta_forno(self):
        pid = self.pid.pid_controle(self.temp_ref, self.temp_inter)
        print('pid', pid)

        if self.aquecendo.is_set():
            if pid > 0:
                self.forno.aquecer(pid)
                self.forno.resfriar(0)
            else:
                pid *= -1
                self.forno.aquecer(0)
                if pid < 40.0:
                    self.forno.resfriar(40.0)
                else:
                    self.forno.resfriar(pid)
        elif self.resfriando.is_set():
            self.forno.aquecer(0)
            self.forno.resfriar(100.00)
        else:
            self.forno.aquecer(0)
            self.forno.resfriar(0.0)
    
    def seta_tempo(self, tempo):
        self.enviando.set()
        comando_estado = b'\x01\x23\xd6'
        valor = tempo.to_bytes(4, 'little')

        self.uart.envia(comando_estado, self.matricula, valor, 11)
        dados = self.uart.recebe()

        #if dados is not None:
        self.tempo = tempo

        self.enviando.clear()
    
    def trata_botao(self, bytes):
        botao = int.from_bytes(bytes, 'little')
        print('botao', botao)
        if botao == 1:
            self.liga()
        elif botao == 2:
           self.desliga()
        elif botao == 3:
            self.inicia()
        elif botao == 4:
            self.para()
        elif botao == 5:
            self.seta_tempo(self.tempo + 1)
        elif botao == 6:
            self.seta_tempo(self.tempo - 1)
        elif botao == 7:
            self.abre_menu()

    def trata_temp_int(self, bytes):
        self.temp_inter = struct.unpack('f', bytes)[0]
        print('temperatura int', self.temp_inter)
        self.seta_forno()

    def trata_temp_ref(self, bytes):
        self.temp_ref = struct.unpack('f', bytes)[0]
        print('temperatura ref', self.temp_ref)

    def solicita_botao(self):
        comando_botao = b'\x01\x23\xc3'
        
        self.uart.envia(comando_botao, self.matricula, b'', 7)
        dados = self.uart.recebe()

        if dados is not None:
            self.trata_botao(dados)

    def solicita_temp_int(self):
        comando_temp = b'\x01\x23\xc1'

        self.uart.envia(comando_temp, self.matricula, b'', 7)
        dados = self.uart.recebe()

        if dados is not None:
            self.trata_temp_int(dados)

    def solicita_temp_ref(self):
        comando_temp = b'\x01\x23\xc2'

        self.uart.envia(comando_temp, self.matricula, b'', 7)
        dados = self.uart.recebe()

        if dados is not None:
            self.trata_temp_ref(dados)

    def atualiza_lcd(self):
        while True:
            if self.ligado.is_set():
                self.lcd.clear()
                if self.aquecendo.is_set():
                    self.lcd.text(f'TI:{round(self.temp_inter, 2)} TR:{round(self.temp_ref, 2)}', 1)
                    self.lcd.text(f'Aquecendo', 2)
                elif self.resfriando.is_set():
                    self.lcd.text(f'TI:{round(self.temp_inter, 2)} TR:{round(self.temp_ref, 2)}', 1)
                    self.lcd.text(f'Resfriando', 2)
                else:
                    self.lcd.text(f'TI:{round(self.temp_inter, 2)} TR:{round(self.temp_ref, 2)}', 1)
                    self.lcd.text(f'Tempo: {self.tempo}', 2)
            else:
                self.lcd.clear()
            time.sleep(1)
    
    def rotina(self):
        while True:
            self.solicita_botao()
            time.sleep(0.5)
            self.solicita_botao()
            time.sleep(0.5)
            self.solicita_temp_int()
            self.solicita_temp_ref()
    
    def inicia_servicos(self):
        self.liga()

        thread_rotina = Thread(target=self.rotina, args=())
        thread_rotina.start()

        thread_lcd = Thread(target=self.atualiza_lcd, args=())
        thread_lcd.start()

        print('AirFryer iniciada')

AirFryer()