import serial
import time
import struct

from threading import Thread
from rpi_lcd import LCD

from connection.uart import Uart

class AirFryer:
    port = '/dev/serial0'
    baudrate = 9600
    timeout = 0.5
    matricula = [3, 6, 6, 6]

    ligado = True
    funcionando = False
    enviando = False
    menu = -1
    lcd = LCD()
    temp_inter = 0
    temp_ref = 0
    tempo = 0

    def __init__(self):
        self.uart = Uart(self.port, self.baudrate, self.timeout)
        self.inicia_servicos()

    def liga(self):
        enviando = True

        comando_estado = b'\x01\x23\xd3'
        matricula = self.matricula + [1]

        self.uart.envia(comando_estado, matricula, 8)
        dados = self.uart.recebe()

        if dados is not None:
            self.ligado = True

        enviando = False

    def desliga(self):
        enviando = True

        comando_estado = b'\x01\x23\xd3'
        matricula = self.matricula + [0]

        self.uart.envia(comando_estado, matricula, 8)
        dados = self.uart.recebe()

        if dados is not None:
            self.para()
            self.ligado = False

        enviando = False

    def inicia(self):
        enviando = True

        comando_estado = b'\x01\x23\xd5'
        matricula = self.matricula + [1]

        self.uart.envia(comando_estado, matricula, 8)
        dados = self.uart.recebe()

        if dados is not None:
            self.funcionando = True

        enviando = False

    def para(self):
        enviando = True

        comando_estado = b'\x01\x23\xd5'
        matricula = self.matricula + [0]

        self.uart.envia(comando_estado, matricula, 8)
        dados = self.uart.recebe()

        if dados is not None:
            self.funcionando = False

        enviando = False

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
            self.tempo += 1
        elif botao == 6:
            self.tempo -= 1
        elif botao == 7:
            self.abre_menu()

    def trata_temp_int(self, bytes):
        self.temp_inter = struct.unpack('f', bytes)[0]
        print('temperatura int', self.temp_inter)

    def trata_temp_ref(self, bytes):
        self.temp_ref = struct.unpack('f', bytes)[0]
        print('temperatura ref', self.temp_ref)

    def solicita_botao(self):
        comando_botao = b'\x01\x23\xc3'
        
        self.uart.envia(comando_botao, self.matricula, 7)
        dados = self.uart.recebe()

        if dados is not None:
            self.trata_botao(dados)

    def solicita_temp_int(self):
        comando_temp = b'\x01\x23\xc1'

        self.uart.envia(comando_temp, self.matricula, 7)
        dados = self.uart.recebe()

        if dados is not None:
            self.trata_temp_int(dados)

    def solicita_temp_ref(self):
        comando_temp = b'\x01\x23\xc2'

        self.uart.envia(comando_temp, self.matricula, 7)
        dados = self.uart.recebe()

        if dados is not None:
            self.trata_temp_ref(dados)

    def atualiza_lcd(self):
        while True:
            if self.ligado:
                if self.funcionando:
                    self.lcd.text(f'TI:{round(self.temp_inter, 2)} TR:{round(self.temp_ref, 2)}', 1)
                    self.lcd.text(f'Tempo:{self.tempo}', 2)
                else:
                    self.lcd.text(f'TI:{round(self.temp_inter, 2)} TR:{round(self.temp_ref, 2)} 2', 1)
                    self.lcd.text(f'Tempo: {self.tempo}', 2)
            else:
                self.lcd.clear()
    
    def rotina(self):
        while not self.enviando:
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