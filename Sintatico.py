from tokens import TOKEN
from Semantico import Semantico

class Sintatico:
    def __init__(self, lexico, nomeAlvo):
        self.lexico = lexico
        self.lexico.tokenLido = self.lexico.getToken()
        self.semantico = Semantico(nomeAlvo)

    def consome(self, tokenAtual):
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.erro:
            print(f"\nErro Léxico na linha {linha}, coluna {coluna}: {lexema}")
            exit(1)

        if tokenAtual == token:
            self.lexico.tokenLido = self.lexico.getToken()
        else:
            msgTokenLido = TOKEN.msg(token)
            msgTokenAtual = TOKEN.msg(tokenAtual)
            if token == TOKEN.erro:
                msg = lexema
            else:
                msg = msgTokenLido

            print(f'Era esperado {msgTokenAtual} mas veio {msg} Linha: {linha} Coluna: {coluna}')

    def program(self):
        # Program -> Function Program | LAMBDA
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        identificadores = {
            TOKEN.INT,
            TOKEN.FLOAT,
            TOKEN.CHAR,
        }

        if token in identificadores:
            self.function()
            self.program()
        elif token == TOKEN.fimarquivo:
            self.consome(TOKEN.fimarquivo)
            return

    def function(self):
        # Function -> Type ident ( ArgList ) CompoundStmt
        tipo = self.type()
        nome_funcao = self.lexico.tokenLido[1]
        self.consome(TOKEN.ident)
        self.consome(TOKEN.abreParenteses)
        argumentos = self.argList()
        self.consome(TOKEN.fechaParenteses)

        #declara a função e entra no escopo dela
        self.semantico.declaraFuncao(nome_funcao, tipo, argumentos)

        #corpo da função
        self.consome(TOKEN.abreChaves)
        self.stmtList()
        self.consome(TOKEN.fechaChaves)
        self.semantico.sai_escopo()


    def argList(self):
        # ArgList -> Arg RestoArgList | LAMBDA

        primeiros_arg = {
            TOKEN.INT,
            TOKEN.FLOAT,
            TOKEN.CHAR,
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido
        args = [{}]
        if token in primeiros_arg:
            argumento = self.arg()
            args.append(argumento)
            self.restoArgList(args)
            return args
        elif token == TOKEN.fechaParenteses:
            return args
        else:
            print(f'Erro em argList: esperado tipo (int, float, char) ou fechaParenteses, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')

    def restoArgList(self, args):
        # RestoArgList -> , Arg RestoArgList | LAMBDA
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            argumento = self.arg()
            args.append(argumento)
            self.restoArgList(args)
        elif token == TOKEN.fechaParenteses:
            return args
        else:
            print(f'Erro em restoArgList: esperado vírgula ou fechaParenteses, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')

    # Retorna uma tripla (TOKEN.TIPO, nome_arg, True or False)
    def arg(self):
        # Arg -> Type IdentArg
        tipo = self.type()
        nome, vet = self.identArg()
        return tipo, nome, vet

    #Retorna uma tupla (nome_arg, True or False)
    def identArg(self):
        # IdentArg -> ident OpcIdentArg
        nome = self.lexico.tokenLido[1]
        self.consome(TOKEN.ident)
        vet = self.opcIdentArg()
        return nome, vet

    #Retorna True or False se for ou não vetor
    def opcIdentArg(self):
        # OpcIdentArg -> [ ] | LAMBDA
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.abreColchetes:
            self.consome(TOKEN.abreColchetes)
            self.consome(TOKEN.fechaColchetes)
            return True
        elif token in {TOKEN.virgula, TOKEN.fechaParenteses}:
            # LAMBDA
            return False
        else:
            print(f'Erro em opcIdentArg: esperado abreColchete, vírgula ou fechaParenteses, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')

    def compoundStmt(self):
        # CompoundStmt -> { StmtList }
        # Blocos aninhados (dentro de if, while...)

        #entra em um novo escopo aninhado
        self.semantico.entra_escopo()
        self.consome(TOKEN.abreChaves)
        self.stmtList()
        self.consome(TOKEN.fechaChaves)
        self.semantico.sai_escopo()

    def stmtList(self):
        # StmtList -> Stmt StmtList | LAMBDA

        primeiros_stmt = {
            TOKEN.FOR, TOKEN.WHILE, TOKEN.IF, TOKEN.abreChaves,
            TOKEN.BREAK, TOKEN.CONTINUE, TOKEN.RETURN,
            TOKEN.INT, TOKEN.FLOAT, TOKEN.CHAR,
            TOKEN.ident, TOKEN.abreParenteses,
            TOKEN.valorInt, TOKEN.valorFloat, TOKEN.valorChar, TOKEN.valorString,
            TOKEN.pontoVirgula,
            TOKEN.mais, TOKEN.menos, TOKEN.NOT
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token in primeiros_stmt:
            self.stmt()
            self.stmtList()
        elif token == TOKEN.fechaChaves:
            return
        else:
            print(
                f'Erro em stmtList: esperado token inicial de um comando ou fechaChaves, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def stmt(self):
        # Stmt -> ForStmt | WhileStmt | IfStmt | CompoundStmt | break ; | continue ; | return Expr ; | Expr ; | Declaration | ;

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.FOR:
            self.forStmt()
        elif token == TOKEN.WHILE:
            self.whileStmt()
        elif token == TOKEN.IF:
            self.ifStmt()
        elif token == TOKEN.abreChaves:
            self.compoundStmt()
        elif token == TOKEN.BREAK:
            self.consome(TOKEN.BREAK)
            self.consome(TOKEN.pontoVirgula)
        elif token == TOKEN.CONTINUE:
            self.consome(TOKEN.CONTINUE)
            self.consome(TOKEN.pontoVirgula)
        elif token == TOKEN.RETURN:
            self.consome(TOKEN.RETURN)
            self.expr()
            self.consome(TOKEN.pontoVirgula)
        elif token in {TOKEN.INT, TOKEN.FLOAT, TOKEN.CHAR}:
            self.declaration()
        elif token == TOKEN.pontoVirgula:
            self.consome(TOKEN.pontoVirgula)

        elif token in {
            TOKEN.ident, TOKEN.abreParenteses,
            TOKEN.valorInt, TOKEN.valorFloat, TOKEN.valorChar, TOKEN.valorString,
            TOKEN.mais, TOKEN.menos, TOKEN.NOT
        }:
            self.expr()
            self.consome(TOKEN.pontoVirgula)
        else:
            print(f'Erro em stmt: comando inesperado: {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def forStmt(self):
        # ForStmt -> for ( Expr ; OptExpr ; OptExpr ) Stmt
        self.consome(TOKEN.FOR)
        self.consome(TOKEN.abreParenteses)
        self.expr()
        self.consome(TOKEN.pontoVirgula)
        self.optExpr()
        self.consome(TOKEN.pontoVirgula)
        self.optExpr()
        self.consome(TOKEN.fechaParenteses)
        self.stmt()

    def optExpr(self):
        # OptExpr -> Expr | LAMBDA

        primeiros_expr = {
            TOKEN.ident, TOKEN.abreParenteses,
            TOKEN.valorInt, TOKEN.valorFloat, TOKEN.valorChar, TOKEN.valorString,
            TOKEN.mais, TOKEN.menos, TOKEN.NOT
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token in primeiros_expr:
            self.expr()
        elif token in {TOKEN.pontoVirgula, TOKEN.fechaParenteses}:
            # LAMBDA
            return
        else:
            print(
                f'Erro em optExpr: esperado início de expressão, pontoVirgula ou fechaParenteses, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def whileStmt(self):
        # WhileStmt -> while ( Expr ) Stmt
        self.consome(TOKEN.WHILE)
        self.consome(TOKEN.abreParenteses)
        self.expr()
        self.consome(TOKEN.fechaParenteses)
        self.stmt()

    def ifStmt(self):
        # IfStmt -> if ( Expr ) Stmt ElsePart
        self.consome(TOKEN.IF)
        self.consome(TOKEN.abreParenteses)
        self.expr()
        self.consome(TOKEN.fechaParenteses)
        self.stmt()
        self.elsePart()

    def elsePart(self):
        # ElsePart -> else Stmt | LAMBDA

        primeiros_follow_stmt = {
            TOKEN.FOR, TOKEN.WHILE, TOKEN.IF, TOKEN.abreChaves,
            TOKEN.BREAK, TOKEN.CONTINUE, TOKEN.RETURN,
            TOKEN.INT, TOKEN.FLOAT, TOKEN.CHAR,
            TOKEN.ident, TOKEN.abreParenteses,
            TOKEN.valorInt, TOKEN.valorFloat, TOKEN.valorChar, TOKEN.valorString,
            TOKEN.pontoVirgula, TOKEN.fechaChaves,
            TOKEN.mais, TOKEN.menos, TOKEN.NOT, TOKEN.fimarquivo
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            self.stmt()
        elif token in primeiros_follow_stmt:
            return
        else:
            print(
                f'Erro em elsePart: esperado else ou token inicial de um novo comando, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def declaration(self):
        # Declaration -> Type IdentList ;
        tipo = self.type()
        self.identList(tipo)
        self.consome(TOKEN.pontoVirgula)

    def type(self):
        # Type -> int | float | char
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.INT:
            self.consome(TOKEN.INT)
            return TOKEN.valorInt
        elif token == TOKEN.FLOAT:
            self.consome(TOKEN.FLOAT)
            return TOKEN.valorFloat
        elif token == TOKEN.CHAR:
            self.consome(TOKEN.CHAR)
            return TOKEN.valorChar
        else:
            print(f'Erro em type: esperado int, float ou char, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')
            exit(1)

    def identList(self, tipo):
        # IdentList -> IdentDeclar RestoIdentList
        self.identDeclar(tipo)
        self.restoIdentList(tipo)

    def restoIdentList(self, tipo):
        # RestoIdentList -> , IdentDeclar RestoIdentList | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            self.identDeclar(tipo)
            self.restoIdentList(tipo)
        elif token == TOKEN.pontoVirgula:
            return
        else:
            print(f'Erro em restoIdentList: esperado vírgula ou pontoVirgula, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')
            exit(1)

    def identDeclar(self, tipo):
        # IdentDeclar -> ident OpcIdentDeclar
        nome_variavel = self.lexico.tokenLido[1]
        self.consome(TOKEN.ident)
        eh_vetor = self.opcIdentDeclar()
        self.semantico.declaraVariavel(nome_variavel, tipo, eh_vetor)

    # Retorna True se for um vetor, False caso contrário
    def opcIdentDeclar(self):
        # OpcIdentDeclar -> [ valorInt ] | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.abreColchetes:
            self.consome(TOKEN.abreColchetes)
            self.consome(TOKEN.valorInt)
            self.consome(TOKEN.fechaColchetes)
            return True
        elif token in {TOKEN.virgula, TOKEN.pontoVirgula}:
            return False
        else:
            print(
                f'Erro em opcIdentDeclar: esperado abreColchetes, vírgula ou pontoVirgula, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')
            return False

    def expr(self):
        # Expr -> Log RestoExpr
        tipo_log = self.log()
        return self.restoExpr(tipo_log)

    def restoExpr(self, tipo_esquerda):
        # RestoExpr -> = Expr RestoExpr | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        primeiros_follow_expr = {
            TOKEN.pontoVirgula, TOKEN.fechaParenteses,
            TOKEN.virgula, TOKEN.fechaColchetes
        }

        if token == TOKEN.atrib:
            lvalue = tipo_esquerda[2]
            if not lvalue:
                raise Exception(
                    f"Erro Semântico: Expressão à esquerda do '=' não é atribuível (não é um L-value). Linha: {linha}, Coluna: {coluna}")

            self.consome(TOKEN.atrib)

            tipo_direita = self.expr()

            self.semantico.verifica_tipo(tipo_esquerda[0], tipo_direita[0])

            tipo_resultado = (tipo_direita[0], tipo_esquerda[1], False)

            return self.restoExpr(tipo_resultado)

        elif token in primeiros_follow_expr:
            #LAMBDA
            return tipo_esquerda
        else:
            print(
                f'Erro em restoExpr: esperado igual ou token de fim de expressão, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def log(self):
        # Log -> Nao RestoLog
        tipo_esquerda = self.nao()
        return self.restoLog(tipo_esquerda)

    def restoLog(self, tipo_esquerda):
        # RestoLog -> AND Nao RestoLog | OR Nao RestoLog | LAMBDA

        primeiros_follow_log = {
            TOKEN.atrib, TOKEN.pontoVirgula, TOKEN.fechaParenteses,
            TOKEN.virgula, TOKEN.fechaColchetes
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.AND:
            self.consome(TOKEN.AND)
            tipo_direita = self.nao()

            op = [tipo_esquerda, TOKEN.AND, tipo_direita]
            tipo_result_op = self.semantico.verifica_operacao(op)

            tipo_para_proximo = (tipo_result_op[0], tipo_result_op[1], False)

            return self.restoLog(tipo_para_proximo)

        elif token == TOKEN.OR:
            self.consome(TOKEN.OR)
            tipo_direita = self.nao()

            op = [tipo_esquerda, TOKEN.OR, tipo_direita]
            tipo_result_op = self.semantico.verifica_operacao(op)

            tipo_para_proximo = (tipo_result_op[0], tipo_result_op[1], False)

            return self.restoLog(tipo_para_proximo)

        elif token in primeiros_follow_log:
            return tipo_esquerda
        else:
            print(
                f'Erro em restoLog: esperado AND, OR, igual ou token de fim de expressão, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def nao(self):
        # Nao -> NOT Nao | Rel
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.NOT:
            self.consome(TOKEN.NOT)

            tipo_filho = self.nao()

            op = [TOKEN.NOT, tipo_filho]

            try:
                tipo_resultante_op = self.semantico.verifica_operacao(op)
            except Exception as e:
                print(f"Erro Semântico na Linha {linha}, Coluna {coluna}: {e}")
                raise Exception("Operação 'NOT' inválida.")

            return tipo_resultante_op[0], tipo_resultante_op[1], False

        else:
            return self.rel()

    def rel(self):
        # Rel -> Soma RestoRel
        tipo_esquerda = self.soma()
        return self.restoRel(tipo_esquerda)

    def restoRel(self, tipo_esquerda):
        # RestoRel -> opRel Soma | LAMBDA

        primeiros_follow_rel = {
            TOKEN.AND, TOKEN.OR, TOKEN.atrib,
            TOKEN.pontoVirgula, TOKEN.fechaParenteses,
            TOKEN.virgula, TOKEN.fechaColchetes
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.opRel:
            self.consome(TOKEN.opRel)
            tipo_direita = self.soma()

            op = [tipo_esquerda, TOKEN.opRel, tipo_direita]
            tipo_result_op = self.semantico.verifica_operacao(op)

            tipo_para_proximo = (tipo_result_op[0], tipo_result_op[1], False)

            return  tipo_para_proximo

        elif token in primeiros_follow_rel:
            # LAMBDA
            return tipo_esquerda
        else:
            print(f'Erro em restoRel: esperado operador relacional ({TOKEN.msg(TOKEN.opRel)}) ou token de fim de expressão, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def soma(self):
        # Soma -> Mult RestoSoma
        tipo_esquerda = self.mult()
        return self.restoSoma(tipo_esquerda)

    def restoSoma(self, tipo_esquerda):
        # RestoSoma -> + Mult RestoSoma | - Mult RestoSoma | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.mais:
            self.consome(TOKEN.mais)
            tipo_direita = self.mult()  # (TIPO, VET, LVALUE)

            # Passo 3: Validar Operação
            op = [tipo_esquerda, TOKEN.mais, tipo_direita]
            tipo_result_op = self.semantico.verifica_operacao(op)  # Retorna (TIPO, VET)

            # Resultado de a+b não é L-value
            tipo_para_proximo = (tipo_result_op[0], tipo_result_op[1], False)

            return self.restoSoma(tipo_para_proximo)

        elif token == TOKEN.menos:
            self.consome(TOKEN.menos)
            tipo_direita = self.mult()

            op = [tipo_esquerda, TOKEN.menos, tipo_direita]
            tipo_result_op = self.semantico.verifica_operacao(op)

            tipo_para_proximo = (tipo_result_op[0], tipo_result_op[1], False)

            return self.restoSoma(tipo_para_proximo)

        else:
            #LAMBDA
            return tipo_esquerda

    def mult(self):
        # Mult -> Uno RestoMult
        tipo_esquerda = self.uno()
        return self.restoMult(tipo_esquerda)

    def restoMult(self, tipo_esquerda):
        # RestoMult -> * Uno RestoMult | / Uno RestoMult | % Uno RestoMult | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.multiplicacao:
            self.consome(TOKEN.multiplicacao)
            tipo_direita = self.uno()

            op = [tipo_esquerda, TOKEN.multiplicacao, tipo_direita]
            tipo_result_op = self.semantico.verifica_operacao(op)

            tipo_para_proximo = (tipo_result_op[0], tipo_result_op[1], False)

            return self.restoMult(tipo_para_proximo)

        elif token == TOKEN.divisao:
            self.consome(TOKEN.divisao)
            tipo_direita = self.uno()

            op = [tipo_esquerda, TOKEN.divisao, tipo_direita]
            tipo_result_op = self.semantico.verifica_operacao(op)

            tipo_para_proximo = (tipo_result_op[0], tipo_result_op[1], False)

            return self.restoMult(tipo_para_proximo)

        elif token == TOKEN.porcentagem:
            self.consome(TOKEN.porcentagem)
            tipo_direita = self.uno()

            op = [tipo_esquerda, TOKEN.porcentagem, tipo_direita]
            tipo_result_op = self.semantico.verifica_operacao(op)

            tipo_para_proximo = (tipo_result_op[0], tipo_result_op[1], False)

            return self.restoMult(tipo_para_proximo)

        else:
            return tipo_esquerda

    def uno(self):
        # Uno -> + Uno | - Uno | Folha
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.mais:
            self.consome(TOKEN.mais)

            tipo_filho = self.uno()

            op = [TOKEN.mais, tipo_filho]

            try:
                tipo_resultante_op = self.semantico.verifica_operacao(op)
            except Exception as e:
                print(f"Erro Semântico na Linha {linha}, Coluna {coluna}: {e}")
                raise Exception("Operação unária '+' inválida.")

            return tipo_resultante_op[0], tipo_resultante_op[1], False

        elif token == TOKEN.menos:
            self.consome(TOKEN.menos)

            tipo_filho = self.uno()

            op = [TOKEN.menos, tipo_filho]

            try:
                tipo_resultante_op = self.semantico.verifica_operacao(op)
            except Exception as e:
                print(f"Erro Semântico na Linha {linha}, Coluna {coluna}: {e}")
                raise Exception("Operação unária '-' inválida.")

            return tipo_resultante_op[0], tipo_resultante_op[1], False

        else:
            return self.folha()

    #Retorna o tipo do identificador
    def folha(self):
        # Folha -> ( Expr ) | Identifier | valorInt | valorFloat | valorChar | valorString
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.abreParenteses:
            self.consome(TOKEN.abreParenteses)
            tipo = self.expr()
            self.consome(TOKEN.fechaParenteses)
            return tipo[0], tipo[1], False

        elif token == TOKEN.ident:
            return self.identifier()

        elif token == TOKEN.valorInt:
            self.consome(TOKEN.valorInt)
            return TOKEN.valorInt, False, False

        elif token == TOKEN.valorFloat:
            self.consome(TOKEN.valorFloat)
            return TOKEN.valorFloat, False, False

        elif token == TOKEN.valorChar:
            self.consome(TOKEN.valorChar)
            return TOKEN.valorChar, False, False

        elif token == TOKEN.valorString:
            self.consome(TOKEN.valorString)
            return TOKEN.valorString, False, False

        else:
            print(
                f'Erro em folha: esperado (, ident, valorInt, valorFloat, valorChar, valorString, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def identifier(self):
        # Identifier -> ident OpcIdentifier
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        # Descobre o tipo do identificador passando seu nome
        tipo = self.semantico.verifica_declaracao(lexema)

        self.consome(TOKEN.ident)

        return self.opcIdentifier(tipo, lexema)

    def opcIdentifier(self, tipo, nome):
        # OpcIdentifier -> [ Expr ] | ( Params ) | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.abreColchetes:
            # se não for tupla é uma função
            if not isinstance(tipo, tuple):
                raise Exception(
                    f"Erro Semântico: '{nome}' é uma função e não pode ser acessado com []. Linha: {linha}, Coluna: {coluna}")

            # verificar se é vetor a partir da tupla
            if not tipo[1]:
                raise Exception(f"Erro Semântico: '{nome}' não é um vetor e não pode ser acessado com []. Linha: {linha}, Coluna: {coluna}")

            self.consome(TOKEN.abreColchetes)
            tipo_indice = self.expr()

            # verifica se é inteiro, já que indices só podem ser inteiros
            self.semantico.verifica_tipo(TOKEN.valorInt, tipo_indice[0])

            self.consome(TOKEN.fechaColchetes)

            # Retorna o valor daquela posição do vetor, que não é um vetor
            return tipo[0], False, True

        elif token == TOKEN.abreParenteses:
            # Validação Semântica 1: Símbolo é uma função (list)?
            if not isinstance(tipo, list):
                raise Exception(f"Erro Semântico: '{nome}' não é uma função. Linha: {linha}, Coluna: {coluna}")

            assinatura_func = tipo
            tipo_retorno = assinatura_func[0]  # (TIPO_RETORNO, False)
            params_esperados = assinatura_func[1:]  # [(TIPO_ARG1, VET_ARG1), ...]

            self.consome(TOKEN.abreParenteses)

            # Pega os tipos dos argumentos passados na chamada
            tipos_passados = self.params()

            self.consome(TOKEN.fechaParenteses)

            # Validação Semântica 2: Número de argumentos bate?
            if len(params_esperados) != len(tipos_passados):
                raise Exception(
                    f"Erro Semântico: Função '{nome}' esperava {len(params_esperados)} argumentos, mas recebeu {len(tipos_passados)}. Linha: {linha}, Coluna: {coluna}")

            # Validação Semântica 3: Tipos dos argumentos batem?
            for i in range(len(params_esperados)):
                tipo_esperado = params_esperados[i]  # (TIPO, VETOR)
                tipo_passado = tipos_passados[i]  # (TIPO, VETOR)

                # Compara o TIPO (ex: int, float)
                self.semantico.verifica_tipo(tipo_esperado[0], tipo_passado[0])

                # Compara se é VETOR (ex: int[] vs int)
                if tipo_esperado[1] != tipo_passado[1]:
                    raise Exception(
                        f"Erro Semântico: Argumento {i + 1} de '{nome}': esperado {'vetor' if tipo_esperado[1] else 'não-vetor'}, mas recebeu {'vetor' if tipo_passado[1] else 'não-vetor'}. Linha: {linha}, Coluna: {coluna}")

            # Resultado: O tipo de retorno da função
            return tipo_retorno[0], tipo_retorno[1], False
        else:
            # CASO: LAMBDA (uso de variável simples, 'a', ou passagem de vetor 'v')

            # Validação Semântica: Não pode ser uma função (função *precisa* ser chamada)
            if isinstance(tipo, list):
                raise Exception(
                    f"Erro Semântico: '{nome}' é uma função e deve ser chamada com (). Linha: {linha}, Coluna: {coluna}")

            # Resultado: O tipo da própria variável (seja int ou int[])
            return tipo[0], tipo[1], True
    def params(self):
        # Params -> Expr RestoParams | LAMBDA
        # Retorna uma lista de tuplas de tipo: [(TIPO, VET), (TIPO, VET), ...]

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        # Conjunto FIRST(Expr)
        primeiros_expr = {
            TOKEN.ident, TOKEN.abreParenteses,
            TOKEN.valorInt, TOKEN.valorFloat, TOKEN.valorChar, TOKEN.valorString,
            TOKEN.mais, TOKEN.menos, TOKEN.NOT
        }

        lista_tipos = []

        if token in primeiros_expr:
            tipo_expr = self.expr()
            lista_tipos.append(tipo_expr)
            self.restoParams(lista_tipos)

        # Caso LAMBDA (função sem argumentos, ex: func())
        return lista_tipos

    def restoParams(self, lista_tipos):
        # RestoParams -> , Expr RestoParams | LAMBDA
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            tipo_expr = self.expr()
            lista_tipos.append(tipo_expr)
            self.restoParams(lista_tipos)

        # Caso LAMBDA (fim da lista de argumentos)
        return


#todo: Passo 4: Validar atribuições (tipo, leftValue)