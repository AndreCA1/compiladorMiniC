from Lexico import lexico
from Sintatico import sintatico

if __name__ == '__main__':
    # with open("exampleCorrect.c", "r", encoding="utf-8") as arqFonte:
    #     lexico = lexico(arqFonte)
    #     parser = sintatico(lexico)
    #
    #     try:
    #         parser.program()
    #         print("Programa correto reconhecido com sucesso!")
    #     except Exception as e:
    #         print("Erro de sintaxe:", e)

    with open("exampleWrong.c", "r", encoding="utf-8") as arqFonte:
        lexico = lexico(arqFonte)
        parser = sintatico(lexico)

        try:
            parser.program()
            print("Programa errado reconhecido como correto!")
        except Exception as e:
            print("Erro de sintaxe:", e)
