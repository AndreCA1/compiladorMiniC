from tokens import TOKEN
from colorama import init, Fore

class Lexico:
    def __init__(self, arqFonte):
        self.arqFonte = arqFonte
        self.fonte = self.arqFonte.read()
        self.tamFonte = len(self.fonte)
        self.indiceFonte = 0
        self.linha = 1
        self.coluna = 0

    def fimDoArquivo(self):
        return self.indiceFonte >= self.tamFonte

    def getChar(self):
        if self.fimDoArquivo():
            return '\0'
        car = self.fonte[self.indiceFonte]
        self.indiceFonte += 1
        if car == '\n':
            self.linha += 1
            self.coluna = 0
        else:
            self.coluna += 1
        return car

    def unGetChar(self, simbolo):
        if simbolo == '\n':
            self.linha -= 1
        if self.indiceFonte > 0:
            self.indiceFonte -= 1
        self.coluna -= 1

    def imprimirToken(self, tokenCorrente):
        (token, lexema, linha, coluna) = tokenCorrente

        #MOSTRA SÓ ERROS
        # if token == TOKEN.erro:
        #     msg = TOKEN.msg(token)
        #     print(Fore.GREEN + '(tk = ' + Fore.RED + str(msg) +
        #             Fore.GREEN + ' lex = ' + Fore.YELLOW + str(lexema) +
        #             Fore.GREEN + ' lin = ' + Fore.RESET + str(linha) +
        #             Fore.GREEN + ' col = ' + Fore.RESET + str(coluna))

        #MOSTRA TODOS
        msg = TOKEN.msg(token)

        if token == TOKEN.erro:
            print(Fore.GREEN + '(tk = ' + Fore.RED + str(msg), end = '')
        else:
            print(Fore.GREEN + '(tk = ' + Fore.BLUE + str(msg), end = '')

        print(Fore.GREEN + ' lex = ' + Fore.YELLOW + str(lexema) +
              Fore.GREEN + ' lin = ' + Fore.RESET + str(linha) +
              Fore.GREEN + ' col = ' + Fore.RESET + str(coluna))

    def getToken(self):
        simbolo = self.getChar()
        lexema = ''

        while True:
            lin = self.linha
            col = self.coluna


            #Ignora comentários
            if simbolo == "/":
                prox = self.getChar()
                if prox == "/":
                    while simbolo != "\n" and simbolo != '\0':
                        simbolo = self.getChar()
                    simbolo = self.getChar()
                    continue
                else:
                    self.unGetChar(prox)
                    return TOKEN.divisao, "/", lin, col

            elif simbolo in [" ", "\n"] :
                simbolo = self.getChar()
                continue

            elif simbolo.isalpha() or simbolo == "_":
                estado = 2
                palavra = simbolo
                while True:
                    simbolo = self.getChar()
                    if not (simbolo.isalnum() or simbolo == "_"):
                        self.unGetChar(simbolo)
                        break
                    palavra += simbolo

                tk = TOKEN.reservada(palavra)
                return tk, palavra, lin, col

            elif simbolo.isdigit():
                numero = simbolo
                tem_ponto = False
                while True:
                    simbolo = self.getChar()
                    if simbolo.isalpha():
                        numero += simbolo
                        return TOKEN.erro, numero, lin, col

                    if simbolo == ".":
                        if not tem_ponto:
                            tem_ponto = True
                            numero += simbolo
                            prox = self.getChar()
                            if not prox.isdigit():
                                return TOKEN.erro, numero, lin, col
                            self.unGetChar(prox)
                        else:
                            numero += simbolo
                            return TOKEN.erro, numero, lin, col
                    elif simbolo.isdigit():
                        numero += simbolo
                    else:

                        self.unGetChar(simbolo)
                        break
                if tem_ponto:
                    return TOKEN.valorFloat, numero, lin, col
                else:
                    return TOKEN.valorInt, numero, lin, col

            elif simbolo == '"':
                string = ""
                simbolo = self.getChar()
                while simbolo != '"' and simbolo != '\0':
                    string += simbolo
                    simbolo = self.getChar()

                string = '"' + string + '"'
                return TOKEN.valorString, string, lin, col

            elif simbolo == "'":
                lexema = "'"
                simbolo = self.getChar()

                if simbolo == "\\":
                    lexema += simbolo
                    prox = self.getChar()
                    lexema += prox

                    if prox == "n":
                        char_val = "\\n"
                    else:
                        return TOKEN.erro, lexema, lin, col

                    simbolo = self.getChar()
                    lexema += simbolo
                    while simbolo != "'":
                        simbolo = self.getChar()
                        lexema += simbolo
                        return TOKEN.erro, lexema, lin, col

                    return TOKEN.valorChar, char_val, lin, col

                else:
                    lexema += simbolo
                    char_val = simbolo
                    simbolo = self.getChar()
                    lexema += simbolo

                    if simbolo != "'":
                        while simbolo != "'" and simbolo != '\0':
                            simbolo = self.getChar()
                            lexema += simbolo
                        return TOKEN.erro, lexema, lin, col

                    return TOKEN.valorChar, char_val, lin, col

            elif simbolo == '&':
                prox = self.getChar()
                if prox == '&':
                    return TOKEN.AND, '&&', lin, col
                else:
                    return TOKEN.erro, '&', lin, col

            elif simbolo == '|':
                prox = self.getChar()
                if prox == '|':
                    return TOKEN.OR, '||', lin, col
                else:
                    return TOKEN.erro, '|', lin, col


            elif simbolo == "=":
                prox = self.getChar()
                if prox == "=":
                    return TOKEN.opRel, "==", lin, col
                else:
                    self.unGetChar(prox)
                    return TOKEN.atrib, "=", lin, col

            elif simbolo == "!":
                prox = self.getChar()
                if prox == "=":
                    return TOKEN.opRel, "!=", lin, col
                else:
                    self.unGetChar(prox)
                    return TOKEN.NOT, "!", lin, col

            elif simbolo == ">":
                prox = self.getChar()
                if prox == "=":
                    return TOKEN.opRel, ">=", lin, col
                else:
                    self.unGetChar(prox)
                    return TOKEN.opRel, ">", lin, col

            elif simbolo == "<":
                prox = self.getChar()
                if prox == "=":
                    return TOKEN.opRel, "<=", lin, col
                else:
                    self.unGetChar(prox)
                    return TOKEN.opRel, "<", lin, col

            elif simbolo == "{":
                return TOKEN.abreChaves, "{", lin, col
            elif simbolo == "}":
                return TOKEN.fechaChaves, "}", lin, col
            elif simbolo == "(":
                return TOKEN.abreParenteses, "(", lin, col
            elif simbolo == ")":
                return TOKEN.fechaParenteses, ")", lin, col
            elif simbolo == "[":
                return TOKEN.abreColchetes, "[", lin, col
            elif simbolo == "]":
                return TOKEN.fechaColchetes, "]", lin, col
            elif simbolo == ",":
                return TOKEN.virgula, ",", lin, col
            elif simbolo == ";":
                return TOKEN.pontoVirgula, ";", lin, col
            elif simbolo == "+":
                return TOKEN.mais, "+", lin, col
            elif simbolo == "-":
                return TOKEN.menos, "-", lin, col
            elif simbolo == "*":
                return TOKEN.multiplicacao, "*", lin, col
            elif simbolo == "%":
                return TOKEN.porcentagem, "%", lin, col

            elif simbolo == "\0":
                return TOKEN.fimarquivo, "<eof>", lin, col

            else:
                return TOKEN.erro, simbolo, lin, col


if __name__ == '__main__':
    init()
    with open("exampleWrite.c", "r", encoding="utf-8") as arqFonte:
        lexico = Lexico(arqFonte)
        token = lexico.getToken()
        while token[0] != TOKEN.fimarquivo:
            lexico.imprimirToken(token)
            token = lexico.getToken()
        lexico.imprimirToken(token)