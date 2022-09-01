import serial

from utils.crc16 import calcula_CRC

class Uart:
    conectado = False

    def __init__(self, port, baudrate, timeout=2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.conecta()

    def conecta(self):
        self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

        if (self.serial.isOpen()):
            self.conectado = True
            print("Porta aberta, conexao realizada")
        else:
            self.conectado = False
            print("Porta fechada, conexao nao realizada")
    
    def desconecta(self):
        self.serial.close()
        self.conectado = False
        print("Porta fechada")

    def envia(self, comando, matricula):
        if (self.conectado):
            m1 = comando + bytes(matricula)
            m2 = calcula_CRC(m1, 7).to_bytes(2, 'little')
            msg = m1 + m2
            self.serial.write(msg)
            print("Mensagem enviada: {}".format(msg))
        else:
            self.conecta()

    def recebe(self):
        if (self.conectado):
            data = self.serial.read(10)
            print("Mensagem recebida: {}".format(data))
            return data
        else:
            self.conecta()
            return None
