import hashlib
import json
import time

import ply.lex as lex
import ply.yacc as yacc
from flask import Flask, jsonify, render_template, request, send_from_directory

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

t_ASSIGN = r"="
t_TYPEASSIGN = r":"
t_SEPARATOR = r","
t_LPAREN = r"\("
t_RPAREN = r"\)"


def t_STRING(t):
    r"\"[^\"]*\" "
    t.value = t.value[1:-1]
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


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


t_ignore = " \t\r"


def t_COMMENT(t):
    r"//[^\n]*"
    pass


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)


class Block:
    """Represents a single block in the blockchain"""

    def __init__(self, index, timestamp, data, previous_hash="0"):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = None
        self.nonce = 0

    def calculate_hash(self):
        """Calculate SHA-256 hash of the block"""
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.data)}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty=2):
        """Mine the block using proof-of-work"""
        target = "0" * difficulty
        while self.hash is None or self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined: {self.hash}")

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce,
        }


class Blockchain:
    """Manages the blockchain with validation and operations"""

    def __init__(self, block_name, attributes):
        self.block_name = block_name
        self.attributes = attributes
        self.chain = []
        self.pending_data = {}
        self.is_mined = False

    def add_data(self, data_dict):
        """Add data to pending transactions with type checking"""
        for key, value in data_dict.items():
            if key not in self.attributes:
                raise Exception(
                    f"Semantic Error: Attribute '{key}' not defined in block schema"
                )

            expected_type = self.attributes[key]
            actual_type = type(value).__name__

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
        print(f"Data added: {data_dict}")

    def mine_chain(self):
        """Mine pending data into a new block"""
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
        """Validate blockchain integrity"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True


symbol_table = {}


def p_start(p):
    """start : block_definition block_operations"""
    pass


def p_block_definition(p):
    """block_definition : BLOCK ID ASSIGN LPAREN attributes RPAREN"""
    block_name = p[2]
    attributes = p[5]

    try:
        blockchain = Blockchain(block_name, attributes)
        symbol_table[block_name] = blockchain
        print(f"Blockchain '{block_name}' created")
    except Exception as e:
        print(f"Error: {e}")
        raise


def p_block_operations_single(p):
    """block_operations : block_operation"""
    pass


def p_block_operations_multiple(p):
    """block_operations : block_operations block_operation"""
    pass


def p_block_operation_add(p):
    """block_operation : ADD ID ASSIGN LPAREN new_atts RPAREN"""
    block_name = p[2]
    data = p[5]

    if block_name not in symbol_table:
        print(f"Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    try:
        symbol_table[block_name].add_data(data)
    except Exception as e:
        print(f"{e}")
        raise


def p_block_operation_print(p):
    """block_operation : PRINT ID"""
    block_name = p[2]

    if block_name not in symbol_table:
        print(f"Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    symbol_table[block_name].print_chain()


def p_block_operation_run(p):
    """block_operation : RUN ID"""
    block_name = p[2]

    if block_name not in symbol_table:
        print(f"Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    try:
        app = Flask(__name__)
        blockchain = symbol_table[block_name]

        @app.route("/")
        def index():
            return render_template("index.html")

        @app.route("/api/blockchain", methods=["GET"])
        def get_blockchain():
            chain_data = [block.to_dict() for block in blockchain.chain]
            return jsonify(
                {
                    "block_name": blockchain.block_name,
                    "length": len(blockchain.chain),
                    "chain": chain_data,
                    "is_valid": blockchain.is_valid(),
                    "schema": blockchain.attributes,
                }
            )

        @app.route("/api/block/<int:index>", methods=["GET"])
        def get_block(index):
            if index < 0 or index >= len(blockchain.chain):
                return jsonify({"error": "Block not found"}), 404
            return jsonify(blockchain.chain[index].to_dict())

        @app.route("/api/validate", methods=["GET"])
        def validate_chain():
            is_valid = blockchain.is_valid()
            return jsonify(
                {
                    "block_name": blockchain.block_name,
                    "is_valid": is_valid,
                    "message": (
                        "Blockchain is valid" if is_valid else "Blockchain is invalid"
                    ),
                }
            )

        @app.route("/api/pending", methods=["GET"])
        def get_pending():
            return jsonify(
                {
                    "block_name": blockchain.block_name,
                    "pending_data": blockchain.pending_data,
                }
            )

        @app.route("/api/mine", methods=["POST"])
        def mine_block():
            try:
                blockchain.mine_chain()
                return jsonify({"success": True, "message": "Block mined successfully"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 400

        @app.route("/api/add", methods=["POST"])
        def add_data():
            try:
                data = request.json
                blockchain.add_data(data)
                return jsonify({"success": True, "message": "Data added to pending"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 400

        @app.route("/api/execute", methods=["POST"])
        def execute_command():
            try:
                command_text = request.json.get("command", "").strip()
                if not command_text:
                    return jsonify({"success": False, "error": "No command provided"}), 400

                # Parse command components
                command_parts = command_text.split()
                if not command_parts:
                    return jsonify({"success": False, "error": "Invalid command format"}), 400

                cmd = command_parts[0].upper()

                # Capture output
                import io
                import sys
                old_stdout = sys.stdout
                sys.stdout = buffer = io.StringIO()

                try:
                    if cmd == "BLOCK" and len(command_parts) >= 4:
                        # Handle block creation: block name = (attributes)
                        # Parse full command with new grammar
                        lexer = lex.lex()
                        parser = yacc.yacc()
                        parser.parse(command_text, lexer=lexer)

                    elif cmd in ["ADD", "MINE", "PRINT", "VIEW", "EXPORT"] and len(command_parts) >= 2:
                        # Handle operations on existing blockchains
                        blockchain_name = command_parts[1]

                        if blockchain_name not in symbol_table:
                            return jsonify({"success": False, "error": f"Blockchain '{blockchain_name}' not defined"}), 400

                        blockchain = symbol_table[blockchain_name]

                        if cmd == "ADD":
                            # Extract data part: add name = (data)
                            if "=" not in command_text:
                                return jsonify({"success": False, "error": "Invalid add command format"}), 400
                            data_part = command_text.split("=", 1)[1].strip()
                            if not data_part.startswith("(") or not data_part.endswith(")"):
                                return jsonify({"success": False, "error": "Invalid data format"}), 400

                            data_str = data_part[1:-1].strip()
                            data_pairs = [pair.strip() for pair in data_str.split(",")]
                            data_dict = {}
                            for pair in data_pairs:
                                if ":" not in pair:
                                    return jsonify({"success": False, "error": "Invalid key:value format"}), 400
                                key, value_str = pair.split(":", 1)
                                key = key.strip()
                                value_str = value_str.strip()

                                # Parse value
                                if value_str.startswith('"') and value_str.endswith('"'):
                                    value = value_str[1:-1]
                                elif "." in value_str and value_str.replace(".", "").replace("-", "").isdigit():
                                    value = float(value_str)
                                elif value_str.replace("-", "").isdigit():
                                    value = int(value_str)
                                else:
                                    return jsonify({"success": False, "error": "Invalid value format"}), 400

                                data_dict[key] = value

                            blockchain.add_data(data_dict)

                        elif cmd == "MINE":
                            blockchain.mine_chain()

                        elif cmd == "PRINT":
                            blockchain.print_chain()

                        elif cmd == "VIEW":
                            is_valid = blockchain.is_valid()
                            print(f"Blockchain '{blockchain_name}' is {'VALID' if is_valid else 'INVALID'}")

                        elif cmd == "EXPORT":
                            blockchain.export_to_json()

                    else:
                        return jsonify({"success": False, "error": "Unknown or incomplete command"}), 400

                    output = buffer.getvalue()

                except Exception as e:
                    print(f"Error: {e}")
                    output = str(e)

                sys.stdout = old_stdout

                return jsonify({"success": True, "output": output or "Command executed successfully"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        print(f"\n=== Blockchain Server Started ===")
        print(f"Server running at http://localhost:8080")
        print(f"Open browser to view UI")
        print(f"=================================\n")
        app.run(debug=False, port=8080)
    except Exception as e:
        print(f"Error: {e}")


def p_block_operation_mine(p):
    """block_operation : MINE ID"""
    block_name = p[2]

    if block_name not in symbol_table:
        print(f"Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    try:
        symbol_table[block_name].mine_chain()
    except Exception as e:
        print(f"Error: {e}")
        raise


def p_block_operation_export(p):
    """block_operation : EXPORT ID"""
    block_name = p[2]

    if block_name not in symbol_table:
        print(f"Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    try:
        symbol_table[block_name].export_to_json()
    except Exception as e:
        print(f"Error: {e}")
        raise


def p_block_operation_view(p):
    """block_operation : VIEW ID"""
    block_name = p[2]

    if block_name not in symbol_table:
        print(f"Semantic Error: Blockchain '{block_name}' not defined")
        raise Exception(f"Blockchain '{block_name}' not defined")

    is_valid = symbol_table[block_name].is_valid()
    print(f"Blockchain '{block_name}' is {'VALID' if is_valid else 'INVALID'}")


def p_type(p):
    """type : STR
    | INT
    | LONG
    | FLOAT
    | LIST
    | TUPLE
    | DICT"""
    p[0] = p[1]


def p_attribute(p):
    """attribute : ID TYPEASSIGN type"""
    p[0] = (p[1], p[3])


def p_attributes_single(p):
    """attributes : attribute"""
    p[0] = {p[1][0]: p[1][1]}


def p_attributes_multiple(p):
    """attributes : attributes SEPARATOR attribute"""
    p[0] = p[1]
    p[0][p[3][0]] = p[3][1]


def p_new_att_string(p):
    """new_att : ID TYPEASSIGN STRING"""
    p[0] = (p[1], p[3])


def p_new_att_number(p):
    """new_att : ID TYPEASSIGN NUMBER"""
    p[0] = (p[1], p[3])


def p_new_atts_single(p):
    """new_atts : new_att"""
    p[0] = {p[1][0]: p[1][1]}


def p_new_atts_multiple(p):
    """new_atts : new_atts SEPARATOR new_att"""
    p[0] = p[1]
    p[0][p[3][0]] = p[3][1]


def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} ('{p.value}') at line {p.lineno}")
    else:
        print("Syntax error at EOF")


def main():
    lexer = lex.lex()
    parser = yacc.yacc()

    try:
        with open("Program_Test.txt", "r") as f:
            data = f.read()

        result = parser.parse(data, lexer=lexer)

    except FileNotFoundError:
        print("Error: Program_Test.txt not found")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
