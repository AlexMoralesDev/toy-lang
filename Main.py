import ply.lex as lex
import ply.yacc as yacc


# BEGIN LEXICAL ANALYZER DEFINITION

# List of token names
tokens = (
    'ID',
    'BLOCK',
    'ADD',
    'PRINT',
    'VIEW',
    'RUN',
    'MINE',
    'EXPORT',
    'STR',
    'INT',
    'LONG',
    'FLOAT',
    'LIST',
    'TUPLE',
    'DICT',
    'NUMBER',
    'STRING',
    'ASSIGN',
    'TYPEASSIGN',
    'SEPARATOR',
    'LPAREN',
    'RPAREN',
)

# Keywords dictionary
keywords = {
    "block": "BLOCK",
    "add": "ADD",
    "print": "PRINT",
    "view": "VIEW",
    "run": "RUN",
    "mine": "MINE",
    "export": "EXPORT",
    "str": "STR",
    "int": "INT",
    "long": "LONG",
    "float": "FLOAT",
    "List": "LIST",
    "Tuple": "TUPLE",
    "Dict": "DICT"
}

# Regex for simple tokens
t_ASSIGN = r'='
t_TYPEASSIGN = r':'
t_SEPARATOR = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'

# Function-based tokens
def t_STRING(t):
    r'\"[^\"]*\"'
    t.value = t.value[1:-1]  # Remove quotes
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = keywords.get(t.value, "ID")
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

# Track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignore whitespace
t_ignore = ' \t\r'

# Ignore comments
def t_COMMENT(t):
    r'//[^\n]*'
    pass

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# END LEXICAL ANALYZER DEFINITION

#################################

# BEGIN SYNTAX ANALYSIS DEFINITION

# Grammar rule for start symbol
def p_start(p):
    '''start : block_definition block_operations'''
    print("Recognized: start -> block_definition block_operations")

# Grammar rule for block definition
def p_block_definition(p):
    '''block_definition : BLOCK ID ASSIGN LPAREN attributes RPAREN'''
    print(f"Recognized: block_definition -> BLOCK {p[2]} = ( attributes )")

# Grammar rules for block operations
def p_block_operations_single(p):
    '''block_operations : block_operation'''
    print("Recognized: block_operations -> block_operation")

def p_block_operations_multiple(p):
    '''block_operations : block_operations block_operation'''
    print("Recognized: block_operations -> block_operations block_operation")

# Grammar rules for individual block operations
def p_block_operation_add(p):
    '''block_operation : ADD ID ASSIGN LPAREN new_atts RPAREN'''
    print(f"Recognized: block_operation -> ADD {p[2]} = ( new_atts )")

def p_block_operation_print(p):
    '''block_operation : PRINT ID'''
    print(f"Recognized: block_operation -> PRINT {p[2]}")

def p_block_operation_run(p):
    '''block_operation : RUN ID'''
    print(f"Recognized: block_operation -> RUN {p[2]}")

def p_block_operation_mine(p):
    '''block_operation : MINE ID'''
    print(f"Recognized: block_operation -> MINE {p[2]}")

def p_block_operation_export(p):
    '''block_operation : EXPORT ID'''
    print(f"Recognized: block_operation -> EXPORT {p[2]}")

def p_block_operation_view(p):
    '''block_operation : VIEW ID'''
    print(f"Recognized: block_operation -> VIEW {p[2]}")

# Grammar rules for type
def p_type(p):
    '''type : STR
            | INT
            | LONG
            | FLOAT
            | LIST
            | TUPLE
            | DICT'''
    print(f"Recognized: type -> {p[1]}")

# Grammar rule for attribute
def p_attribute(p):
    '''attribute : ID TYPEASSIGN type'''
    print(f"Recognized: attribute -> {p[1]} : type")

# Grammar rules for attributes
def p_attributes_single(p):
    '''attributes : attribute'''
    print("Recognized: attributes -> attribute")

def p_attributes_multiple(p):
    '''attributes : attributes SEPARATOR attribute'''
    print("Recognized: attributes -> attributes , attribute")

# Grammar rules for new_att
def p_new_att_string(p):
    '''new_att : ID TYPEASSIGN STRING'''
    print(f"Recognized: new_att -> {p[1]} : \"{p[3]}\"")

def p_new_att_number(p):
    '''new_att : ID TYPEASSIGN NUMBER'''
    print(f"Recognized: new_att -> {p[1]} : {p[3]}")

# Grammar rules for new_atts
def p_new_atts_single(p):
    '''new_atts : new_att'''
    print("Recognized: new_atts -> new_att")

def p_new_atts_multiple(p):
    '''new_atts : new_atts SEPARATOR new_att'''
    print("Recognized: new_atts -> new_atts , new_att")

# Error handling
def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} ('{p.value}') at line {p.lineno}")
    else:
        print("Syntax error at EOF")

# END SYNTAX ANALYSIS DEFINITION


################
## CALL PARSER
###############

def main():

    # Build the lexer and parser
    lexer = lex.lex()
    parser = yacc.yacc()

    # Read the file
    with open("Program_Test.txt", "r") as f:
        data = f.read()

    # Parse the file
    result = parser.parse(data, lexer=lexer)
    

if __name__ == '__main__':
    main()