import serial
import time
from threading import Thread
from rpi_lcd import LCD

from connection.uart import Uart

class AirFryer:
    port = "/dev/serial0"
    baudrate = 9600
    timeout = 2
    matricula = [3, 6, 6, 6]

    ligado = False
    funcionando = False
    menu = -1
    lcd = LCD()
    temp_amb = 0
    temp_ref = 0
    temp_atual = 0
    tempo = 0

    def __init__(self):
        self.uart = Uart(self.port, self.baudrate, self.timeout)
        self.inicia_servicos()

    def liga(self):
        self.ligado = True

    def desliga(self):
        self.ligado = False
        self.funcionando = False

    def trata_botao(self, botao):
        if botao == 0:
            self.desliga()
        elif botao == 1:
            self.liga()
        elif botao == 2:
            self.inicia()
        elif botao == 3:
            self.para()
        elif botao == 4:
            self.tempo += 5
        elif botao == 5:
            self.tempo -= 5
        elif botao == 6:
            self.temp_ref += 10
        elif botao == 7:
            self.temp_ref -= 10
        elif botao == 8:
            self.abre_menu()

    def trata_temperatura(self, temperatura):
        self.temp_atual = temperatura

    def atualiza_lcd(self):
        while True:
            if self.ligado:
                if self.funcionando:
                    lcd.text('Hello World!', 1)
                else:
                    lcd.text('Raspberry Pi', 2)
            else:
                lcd.clear()
                print("Desligado")
            time.sleep(1)

    def verifica_botoes(self):
        comando = b'\x01\x23\xc3'

        while True:
            self.uart.envia(comando, self.matricula)
            time.sleep(0.2)
            recebido = self.uart.recebe()
            trata_botao(recebido)
            time.sleep(0.3)

    def verifica_temperatura(self):
        comando = b'\x01\x23\xc1'

        while True:
            self.uart.envia(comando, self.matricula)
            time.sleep(0.2)
            recebido = self.uart.recebe()
            trata_temperatura(recebido)
            time.sleep(0.8)
    
    def inicia_servicos(self):
        thread_botoes = Thread(target=self.verifica_botoes, args=())
        thread_botoes.start()

        time.sleep(0.5)

        thread_temperatura = Thread(target=self.verifica_temperatura, args=())
        thread_temperatura.start()

        time.sleep(0.5)

        thread_lcd = Thread(target=self.atualiza_lcd, args=())
        thread_lcd.start()

AirFryer()