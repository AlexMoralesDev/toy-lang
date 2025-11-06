import hashlib
import json
import time

import ply.lex as lex
import ply.yacc as yacc
from flask import Flask, jsonify

# BEGIN LEXICAL ANALYZER DEFINITION

# List of token names
tokens = (
    "ID",
    "BLOCK",
    "ADD",
    "PRINT",
    "VIEW",
    "RUN",
    "MINE",
    "EXPORT",
    "STR",
    "INT",
    "LONG",
    "FLOAT",
    "LIST",
    "TUPLE",
    "DICT",
    "NUMBER",
    "STRING",
    "ASSIGN",
    "TYPEASSIGN",
    "SEPARATOR",
    "LPAREN",
    "RPAREN",
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
    "Dict": "DICT",
}

# Regex for simple tokens
t_ASSIGN = r"="
t_TYPEASSIGN = r":"
t_SEPARATOR = r","
t_LPAREN = r"\("
t_RPAREN = r"\)"


# Function-based tokens
def t_STRING(t):
    r"\"[^\"]*\" "
    t.value = t.value[1:-1]  # Remove quotes
    return t


def t_ID(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = keywords.get(t.value, "ID")
    return t


def t_NUMBER(t):
    r"\d+(\.\d+)?"
    if "." in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t


# Track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# Ignore whitespace
t_ignore = " \t\r"


# Ignore comments
def t_COMMENT(t):
    r"//[^\n]*"
    pass


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)


# END LEXICAL ANALYZER DEFINITION

#################################

# BEGIN BLOCKCHAIN IMPLEMENTATION


class Block:
    def __init__(self, index, timestamp, data, previous_hash="0"):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = None
        self.nonce = 0

    def calculate_hash(self):
        """Calculate the hash of the block"""
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.data)}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty=2):
        """Mine the block with proof of work"""
        target = "0" * difficulty
        while self.hash is None or self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined: {self.hash}")

    def to_dict(self):
        """Convert block to dictionary for JSON export"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce,
        }


class Blockchain:
    def __init__(self, block_name, attributes):
        self.block_name = block_name
        self.attributes = attributes  # Store the schema
        self.chain = []
        self.pending_data = {}
        self.is_mined = False

    def add_data(self, data_dict):
        """Add data to pending data after type verification"""
        for key, value in data_dict.items():
            if key not in self.attributes:
                raise Exception(
                    f"Semantic Error: Attribute '{key}' not defined in block schema"
                )

            expected_type = self.attributes[key]
            actual_type = type(value).__name__

            # Type checking
            type_map = {
                "str": "str",
                "int": "int",
                "long": "int",
                "float": "float",
                "List": "list",
                "Tuple": "tuple",
                "Dict": "dict",
            }

            if type_map.get(expected_type) != actual_type:
                raise Exception(
                    f"Semantic Error: Type mismatch for '{key}'. Expected {expected_type}, got {actual_type}"
                )

        self.pending_data.update(data_dict)
        print(f"Data added to pending: {data_dict}")

    def mine_chain(self):
        """Mine all pending data as a new block"""
        if not self.pending_data:
            print("No pending data to mine")
            return

        previous_hash = "0" if len(self.chain) == 0 else self.chain[-1].hash
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=self.pending_data.copy(),
            previous_hash=previous_hash,
        )
        new_block.mine_block()
        self.chain.append(new_block)
        self.pending_data = {}
        self.is_mined = True
        print(f"Block {new_block.index} added to chain")

    def print_chain(self):
        print(f"\nBlockchain: {self.block_name}")
        print(f"Schema: {self.attributes}")
        print(f"Chain length: {len(self.chain)}")
        print(f"Is mined: {self.is_mined}")
        print(f"Pending data: {self.pending_data}")

        for block in self.chain:
            print(f"\nBlock #{block.index}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Data: {block.data}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Hash: {block.hash}")
            print(f"Nonce: {block.nonce}")
        print()

    def export_to_json(self, filename=None):
        """Export blockchain to JSON file"""
        if filename is None:
            filename = f"{self.block_name}_blockchain.json"

        blockchain_data = {
            "block_name": self.block_name,
            "attributes": self.attributes,
            "chain": [block.to_dict() for block in self.chain],
            "pending_data": self.pending_data,
        }

        with open(filename, "w") as f:
            json.dump(blockchain_data, f, indent=4)
        print(f"Blockchain exported to {filename}")

    def is_valid(self):
        """Validate the blockchain"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True


# END BLOCKCHAIN IMPLEMENTATION

#################################

# BEGIN SYNTAX ANALYSIS DEFINITION

# Global symbol table to store blockchains
symbol_table = {}


# Grammar rule for start symbol
def p_start(p):
    """start : block_definition block_operations"""
    print("\n=== Parsing completed successfully ===\n")


# Grammar rule for block definition
def p_block_definition(p):
    """block_definition : BLOCK ID ASSIGN LPAREN attributes RPAREN"""
    block_name = p[2]
    attributes = p[5]

    print(f"Creating blockchain '{block_name}' with attributes: {attributes}")

    # Semantic action: Create blockchain
    try:
        blockchain = Blockchain(block_name, attributes)
        symbol_table[block_name] = blockchain
        print(f"✓ Blockchain '{block_name}' created successfully")
    except Exception as e:
        print(f"✗ Error creating blockchain: {e}")
        raise


# Grammar rules for block operations
def p_block_operations_single(p):
    """block_operations : block_operation"""
    pass


