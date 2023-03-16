grammar ExprParser;

prog : exp (SEP exp)* ;

sta : exp | asi ;
asi : ID ASI exp # asignacion
    | ID INC exp # incremento
    | ID RED exp # reduccion;
exp : exp MAS ter | exp MEN ter | ter ;
ter : ter POR fac | ter DIV fac | fac ;
fac : GRP_1 exp GRP_2 | NUM | ID | const ;

const : PI ;

PI : 'pi' ;

INC : '+=' ;
RED : '-=' ;
ASI : '=' ;

MAS : '+' ;
MEN : '-' ;
POR : '*' ;
DIV : '/' ;

GRP_1 : '(' ;
GRP_2 : ')' ;

SEP : ';' ;

NUM : [0-9]+ ('.' [0-9]+)? ;
ID : [A-Za-z_] [A-Za-z0-9_]* ;