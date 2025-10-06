import tokens
import Lexico

class sintatico:
    def __init__(self, lexico):
        self.lexico = lexico
        self.lexico.tokenLido = self.lexico.getToken()

    def consome(self, tokenAtual):
        (token, lexema, linha, coluna) = self.lexico.tokenLido
        if tokenAtual == token:
            self.lexico.tokenLido = self.lexico.getToken()
        else:
            msgTokenLido = tokens.TOKEN.msg(token)
            msgTokenAtual = tokens.TOKEN.msg(tokenAtual)
            if token == tokens.TOKEN.erro:
                msg = lexema
            else:
                msg = msgTokenLido

            print(f'Erro Sintático na linha {linha}, coluna {coluna}:')
            print(f'Era esperado {msgTokenAtual} mas veio {msg}')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")


    def program(self):
        # Program -> Function Program | LAMBDA
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        identificadores = {
            tokens.TOKEN.INT,
            tokens.TOKEN.FLOAT,
            tokens.TOKEN.CHAR,
        }

        if token in identificadores:
            self.function()
            self.program()
        elif token == tokens.TOKEN.fimarquivo:
            # FOLLOW(Program) = { fimarquivo } - Trata LAMBDA
            self.consome(tokens.TOKEN.fimarquivo)
        elif token == tokens.TOKEN.fimarquivo:
            return

    def function(self):
        # Function -> Type ident ( ArgList ) CompoundStmt
        self.type()
        self.consome(tokens.TOKEN.ident)
        self.consome(tokens.TOKEN.abreParenteses)
        self.argList()
        self.consome(tokens.TOKEN.fechaParenteses)
        self.compoundStmt()

    def argList(self):
        # ArgList -> Arg RestoArgList | LAMBDA

        primeiros_arg = {
            tokens.TOKEN.INT,
            tokens.TOKEN.FLOAT,
            tokens.TOKEN.CHAR,
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token in primeiros_arg:
            self.arg()
            self.restoArgList()
        elif token == tokens.TOKEN.fechaParenteses:
            return
        else:
            print(
                f'Erro em argList: esperado tipo (int, float, char) ou fechaParenteses, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def restoArgList(self):
        # RestoArgList -> , Arg RestoArgList | LAMBDA

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.virgula:
            self.consome(tokens.TOKEN.virgula)
            self.arg()
            self.restoArgList()
        elif token == tokens.TOKEN.fechaParenteses:
            # LAMBDA
            return
        else:
            print(f'Erro em restoArgList: esperado vírgula ou fechaParenteses, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def arg(self):
        # Arg -> Type IdentArg
        self.type()
        self.identArg()

    def identArg(self):
        # IdentArg -> ident OpcIdentArg
        self.consome(tokens.TOKEN.ident)
        self.opcIdentArg()

    def opcIdentArg(self):
        # OpcIdentArg -> [ ] | LAMBDA
        # FOLLOW(OpcIdentArg) = { ',' , ')' }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.abreColchetes:
            self.consome(tokens.TOKEN.abreColchetes)
            self.consome(tokens.TOKEN.fechaColchetes)
        # LAMBDA
        elif token in {tokens.TOKEN.virgula, tokens.TOKEN.fechaParenteses}:
            return
        else:
            print(
                f'Erro em opcIdentArg: esperado abreColchete, vírgula ou fechaParenteses, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def compoundStmt(self):
        # CompoundStmt -> { StmtList }
        self.consome(tokens.TOKEN.abreChaves)
        self.stmtList()
        self.consome(tokens.TOKEN.fechaChaves)

    def stmtList(self):
        # StmtList -> Stmt StmtList | LAMBDA
        # FIRST(Stmt) = { for, while, if, {, break, continue, return, int, float, char, ident, (, valorInt, valorFloat, valorChar, valorString, ;, +, -, NOT }
        # FOLLOW(StmtList) = { '}' }

        primeiros_stmt = {
            tokens.TOKEN.FOR, tokens.TOKEN.WHILE, tokens.TOKEN.IF, tokens.TOKEN.abreChaves,
            tokens.TOKEN.BREAK, tokens.TOKEN.CONTINUE, tokens.TOKEN.RETURN,
            tokens.TOKEN.INT, tokens.TOKEN.FLOAT, tokens.TOKEN.CHAR,  # Começam com Declaration
            tokens.TOKEN.ident, tokens.TOKEN.abreParenteses,  # Começam com Expr
            tokens.TOKEN.valorInt, tokens.TOKEN.valorFloat, tokens.TOKEN.valorChar, tokens.TOKEN.valorString,
            # Começam com Expr
            tokens.TOKEN.pontoVirgula,  # Stmt -> ;
            tokens.TOKEN.mais, tokens.TOKEN.menos, tokens.TOKEN.NOT  # Começam com Expr
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token in primeiros_stmt:
            self.stmt()
            self.stmtList()
        elif token == tokens.TOKEN.fechaChaves:
            # LAMBDA
            return
        else:
            print(
                f'Erro em stmtList: esperado token inicial de um comando ou fechaChaves, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def stmt(self):
        # Stmt -> ForStmt | WhileStmt | IfStmt | CompoundStmt | break ; | continue ; | return Expr ; | Expr ; | Declaration | ;

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.FOR:
            self.forStmt()
        elif token == tokens.TOKEN.WHILE:
            self.whileStmt()
        elif token == tokens.TOKEN.IF:
            self.ifStmt()
        elif token == tokens.TOKEN.abreChaves:
            self.compoundStmt()
        elif token == tokens.TOKEN.BREAK:
            self.consome(tokens.TOKEN.BREAK)
            self.consome(tokens.TOKEN.pontoVirgula)
        elif token == tokens.TOKEN.CONTINUE:
            self.consome(tokens.TOKEN.CONTINUE)
            self.consome(tokens.TOKEN.pontoVirgula)
        elif token == tokens.TOKEN.RETURN:
            self.consome(tokens.TOKEN.RETURN)
            self.expr()
            self.consome(tokens.TOKEN.pontoVirgula)
        elif token in {tokens.TOKEN.INT, tokens.TOKEN.FLOAT, tokens.TOKEN.CHAR}:
            self.declaration()
        elif token == tokens.TOKEN.pontoVirgula:
            self.consome(tokens.TOKEN.pontoVirgula)
        # O restante (ident, (, valorInt, valorFloat, valorChar, valorString, +, -, NOT) começa com Expr
        elif token in {
            tokens.TOKEN.ident, tokens.TOKEN.abreParenteses,
            tokens.TOKEN.valorInt, tokens.TOKEN.valorFloat, tokens.TOKEN.valorChar, tokens.TOKEN.valorString,
            tokens.TOKEN.mais, tokens.TOKEN.menos, tokens.TOKEN.NOT
        }:
            self.expr()
            self.consome(tokens.TOKEN.pontoVirgula)
        else:
            print(f'Erro em stmt: comando inesperado: {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    # --- Comandos (Statements) ---

    def forStmt(self):
        # ForStmt -> for ( Expr ; OptExpr ; OptExpr ) Stmt
        self.consome(tokens.TOKEN.FOR)
        self.consome(tokens.TOKEN.abreParenteses)
        self.expr()
        self.consome(tokens.TOKEN.pontoVirgula)
        self.optExpr()
        self.consome(tokens.TOKEN.pontoVirgula)
        self.optExpr()
        self.consome(tokens.TOKEN.fechaParenteses)
        self.stmt()

    def optExpr(self):
        # OptExpr -> Expr | LAMBDA
        # FIRST(Expr) = { ident, (, valorInt, valorFloat, valorChar, valorString, +, -, NOT }
        # FOLLOW(OptExpr) = { ';', ')' }

        primeiros_expr = {
            tokens.TOKEN.ident, tokens.TOKEN.abreParenteses,
            tokens.TOKEN.valorInt, tokens.TOKEN.valorFloat, tokens.TOKEN.valorChar, tokens.TOKEN.valorString,
            tokens.TOKEN.mais, tokens.TOKEN.menos, tokens.TOKEN.NOT
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token in primeiros_expr:
            self.expr()
        elif token in {tokens.TOKEN.pontoVirgula, tokens.TOKEN.fechaParenteses}:
            # LAMBDA
            return
        else:
            print(
                f'Erro em optExpr: esperado início de expressão, pontoVirgula ou fechaParenteses, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def whileStmt(self):
        # WhileStmt -> while ( Expr ) Stmt
        self.consome(tokens.TOKEN.WHILE)
        self.consome(tokens.TOKEN.abreParenteses)
        self.expr()
        self.consome(tokens.TOKEN.fechaParenteses)
        self.stmt()

    def ifStmt(self):
        # IfStmt -> if ( Expr ) Stmt ElsePart
        self.consome(tokens.TOKEN.IF)
        self.consome(tokens.TOKEN.abreParenteses)
        self.expr()
        self.consome(tokens.TOKEN.fechaParenteses)
        self.stmt()
        self.elsePart()

    def elsePart(self):
        # ElsePart -> else Stmt | LAMBDA
        # FOLLOW(ElsePart) = FOLLOW(Stmt) - complexo, mas inclui { for, while, if, {, break, continue, return, int, float, char, ident, (, valorInt, valorFloat, valorChar, valorString, ;, +, -, NOT, } }

        primeiros_follow_stmt = {  # Um subconjunto do FOLLOW(Stmt) + FOLLOW(StmtList)
            tokens.TOKEN.FOR, tokens.TOKEN.WHILE, tokens.TOKEN.IF, tokens.TOKEN.abreChaves,
            tokens.TOKEN.BREAK, tokens.TOKEN.CONTINUE, tokens.TOKEN.RETURN,
            tokens.TOKEN.INT, tokens.TOKEN.FLOAT, tokens.TOKEN.CHAR,
            tokens.TOKEN.ident, tokens.TOKEN.abreParenteses,
            tokens.TOKEN.valorInt, tokens.TOKEN.valorFloat, tokens.TOKEN.valorChar, tokens.TOKEN.valorString,
            tokens.TOKEN.pontoVirgula, tokens.TOKEN.fechaChaves,
            tokens.TOKEN.mais, tokens.TOKEN.menos, tokens.TOKEN.NOT, tokens.TOKEN.fimarquivo
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.ELSE:
            self.consome(tokens.TOKEN.ELSE)
            self.stmt()
        elif token in primeiros_follow_stmt:
            # LAMBDA
            return
        else:
            print(
                f'Erro em elsePart: esperado else ou token inicial de um novo comando, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    # --- Declaração ---

    def declaration(self):
        # Declaration -> Type IdentList ;
        self.type()
        self.identList()
        self.consome(tokens.TOKEN.pontoVirgula)

    def type(self):
        # Type -> int | float | char
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.INT:
            self.consome(tokens.TOKEN.INT)
        elif token == tokens.TOKEN.FLOAT:
            self.consome(tokens.TOKEN.FLOAT)
        elif token == tokens.TOKEN.CHAR:
            self.consome(tokens.TOKEN.CHAR)
        else:
            print(f'Erro em type: esperado int, float ou char, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def identList(self):
        # IdentList -> IdentDeclar RestoIdentList
        self.identDeclar()
        self.restoIdentList()

    def restoIdentList(self):
        # RestoIdentList -> , IdentDeclar RestoIdentList | LAMBDA
        # FOLLOW(RestoIdentList) = { ';' }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.virgula:
            self.consome(tokens.TOKEN.virgula)
            self.identDeclar()
            self.restoIdentList()
        elif token == tokens.TOKEN.pontoVirgula:
            # LAMBDA
            return
        else:
            print(f'Erro em restoIdentList: esperado vírgula ou pontoVirgula, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def identDeclar(self):
        # IdentDeclar -> ident OpcIdentDeclar
        self.consome(tokens.TOKEN.ident)
        self.opcIdentDeclar()

    def opcIdentDeclar(self):
        # OpcIdentDeclar -> [ valorInt ] | LAMBDA
        # FOLLOW(OpcIdentDeclar) = { ',', ';' }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.abreColchetes:
            self.consome(tokens.TOKEN.abreColchetes)
            self.consome(tokens.TOKEN.valorInt)
            self.consome(tokens.TOKEN.fechaColchetes)
        elif token in {tokens.TOKEN.virgula, tokens.TOKEN.pontoVirgula}:
            # LAMBDA
            return
        else:
            print(
                f'Erro em opcIdentDeclar: esperado abreColchetes, vírgula ou pontoVirgula, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def expr(self):
        # Expr -> Log RestoExpr
        self.log()
        self.restoExpr()

    def restoExpr(self):
        # RestoExpr -> = Expr RestoExpr | LAMBDA
        # FOLLOW(RestoExpr) = { ';', ')', ',', ']', ... } - depende do contexto

        primeiros_follow_expr = {  # Um subconjunto razoável de FOLLOW(Expr)
            tokens.TOKEN.pontoVirgula, tokens.TOKEN.fechaParenteses,
            tokens.TOKEN.virgula, tokens.TOKEN.fechaColchetes
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.atrib:
            self.consome(tokens.TOKEN.atrib)
            self.expr()
            self.restoExpr()
        elif token in primeiros_follow_expr:
            # LAMBDA
            return
        else:
            print(
                f'Erro em restoExpr: esperado igual ou token de fim de expressão, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def log(self):
        # Log -> Nao RestoLog
        self.nao()
        self.restoLog()

    def restoLog(self):
        # RestoLog -> AND Nao RestoLog | OR Nao RestoLog | LAMBDA
        # FOLLOW(RestoLog) = FOLLOW(Expr) - inclui { '=', ';', ')', ',', ']', ... }

        primeiros_follow_log = {  # Um subconjunto razoável de FOLLOW(Log)
            tokens.TOKEN.atrib, tokens.TOKEN.pontoVirgula, tokens.TOKEN.fechaParenteses,
            tokens.TOKEN.virgula, tokens.TOKEN.fechaColchetes
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.AND:
            self.consome(tokens.TOKEN.AND)
            self.nao()
            self.restoLog()
        elif token == tokens.TOKEN.OR:
            self.consome(tokens.TOKEN.OR)
            self.nao()
            self.restoLog()
        elif token in primeiros_follow_log:
            # LAMBDA
            return
        else:
            print(
                f'Erro em restoLog: esperado AND, OR, igual ou token de fim de expressão, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def nao(self):
        # Nao -> NOT Nao | Rel
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.NOT:
            self.consome(tokens.TOKEN.NOT)
            self.nao()
        else:
            self.rel()

    def rel(self):
        # Rel -> Soma RestoRel
        self.soma()
        self.restoRel()

    def restoRel(self):
        # RestoRel -> opRel Soma | LAMBDA
        # opRel agora é um único token.
        # FOLLOW(RestoRel) = FOLLOW(Nao) - inclui { AND, OR, '=', ';', ')', ',', ']', ... }

        primeiros_follow_rel = { # Um subconjunto razoável de FOLLOW(Rel)
            tokens.TOKEN.AND, tokens.TOKEN.OR, tokens.TOKEN.atrib,
            tokens.TOKEN.pontoVirgula, tokens.TOKEN.fechaParenteses,
            tokens.TOKEN.virgula, tokens.TOKEN.fechaColchetes
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        # --- ALTERAÇÃO AQUI ---
        if token == tokens.TOKEN.opRel:
            self.consome(tokens.TOKEN.opRel) # Consome o único token opRel
            self.soma()
        # --- FIM DA ALTERAÇÃO ---

        elif token in primeiros_follow_rel:
            # LAMBDA
            return
        else:
            print(f'Erro em restoRel: esperado operador relacional ({tokens.TOKEN.msg(tokens.TOKEN.opRel)}) ou token de fim de expressão, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")


    def soma(self):
        # Soma -> Mult RestoSoma
        self.mult()
        self.restoSoma()

    def restoSoma(self):
        # RestoSoma -> + Mult RestoSoma | - Mult RestoSoma | LAMBDA
        # FOLLOW(RestoSoma) = FOLLOW(Rel)

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.mais:
            self.consome(tokens.TOKEN.mais)
            self.mult()
            self.restoSoma()

        elif token == tokens.TOKEN.menos:
            self.consome(tokens.TOKEN.menos)
            self.mult()
            self.restoSoma()

        # FOLLOW(RestoSoma) = { opRel, AND, OR, '=', ';', ')', ',', ']', ... }
        elif token in {
            tokens.TOKEN.opRel,  # <--- ALTERAÇÃO: Checa o token único opRel
            tokens.TOKEN.AND, tokens.TOKEN.OR, tokens.TOKEN.atrib,
            tokens.TOKEN.pontoVirgula, tokens.TOKEN.fechaParenteses,
            tokens.TOKEN.virgula, tokens.TOKEN.fechaColchetes
        }:
            # LAMBDA: não faz nada
            return

        else:
            print(
                f'Erro em restoSoma: esperado + , - , opRel ou token de fim de expressão, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def mult(self):
        # Mult -> Uno RestoMult
        self.uno()
        self.restoMult()

    def restoMult(self):
        # RestoMult -> * Uno RestoMult | / Uno RestoMult | % Uno RestoMult | LAMBDA
        # FOLLOW(RestoMult) = FOLLOW(Soma)

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.multiplicacao:
            self.consome(tokens.TOKEN.multiplicacao)
            self.uno()
            self.restoMult()

        elif token == tokens.TOKEN.divisao:
            self.consome(tokens.TOKEN.divisao)
            self.uno()
            self.restoMult()

        elif token == tokens.TOKEN.porcentagem:
            self.consome(tokens.TOKEN.porcentagem)
            self.uno()
            self.restoMult()

        # FOLLOW(RestoMult) = { +, -, opRel, AND, OR, '=', ';', ')', ',', ']', ... }
        # --- ALTERAÇÃO: Incluído opRel no conjunto FOLLOW para LAMBDA ---
        elif token in {
            tokens.TOKEN.mais, tokens.TOKEN.menos,
            tokens.TOKEN.opRel,  # <--- ALTERADO: Checa o token único opRel
            tokens.TOKEN.AND, tokens.TOKEN.OR, tokens.TOKEN.atrib,
            tokens.TOKEN.pontoVirgula, tokens.TOKEN.fechaParenteses,
            tokens.TOKEN.virgula, tokens.TOKEN.fechaColchetes
        }:
            # LAMBDA: não faz nada
            return
        # --- FIM DA ALTERAÇÃO ---

        else:
            print(
                f'Erro em restoMult: esperado *, /, %, operador aditivo, relacional ou token de fim de expressão, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def uno(self):
        # Uno -> + Uno | - Uno | Folha
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.mais:
            self.consome(tokens.TOKEN.mais)
            self.uno()
        elif token == tokens.TOKEN.menos:
            self.consome(tokens.TOKEN.menos)
            self.uno()
        else:
            self.folha()

    def folha(self):
        # Folha -> ( Expr ) | Identifier | valorInt | valorFloat | valorChar | valorString
        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.abreParenteses:
            self.consome(tokens.TOKEN.abreParenteses)
            self.expr()
            self.consome(tokens.TOKEN.fechaParenteses)
        elif token == tokens.TOKEN.ident:
            self.identifier()
        elif token == tokens.TOKEN.valorInt:
            self.consome(tokens.TOKEN.valorInt)
        elif token == tokens.TOKEN.valorFloat:
            self.consome(tokens.TOKEN.valorFloat)
        elif token == tokens.TOKEN.valorChar:
            self.consome(tokens.TOKEN.valorChar)
        elif token == tokens.TOKEN.valorString:
            self.consome(tokens.TOKEN.valorString)
        else:
            print(
                f'Erro em folha: esperado (, ident, valorInt, valorFloat, valorChar, valorString, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def identifier(self):
        # Identifier -> ident OpcIdentifier
        self.consome(tokens.TOKEN.ident)
        self.opcIdentifier()

    def opcIdentifier(self):
        # OpcIdentifier -> [ Expr ] | ( Params ) | LAMBDA
        # FOLLOW(OpcIdentifier) = FOLLOW(Folha)

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.abreColchetes:
            self.consome(tokens.TOKEN.abreColchetes)
            self.expr()
            self.consome(tokens.TOKEN.fechaColchetes)
        elif token == tokens.TOKEN.abreParenteses:
            self.consome(tokens.TOKEN.abreParenteses)
            self.params()
            self.consome(tokens.TOKEN.fechaParenteses)
        # LAMBDA
        # FOLLOW(OpcIdentifier) = { *, /, %, +, -, opRel, AND, OR, '=', ';', ')', ',', ']', ... }
        # --- ALTERAÇÃO: Incluído opRel no conjunto FOLLOW para LAMBDA ---
        elif token in {
            tokens.TOKEN.multiplicacao, tokens.TOKEN.divisao, tokens.TOKEN.porcentagem,
            tokens.TOKEN.mais, tokens.TOKEN.menos,
            tokens.TOKEN.opRel,  # <--- ALTERADO: Checa o token único opRel
            tokens.TOKEN.AND, tokens.TOKEN.OR, tokens.TOKEN.atrib,
            tokens.TOKEN.pontoVirgula, tokens.TOKEN.fechaParenteses,
            tokens.TOKEN.virgula, tokens.TOKEN.fechaColchetes
        }:
            return
        # --- FIM DA ALTERAÇÃO ---
        else:
            print(
                f'Erro em opcIdentifier: esperado [, (, ou token de operador/fim de expressão, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def params(self):
        # Params -> Expr RestoParams | LAMBDA
        # FIRST(Expr) = { ident, (, valorInt, valorFloat, valorChar, valorString, +, -, NOT }
        # FOLLOW(Params) = { ')' }

        primeiros_expr = {
            tokens.TOKEN.ident, tokens.TOKEN.abreParenteses,
            tokens.TOKEN.valorInt, tokens.TOKEN.valorFloat, tokens.TOKEN.valorChar, tokens.TOKEN.valorString,
            tokens.TOKEN.mais, tokens.TOKEN.menos, tokens.TOKEN.NOT
        }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token in primeiros_expr:
            self.expr()
            self.restoParams()
        elif token == tokens.TOKEN.fechaParenteses:
            # LAMBDA
            return
        else:
            print(
                f'Erro em params: esperado início de expressão ou fechaParenteses, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")

    def restoParams(self):
        # RestoParams -> , Expr RestoParams | LAMBDA
        # FOLLOW(RestoParams) = { ')' }

        (token, lexema, linha, coluna) = self.lexico.tokenLido

        if token == tokens.TOKEN.virgula:
            self.consome(tokens.TOKEN.virgula)
            self.expr()
            self.restoParams()
        elif token == tokens.TOKEN.fechaParenteses:
            # LAMBDA
            return
        else:
            print(f'Erro em restoParams: esperado vírgula ou fechaParenteses, mas veio {tokens.TOKEN.msg(token)}.')
            raise Exception(f"Erro Sintático na linha {linha} col {coluna}")


if __name__ == '__main__':
    with open("example.c", "r") as arqFonte:
        lexico = Lexico.lexico(arqFonte)
        analisador_sintatico = sintatico(lexico)
        print("Iniciando a análise sintática...")
        analisador_sintatico.program()
        print("\nAnálise sintática concluída com SUCESSO! O código é válido de acordo com a gramática.")