def p_block_operations_multiple(p):
    """block_operations : block_operations block_operation"""
    pass


# Grammar rules for individual block operations
def p_block_operation_add(p):
    """block_operation : ADD ID ASSIGN LPAREN new_atts RPAREN"""
    block_name = p[2]
    data = p[5]

    print(f"\nExecuting ADD on '{block_name}' with data: {data}")

    # Semantic action: Add data to blockchain
    if block_name not in symbol_table:
        print(f"✗ Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    try:
        symbol_table[block_name].add_data(data)
        print(f"✓ Data added to '{block_name}'")
    except Exception as e:
        print(f"✗ {e}")
        raise


def p_block_operation_print(p):
    """block_operation : PRINT ID"""
    block_name = p[2]

    print(f"\nExecuting PRINT on '{block_name}'")

    # Semantic action: Print blockchain
    if block_name not in symbol_table:
        print(f"✗ Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    symbol_table[block_name].print_chain()


def p_block_operation_run(p):
    """block_operation : RUN ID"""
    block_name = p[2]

    print(f"\nExecuting RUN on '{block_name}'")

    # Semantic action: Run blockchain server
    if block_name not in symbol_table:
        print(f"✗ Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    try:
        app = Flask(__name__)
        blockchain = symbol_table[block_name]

        @app.route("/blockchain", methods=["GET"])
        def get_blockchain():
            chain_data = [block.to_dict() for block in blockchain.chain]
            return jsonify(
                {
                    "block_name": blockchain.block_name,
                    "length": len(blockchain.chain),
                    "chain": chain_data,
                }
            )

        print(
            f"✓ Starting blockchain server for '{block_name}' on http://localhost:5000"
        )
        print("  Access at: http://localhost:5000/blockchain")
        app.run(debug=False)
    except Exception as e:
        print(f"✗ Error running blockchain server: {e}")


def p_block_operation_mine(p):
    """block_operation : MINE ID"""
    block_name = p[2]

    print(f"\nExecuting MINE on '{block_name}'")

    # Semantic action: Mine blockchain
    if block_name not in symbol_table:
        print(f"✗ Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    try:
        symbol_table[block_name].mine_chain()
        print(f"✓ Blockchain '{block_name}' mined successfully")
    except Exception as e:
        print(f"✗ Error mining blockchain: {e}")
        raise


def p_block_operation_export(p):
    """block_operation : EXPORT ID"""
    block_name = p[2]

    print(f"\nExecuting EXPORT on '{block_name}'")

    # Semantic action: Export blockchain to JSON
    if block_name not in symbol_table:
        print(f"✗ Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    try:
        symbol_table[block_name].export_to_json()
        print(f"✓ Blockchain '{block_name}' exported successfully")
    except Exception as e:
        print(f"✗ Error exporting blockchain: {e}")
        raise


def p_block_operation_view(p):
    """block_operation : VIEW ID"""
    block_name = p[2]

    print(f"\nExecuting VIEW on '{block_name}'")

    # Semantic action: View blockchain validity
    if block_name not in symbol_table:
        print(f"✗ Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    is_valid = symbol_table[block_name].is_valid()
    print(f"Blockchain '{block_name}' is {'VALID' if is_valid else 'INVALID'}")


# Grammar rules for type
def p_type(p):
    """type : STR
    | INT
    | LONG
    | FLOAT
    | LIST
    | TUPLE
    | DICT"""
    p[0] = p[1]


# Grammar rule for attribute
def p_attribute(p):
    """attribute : ID TYPEASSIGN type"""
    p[0] = (p[1], p[3])


# Grammar rules for attributes
def p_attributes_single(p):
    """attributes : attribute"""
    p[0] = {p[1][0]: p[1][1]}


def p_attributes_multiple(p):
    """attributes : attributes SEPARATOR attribute"""
    p[0] = p[1]
    p[0][p[3][0]] = p[3][1]


# Grammar rules for new_att
def p_new_att_string(p):
    """new_att : ID TYPEASSIGN STRING"""
    p[0] = (p[1], p[3])


def p_new_att_number(p):
    """new_att : ID TYPEASSIGN NUMBER"""
    p[0] = (p[1], p[3])


# Grammar rules for new_atts
def p_new_atts_single(p):
    """new_atts : new_att"""
    p[0] = {p[1][0]: p[1][1]}


def p_new_atts_multiple(p):
    """new_atts : new_atts SEPARATOR new_att"""
    p[0] = p[1]
    p[0][p[3][0]] = p[3][1]


# Error handling
def p_error(p):
    if p:
        print(f"✗ Syntax error at token {p.type} ('{p.value}') at line {p.lineno}")
    else:
        print("✗ Syntax error at EOF")


# END SYNTAX ANALYSIS DEFINITION


################
## CALL PARSER
###############


def main():
    print("=" * 60)
    print("Blockchain Programming Language Parser")
    print("=" * 60)

    # Build the lexer and parser
    lexer = lex.lex()
    parser = yacc.yacc()

    # Read the file
    try:
        with open("Program_Test.txt", "r") as f:
            data = f.read()

        print("\nInput program:")
        print("-" * 60)
        print(data)
        print("-" * 60)

        # Parse the file
        print("\nParsing...\n")
        result = parser.parse(data, lexer=lexer)

        print("\n" + "=" * 60)
        print("Execution completed")
        print("=" * 60)

    except FileNotFoundError:
        print("✗ Error: Program_Test.txt not found")
    except Exception as e:
        print(f"\n✗ Fatal Error: {e}")


if __name__ == "__main__":
    main()

