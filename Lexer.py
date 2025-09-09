import ply.lex as lex

# List of token names
tokens = (
    'ID',
    'BLOCK',
    'VAR',
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
    'NUM',
    'ASSIGN',
    'TYPEASSIGN',
    'SEPARATOR',
    'LPAREN',
    'RPAREN',
    'NE',
    'LT',
    'GT',
    'LE',
    'GE',
    'PLUS',
    'MINUS',
    'STAR',
    'SLASH'
)

# Keywords dictionary
keywords = {
    "block": "BLOCK",
    "var": "VAR",
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
t_NE = r'!='
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_PLUS = r'\+'
t_MINUS = r'-'
t_STAR = r'\*'
t_SLASH = r'/'

# Function-based tokens
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = keywords.get(t.value, "ID")
    return t

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
# Reset Char count for every new line
def find_column(input_text, token):
    last_newline = input_text.rfind('\n', 0, token.lexpos)
    column = token.lexpos - last_newline - 1
    return column

# Ignore whitespace
t_ignore = ' \t\r'

# Ignore comments
def t_COMMENT(t):
    r'//[^\n]*'
    pass


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# Test
lexer = lex.lex()

with open('Program_Test.txt', 'r') as f:
    data = f.read()

lexer.input(data)

while True:
    tok = lexer.token()
    if not tok:
        break
    column = find_column(data, tok)
    print(f"LexToken({tok.type},'{tok.value}',{tok.lineno},{column})")
