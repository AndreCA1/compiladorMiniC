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
        self.semantico.declaraFuncao(nome_funcao, tipo, argumentos)
        self.compoundStmt()

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
        self.consome(TOKEN.abreChaves)
        self.stmtList()
        self.consome(TOKEN.fechaChaves)

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
        self.type()
        self.identList()
        self.consome(TOKEN.pontoVirgula)

    def type(self):
        # Type -> int | float | char
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.INT:
            self.consome(TOKEN.INT)
            return TOKEN.INT
        elif token == TOKEN.FLOAT:
            self.consome(TOKEN.FLOAT)
            return TOKEN.FLOAT
        elif token == TOKEN.CHAR:
            self.consome(TOKEN.CHAR)
            return TOKEN.CHAR
        else:
            print(f'Erro em type: esperado int, float ou char, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def identList(self):
        # IdentList -> IdentDeclar RestoIdentList
        self.identDeclar()
        self.restoIdentList()

    def restoIdentList(self):
        # RestoIdentList -> , IdentDeclar RestoIdentList | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            self.identDeclar()
            self.restoIdentList()
        elif token == TOKEN.pontoVirgula:
            return
        else:
            print(f'Erro em restoIdentList: esperado vírgula ou pontoVirgula, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def identDeclar(self):
        # IdentDeclar -> ident OpcIdentDeclar
        self.consome(TOKEN.ident)
        self.opcIdentDeclar()

    def opcIdentDeclar(self):
        # OpcIdentDeclar -> [ valorInt ] | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.abreColchetes:
            self.consome(TOKEN.abreColchetes)
            self.consome(TOKEN.valorInt)
            self.consome(TOKEN.fechaColchetes)
        elif token in {TOKEN.virgula, TOKEN.pontoVirgula}:
            return
        else:
            print(
                f'Erro em opcIdentDeclar: esperado abreColchetes, vírgula ou pontoVirgula, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def expr(self):
        # Expr -> Log RestoExpr
        self.log()
        self.restoExpr()

    def restoExpr(self):
        # RestoExpr -> = Expr RestoExpr | LAMBDA

        primeiros_follow_expr = {  # Um subconjunto razoável de FOLLOW(Expr)
            TOKEN.pontoVirgula, TOKEN.fechaParenteses,
            TOKEN.virgula, TOKEN.fechaColchetes
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.atrib:
            self.consome(TOKEN.atrib)
            self.expr()
            self.restoExpr()
        elif token in primeiros_follow_expr:
            return
        else:
            print(
                f'Erro em restoExpr: esperado igual ou token de fim de expressão, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def log(self):
        # Log -> Nao RestoLog
        self.nao()
        self.restoLog()

    def restoLog(self):
        # RestoLog -> AND Nao RestoLog | OR Nao RestoLog | LAMBDA

        primeiros_follow_log = {  # Um subconjunto razoável de FOLLOW(Log)
            TOKEN.atrib, TOKEN.pontoVirgula, TOKEN.fechaParenteses,
            TOKEN.virgula, TOKEN.fechaColchetes
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.AND:
            self.consome(TOKEN.AND)
            self.nao()
            self.restoLog()
        elif token == TOKEN.OR:
            self.consome(TOKEN.OR)
            self.nao()
            self.restoLog()
        elif token in primeiros_follow_log:
            return
        else:
            print(
                f'Erro em restoLog: esperado AND, OR, igual ou token de fim de expressão, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def nao(self):
        # Nao -> NOT Nao | Rel
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            self.nao()
        else:
            self.rel()

    def rel(self):
        # Rel -> Soma RestoRel
        self.soma()
        self.restoRel()

    def restoRel(self):
        # RestoRel -> opRel Soma | LAMBDA

        primeiros_follow_rel = {
            TOKEN.AND, TOKEN.OR, TOKEN.atrib,
            TOKEN.pontoVirgula, TOKEN.fechaParenteses,
            TOKEN.virgula, TOKEN.fechaColchetes
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.opRel:
            self.consome(TOKEN.opRel)
            self.soma()

        elif token in primeiros_follow_rel:
            # LAMBDA
            return
        else:
            print(f'Erro em restoRel: esperado operador relacional ({TOKEN.msg(TOKEN.opRel)}) ou token de fim de expressão, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def soma(self):
        # Soma -> Mult RestoSoma
        self.mult()
        self.restoSoma()

    def restoSoma(self):
        # RestoSoma -> + Mult RestoSoma | - Mult RestoSoma | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.mais:
            self.consome(TOKEN.mais)
            self.mult()
            self.restoSoma()

        elif token == TOKEN.menos:
            self.consome(TOKEN.menos)
            self.mult()
            self.restoSoma()

        elif token in {
            TOKEN.opRel,  # <--- ALTERAÇÃO: Checa o token único opRel
            TOKEN.AND, TOKEN.OR, TOKEN.atrib,
            TOKEN.pontoVirgula, TOKEN.fechaParenteses,
            TOKEN.virgula, TOKEN.fechaColchetes
        }:
            return

        else:
            print(
                f'Erro em restoSoma: esperado + , - , opRel ou token de fim de expressão, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def mult(self):
        # Mult -> Uno RestoMult
        self.uno()
        self.restoMult()

    def restoMult(self):
        # RestoMult -> * Uno RestoMult | / Uno RestoMult | % Uno RestoMult | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.multiplicacao:
            self.consome(TOKEN.multiplicacao)
            self.uno()
            self.restoMult()

        elif token == TOKEN.divisao:
            self.consome(TOKEN.divisao)
            self.uno()
            self.restoMult()

        elif token == TOKEN.porcentagem:
            self.consome(TOKEN.porcentagem)
            self.uno()
            self.restoMult()

        elif token in {
            TOKEN.mais, TOKEN.menos,
            TOKEN.opRel,  # <--- ALTERADO: Checa o token único opRel
            TOKEN.AND, TOKEN.OR, TOKEN.atrib,
            TOKEN.pontoVirgula, TOKEN.fechaParenteses,
            TOKEN.virgula, TOKEN.fechaColchetes
        }:
            # LAMBDA: não faz nada
            return
        # --- FIM DA ALTERAÇÃO ---

        else:
            print(
                f'Erro em restoMult: esperado *, /, %, operador aditivo, relacional ou token de fim de expressão, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def uno(self):
        # Uno -> + Uno | - Uno | Folha
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.mais:
            self.consome(TOKEN.mais)
            self.uno()
        elif token == TOKEN.menos:
            self.consome(TOKEN.menos)
            self.uno()
        else:
            self.folha()

    def folha(self):
        # Folha -> ( Expr ) | Identifier | valorInt | valorFloat | valorChar | valorString
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.abreParenteses:
            self.consome(TOKEN.abreParenteses)
            self.expr()
            self.consome(TOKEN.fechaParenteses)
        elif token == TOKEN.ident:
            self.identifier()
        elif token == TOKEN.valorInt:
            self.consome(TOKEN.valorInt)
        elif token == TOKEN.valorFloat:
            self.consome(TOKEN.valorFloat)
        elif token == TOKEN.valorChar:
            self.consome(TOKEN.valorChar)
        elif token == TOKEN.valorString:
            self.consome(TOKEN.valorString)
        else:
            print(
                f'Erro em folha: esperado (, ident, valorInt, valorFloat, valorChar, valorString, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def identifier(self):
        # Identifier -> ident OpcIdentifier
        self.consome(TOKEN.ident)
        self.opcIdentifier()

    def opcIdentifier(self):
        # OpcIdentifier -> [ Expr ] | ( Params ) | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.abreColchetes:
            self.consome(TOKEN.abreColchetes)
            self.expr()
            self.consome(TOKEN.fechaColchetes)
        elif token == TOKEN.abreParenteses:
            self.consome(TOKEN.abreParenteses)
            self.params()
            self.consome(TOKEN.fechaParenteses)
        elif token in {
            TOKEN.multiplicacao, TOKEN.divisao, TOKEN.porcentagem,
            TOKEN.mais, TOKEN.menos,
            TOKEN.opRel,  # <--- ALTERADO: Checa o token único opRel
            TOKEN.AND, TOKEN.OR, TOKEN.atrib,
            TOKEN.pontoVirgula, TOKEN.fechaParenteses,
            TOKEN.virgula, TOKEN.fechaColchetes
        }:
            return
        # --- FIM DA ALTERAÇÃO ---
        else:
            print(
                f'Erro em opcIdentifier: esperado [, (, ou token de operador/fim de expressão, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def params(self):
        # Params -> Expr RestoParams | LAMBDA

        primeiros_expr = {
            TOKEN.ident, TOKEN.abreParenteses,
            TOKEN.valorInt, TOKEN.valorFloat, TOKEN.valorChar, TOKEN.valorString,
            TOKEN.mais, TOKEN.menos, TOKEN.NOT
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token in primeiros_expr:
            self.expr()
            self.restoParams()
        elif token == TOKEN.fechaParenteses:
            # LAMBDA
            return
        else:
            print(
                f'Erro em params: esperado início de expressão ou fechaParenteses, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')


    def restoParams(self):
        # RestoParams -> , Expr RestoParams | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == TOKEN.virgula:
            self.consome(TOKEN.virgula)
            self.expr()
            self.restoParams()
        elif token == TOKEN.fechaParenteses:
            # LAMBDA
            return
        else:
            print(f'Erro em restoParams: esperado vírgula ou fechaParenteses, mas veio {TOKEN.msg(token)}. Linha: {linha} Coluna: {coluna}')

