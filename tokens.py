from enum import IntEnum

class TOKEN(IntEnum):
    fimarquivo = 0
    erro = 1

    # Palavras-chave
    INT = 2
    FLOAT = 3
    CHAR = 4
    FOR = 5
    WHILE = 6
    IF = 7
    ELSE = 8
    BREAK = 9
    CONTINUE = 10
    RETURN = 11

    abreParenteses = 12
    fechaParenteses = 13
    abreChaves = 14
    fechaChaves = 15
    abreColchetes = 16
    fechaColchetes = 17

    pontoFinal = 18
    pontoVirgula = 19
    virgula = 20

    atrib = 21
    opRel = 22

    AND = 23
    OR = 24
    NOT = 25

    mais = 26
    menos = 27
    multiplicacao = 28
    divisao = 29
    porcentagem = 30

    ident = 31
    valorInt = 32
    valorFloat = 33
    valorChar = 34
    valorString = 35
    quebraLinha = 36

    @classmethod
    def msg(cls, token):
        nomes = {
            0: '<eof>',
            1: 'erro',

            2: 'int',
            3: 'float',
            4: 'char',
            5: 'for',
            6: 'while',
            7: 'if',
            8: 'else',
            9: 'break',
            10: 'continue',
            11: 'return',

            12: '(',
            13: ')',
            14: '{',
            15: '}',
            16: '[',
            17: ']',

            18: '.',
            19: ';',
            20: ',',

            21: 'atrib',
            22: 'opRel',

            23: 'AND',
            24: 'OR',
            25: 'NOT',

            26: '+',
            27: '-',
            28: '*',
            29: '/',
            30: '%',

            31: 'ident',
            32: 'valorInt',
            33: 'valorFloat',
            34: 'valorChar',
            35: 'valorString',
            36: '\\n'
        }
        return nomes[token]

    @classmethod
    def reservada(cls, lexema):
        reservadas = {
            'int': TOKEN.INT,
            'float': TOKEN.FLOAT,
            'char': TOKEN.CHAR,
            'for': TOKEN.FOR,
            'while': TOKEN.WHILE,
            'if': TOKEN.IF,
            'else': TOKEN.ELSE,
            'break': TOKEN.BREAK,
            'continue': TOKEN.CONTINUE,
            'return': TOKEN.RETURN,
        }
        return reservadas.get(lexema, TOKEN.ident)

    @classmethod
    def tabelaOperacoes(cls):
        return {
            # OPERAÇÕES ARITMÉTICAS (int/int)
            frozenset({(TOKEN.valorInt, False), TOKEN.mais, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),
            frozenset({(TOKEN.valorInt, False), TOKEN.menos, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),
            frozenset({(TOKEN.valorInt, False), TOKEN.multiplicacao, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),
            # Nota: Em Mini-C (como em C), int / int -> int (divisão truncada)
            frozenset({(TOKEN.valorInt, False), TOKEN.divisao, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),
            frozenset({(TOKEN.valorInt, False), TOKEN.porcentagem, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),

            # OPERAÇÕES ARITMÉTICAS (float/float)
            frozenset({(TOKEN.valorFloat, False), TOKEN.mais, (TOKEN.valorFloat, False)}): (TOKEN.valorFloat, False),
            frozenset({(TOKEN.valorFloat, False), TOKEN.menos, (TOKEN.valorFloat, False)}): (TOKEN.valorFloat, False),
            frozenset({(TOKEN.valorFloat, False), TOKEN.multiplicacao, (TOKEN.valorFloat, False)}): (TOKEN.valorFloat, False),
            frozenset({(TOKEN.valorFloat, False), TOKEN.divisao, (TOKEN.valorFloat, False)}): (TOKEN.valorFloat, False),

            # OPERAÇÕES ARITMÉTICAS (float/int e int/float)
            frozenset({(TOKEN.valorFloat, False), TOKEN.mais, (TOKEN.valorInt, False)}): (TOKEN.valorFloat, False),
            frozenset({(TOKEN.valorFloat, False), TOKEN.menos, (TOKEN.valorInt, False)}): (TOKEN.valorFloat, False),
            frozenset({(TOKEN.valorFloat, False), TOKEN.multiplicacao, (TOKEN.valorInt, False)}): (TOKEN.valorFloat, False),
            frozenset({(TOKEN.valorFloat, False), TOKEN.divisao, (TOKEN.valorInt, False)}): (TOKEN.valorFloat, False),

            frozenset({(TOKEN.valorInt, False), TOKEN.mais, (TOKEN.valorFloat, False)}): (TOKEN.valorFloat, False),
            frozenset({(TOKEN.valorInt, False), TOKEN.menos, (TOKEN.valorFloat, False)}): (TOKEN.valorFloat, False),
            frozenset({(TOKEN.valorInt, False), TOKEN.multiplicacao, (TOKEN.valorFloat, False)}): (TOKEN.valorFloat, False),
            frozenset({(TOKEN.valorInt, False), TOKEN.divisao, (TOKEN.valorFloat, False)}): (TOKEN.valorFloat, False),

            # OPERAÇÕES RELACIONAIS (retornam int)
            frozenset({(TOKEN.valorInt, False), TOKEN.opRel, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),
            frozenset({(TOKEN.valorFloat, False), TOKEN.opRel, (TOKEN.valorFloat, False)}): (TOKEN.valorInt, False),
            frozenset({(TOKEN.valorInt, False), TOKEN.opRel, (TOKEN.valorFloat, False)}): (TOKEN.valorInt, False),
            frozenset({(TOKEN.valorFloat, False), TOKEN.opRel, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),

            # OPERAÇÕES LÓGICAS (operam sobre int, retornam int)
            frozenset({(TOKEN.valorInt, False), TOKEN.AND, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),
            frozenset({(TOKEN.valorInt, False), TOKEN.OR, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),
            frozenset({TOKEN.NOT, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),

            # OPERAÇÕES UNÁRIAS (+a, -a)
            frozenset({TOKEN.mais, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),
            frozenset({TOKEN.menos, (TOKEN.valorInt, False)}): (TOKEN.valorInt, False),
            frozenset({TOKEN.mais, (TOKEN.valorFloat, False)}): (TOKEN.valorFloat, False),
            frozenset({TOKEN.menos, (TOKEN.valorFloat, False)}): (TOKEN.valorFloat, False)
        }