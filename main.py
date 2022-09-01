import serial
import time
from threading import Thread

from connection.uart import Uart

class AirFryer:
    port = "/dev/serial0"
    baudrate = 9600
    timeout = 2
    matricula = [3, 6, 6, 6]

    def __init__(self):
        self.uart = Uart(self.port, self.baudrate, self.timeout)
        self.inicia_servicos()

    def verifica_botoes(self):
        comando = b'\x01\x23\xc3'

        while True:
            self.uart.envia(comando, self.matricula)
            time.sleep(0.2)
            recebido = self.uart.recebe()
            time.sleep(0.3)

    def verifica_temperatura(self):
        comando = b'\x01\x23\xc1'

        while True:
            self.uart.envia(comando, self.matricula)
            time.sleep(0.2)
            recebido = self.uart.recebe()
            time.sleep(0.8)

    def inicia_servicos(self):
        thread_botoes = Thread(target=self.verifica_botoes, args=())
        thread_botoes.start() 

        thread_temperatura = Thread(target=self.verifica_temperatura, args=())
        thread_temperatura.start()

AirFryer()