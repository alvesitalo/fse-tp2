import csv

class CSV:   
    def __init__(self):
        self.file = open('log.csv', 'w')
        self.writer = csv.writer(self.file)

    def escrever(self, linha):
        self.writer.writerow(linha)
    
    def fechar(self):
        self.file.close()
