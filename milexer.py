from dataclasses import dataclass
from pprint import pformat

@dataclass
class Token:
    nombre: str
    valor: str
    literal: str
    linea: int

# TODO: clase Error: ...

class MiLexer:
    def __init__(self, input: str):
        self.input = input
        self.inicio = 0
        self.actual = 0
        self.linea = 1

        self.tokens: list[Token] = []
        self.errores: list[str] = []

    def avanzar(self):
        c = self.input[self.actual]
        self.actual += 1
        return c
    
    def mirar(self):
        try:
            return self.input[self.actual]
        except IndexError:
            return ''

    def mirar_otro(self):
        try:
            return self.input[self.actual + 1]
        except IndexError:
            return ''
    
    def ignorar(self):
        self.inicio = self.actual

    def agregar_token(self, nombre:str):
        self.tokens.append(Token(nombre,
                                 self.input[self.inicio : self.actual],
                                 self.input[self.inicio : self.actual], 
                                 self.linea))
        self.inicio = self.actual
    
    def eof(self):
        return self.actual >= len(self.input)
    
    def escanear(self):
        while not self.eof():
            self.est_root()

        return self.tokens, self.errores

    def est_root(self):
        c = self.avanzar()

        if c == '=':
            self.agregar_token('ASI')
        elif c == '*': 
            self.agregar_token('POR')
        elif c == '/': 
            self.agregar_token('DIV')
        elif c == '(': 
            self.agregar_token('GRP_1')
        elif c == ')': 
            self.agregar_token('GRP_2')
        elif c == ';': 
            self.agregar_token('SEP')
        elif c == '-':
            self.est_men()
        elif c == '+':
            self.est_mas()

        elif c.isalpha() or c == '_':
            self.est_id()
        elif c.isnumeric():
            self.est_num()

        elif c in [' ','\t']:
            self.ignorar()
        elif c == '\n':
            self.ignorar()
            self.linea += 1

        else:
            self.ignorar()
            self.errores.append(f"No se reconoce el símbolo {c} en la línea {self.linea}")

    def est_id(self):
        while (self.mirar().isalnum() or self.mirar() == '_') and not self.eof():
            self.avanzar()

        # TODO: si es 'pi' crear un KW en lugar de un ID
        self.agregar_token('ID')

    def est_num(self):
        while self.mirar().isnumeric() and not self.eof():
            self.avanzar()
        
        if self.mirar() == '.' and self.mirar_otro().isnumeric():
            self.avanzar()
            while self.mirar().isnumeric() and not self.eof():
                self.avanzar()

        self.agregar_token('NUM')


    def est_men(self):
        if self.mirar() == '=':
            self.avanzar()
            self.agregar_token('RED')
        else:
            self.agregar_token('MEN')
        
    def est_mas(self):
        if self.mirar() == '=':
            self.avanzar()
            self.agregar_token('INC')
        else:
            self.agregar_token('MAS')

if __name__ == '__main__':
    lexer = MiLexer("(&&&&&7*4)/\n55.+=a&mauris")
    tokens, errores = lexer.escanear()

    print(f"Tokens: \n{pformat(tokens)}")
    print(f"Errores: \n{pformat(errores)}")

# PI : 'pi' ;

# INC : '+=' ;
# RED : '-=' ;
# ASI : '=' ;

# MAS : '+' ;
# MEN : '-' ;
# POR : '*' ;
# DIV : '/' ;

# GRP_1 : '(' ;
# GRP_2 : ')' ;

# SEP : ';' ;

# NUM : [0-9]+ ('.' [0-9]+)? ;
# ID : [A-Za-z_] [A-Za-z0-9_]* ;
