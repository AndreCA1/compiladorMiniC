from tokens import TOKEN

class Semantico:
    def __init__(self, nomeAlvo):
        self.indent = 0
        self.escopos = [{}]
        self.alvo = open(nomeAlvo, "wt")
        self.tabelaOperacoes = TOKEN.tabelaOperacoes()

        self.declaraFuncao("putchar", TOKEN.valorChar,[{}, (TOKEN.valorChar, "c", False)])
        self.declaraFuncao("putstr", TOKEN.valorString,[{}, (TOKEN.valorString, "s", False)])
        self.declaraFuncao("putint", TOKEN.valorInt,[{}, (TOKEN.valorInt, "i", False)])
        self.declaraFuncao("putfloat", TOKEN.valorFloat,[{}, (TOKEN.valorFloat, "f", False)])
        self.declaraFuncao("getchar", TOKEN.valorChar, [{}])
        self.declaraFuncao("getint", TOKEN.valorInt, [{}])
        self.declaraFuncao("getfloat", TOKEN.valorFloat, [{}])

    def finaliza(self):
        self.alvo.close()

    def mais_indent(self):
        self.indent += 1

    def menos_indent(self):
        self.indent -= 1

    def entra_escopo(self):
        self.escopos.append({})

    def sai_escopo(self):
        self.escopos.pop()

    def declaraFuncao(self, nome, tipo, argumentos):
        escopo_global = self.escopos[-1]

        if nome in escopo_global:
            raise Exception(f"Identificador '{nome}' já declarado.")

        funcao = [(tipo, False)]
        # Verifica se é uma tupla e adiciona a uma nova lsita argumentos_validos
        argumentos_validos = [arg for arg in argumentos if isinstance(arg, tuple)]

        for tipo_arg, nome_arg, vet_arg in argumentos_validos:
            funcao.append((tipo_arg, vet_arg))

        escopo_global[nome] = (funcao)

        self.entra_escopo()

        for tipo_arg, nome_arg, vet_arg in argumentos_validos:
            self.declaraVariavel(nome_arg, tipo_arg, vet_arg)

    def declaraVariavel(self, nome, tipo, vet):
        escopo_atual = self.escopos[-1]
        if nome in escopo_atual:
            raise Exception(f"Identificador '{nome}' já declarado neste escopo")
        escopo_atual[nome] = tipo, vet

    #retorna uma tupla com o tipo do identificador Ex: (TOKEN.valorInt, False)
    def verifica_declaracao(self, nome):
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        print(f'Erro semântico: "{nome}" não foi declarado.')
        raise Exception(f'Erro semântico: "{nome}" não foi declarado.')

    def verifica_tipo(self, tipo_esperado, tipo_real):
        if tipo_esperado == TOKEN.valorFloat and tipo_real == TOKEN.valorInt:
            return
        if tipo_esperado == TOKEN.valorInt and tipo_real == TOKEN.valorFloat:
            return
        if tipo_esperado == TOKEN.valorInt and tipo_real == TOKEN.valorChar:
            return
        if tipo_esperado == TOKEN.valorChar and tipo_real == TOKEN.valorInt:
            return
        if tipo_esperado != tipo_real:
            msg_esperado = TOKEN.msg(tipo_esperado)
            msg_real = TOKEN.msg(tipo_real)
            raise Exception(f'Tipo incompatível. Esperado {msg_esperado}, mas recebido {msg_real}.')

    def obter_tipo_token(self, ident, linha, coluna):
        try:
            for escopo in self.escopos:
                if ident in escopo:
                    return escopo[ident]
            raise Exception(f'Variável "{ident}" não declarada. Linha: {linha}, coluna: {coluna}')
        except Exception as e:
            print(f"Erro inesperado: {e}")
            exit(1)

    def verifica_operacao(self, operacao: list):
        #verifica se é uma operação unitaria como a = -1
        if len(operacao) == 2:
            op = (operacao[0], (operacao[1][0], operacao[1][1]))
        else:
            # operacao vem com o LVALUE, portanto é preciso criar a op com apenas o tipo e se é vetor
            op = ((operacao[0][0], operacao[0][1]), operacao[1], (operacao[2][0], operacao[2][1]))
        entrada = frozenset(op)
        if entrada in self.tabelaOperacoes:
            teste = self.tabelaOperacoes[entrada]
            return teste
        else:
            msg = f"Operação inválida: {TOKEN.msg(operacao[0][0])} {TOKEN.msg(operacao[1])} {TOKEN.msg(operacao[2][0])}" if len(
                operacao) == 3 else f"Operação inválida: {TOKEN.msg(operacao[0])} {TOKEN.msg(operacao[1][0])}"
            raise Exception(msg)

    def erro_semantico(self, tokenAtual, msg):
        (token, lexema, linha, coluna) = tokenAtual
        print(f'Erro na linha {linha}, coluna {coluna}:')
        print(f'{msg}')
        raise Exception

    def gera(self, nivel, codigo):
        identacao = ' ' * 4 * nivel
        linha = identacao + codigo
        self.alvo.write(linha)

    def gera_chamada_builtin(self, nome, args):
        if nome == "putstr":
            return f"print({args}, end='')"
        if nome == "putint":
            return f"print({args}, end='')"
        if nome == "putchar":
            return f"print(chr({args}), end='')"
        if nome == "getint":
            return "int(input())"
