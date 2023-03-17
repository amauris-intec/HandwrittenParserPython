from dataclasses import dataclass, field
from pprint import pformat
from typing import Optional

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


class EOFError(Exception):
    pass


@dataclass
class Nodo:
  
    nombre: str
    hijos: list["Nodo"] = field(default_factory=list)
    
    def agregar(self, hijo):
        if hijo:
            self.hijos.append(hijo)

    def __str__(self):
        s = f"[{self.nombre}"
        for hijo in self.hijos:
            s += f" {hijo}"
        s += "]"
        return s


class MiParser:

    def aceptar(self, *alternativas: str) -> Optional[Token]:
        if self.validar(*alternativas):
            return self.avanzar()
 

    def avanzar(self) -> Token:
        if not self.eof():
            token = self.mirar()
            self.actual += 1
            return token
        else:
            raise EOFError()
 

    def validar(self, *alternativas: str) -> bool:
        if self.eof():
            return False
        for alt in alternativas:
            if self.mirar().nombre == alt:
                return True
        return False
 
 
    def eof(self) -> bool:
        try:
            self.tokens[self.actual]
            return False
        except IndexError:
            return True
 
    def mirar(self) -> Token:
        return self.tokens[self.actual]
 
 
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.actual = 0
    
    def prog(self):
        nodo = Nodo("prog")
        exp = self.exp()
        nodo.agregar(exp)
        while sep := self.aceptar("SEP"):
            nodo.agregar(sep.valor)
            exp = self.exp()
            nodo.agregar(exp)
        if not self.eof():
            print("WTF")
        return nodo

    def exp(self):
        # exp : ter exp2 ;
        nodo = Nodo("exp")
        ter = self.ter()
        nodo.agregar(ter)
        exp2 = self.exp2()
        nodo.agregar(exp2)
        return nodo

    def exp2(self):
        # exp2 : (MAS | MEN) ter exp2 | /*E*/ ;
        nodo = Nodo("exp2")
        if op := self.aceptar("MAS", "MEN"):
            nodo.agregar(op.valor)
            ter = self.ter()
            nodo.agregar(ter)
            exp2 = self.exp2()
            nodo.agregar(exp2)
        return nodo
    
    def ter(self):
        # ter : fac ter2;
        nodo = Nodo("ter")
        fac = self.fac()
        nodo.agregar(fac)
        ter2 = self.ter2()
        nodo.agregar(ter2)
        return nodo


    def ter2(self):
        # ter2 : (POR | DIV) fac ter2 | /*E*/ ;
        nodo = Nodo("ter2")
        if op := self.aceptar("POR", "DIV"):
            nodo.agregar(op.valor)
            fac = self.fac()
            nodo.agregar(fac)
            ter2 = self.ter2()
            nodo.agregar(ter2)
        return nodo
    
    def fac(self):
        #fac : GRP_1 exp GRP_2 | NUM ;
        nodo = Nodo("fac")
        if grp_1 := self.aceptar("GRP_1"):
            nodo.agregar(grp_1.valor)
            exp = self.exp()
            nodo.agregar(exp)
            grp_2 = self.aceptar("GRP_2")
            nodo.agregar(grp_2.valor)
        elif num := self.aceptar("NUM"):
            nodo.agregar(num.valor)
        else:
            nodo.agregar(f"```{self.mirar().valor}```")
        return nodo







if __name__ == '__main__':
    lexer = MiLexer('5+6*)2+3)')
    tokens, errores = lexer.escanear()

    print(f"Tokens: \n{pformat(tokens)}")
    print(f"Errores: \n{pformat(errores)}")
    parser = MiParser(tokens)
    tree = parser.prog()

    print(tree)





####### gramatica simplificada:######
# grammar ExprParser;

# prog : exp (SEP exp)* EOF;

# exp : ter exp2 ;
# exp2 : (MAS ter | MEN ter) exp2 | /*E*/ ;

# ter : fac ter2;
# ter2 : (POR fac | DIV fac) ter2 | /*E*/ ;


# fac : GRP_1 exp GRP_2 | NUM ;

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
