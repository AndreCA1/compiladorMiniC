from Lexico import Lexico
from Sintatico import Sintatico

class Tradutor:
    def __init__(self):
        self.nomeArq = "exampleWrong.c"

    def inicializa(self):
        self.arq = open(self.nomeArq, "r")
        self.lexico = Lexico(self.arq)
        self.sintatico = Sintatico(self.lexico, "./saida.py")

    def traduz(self):
        self.sintatico.program()

    def finaliza(self):
        self.arq.close()

# inicia a traducao
if __name__ == '__main__':
    try:
        x = Tradutor()
        x.inicializa()
        x.traduz()
        x.finaliza()
    except Exception as e:
        print(e)