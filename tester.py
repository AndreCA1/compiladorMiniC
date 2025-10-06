from Lexico import lexico
import Sintatico

if __name__ == '__main__':
    with open("example.c", "r") as arqFonte:
        lexico = lexico(arqFonte)
        parser = Sintatico.sintatico(lexico)

        try:
            parser.program()
            print("Programa reconhecido com sucesso!")
        except Exception as e:
            print("Erro de sintaxe:", e)
