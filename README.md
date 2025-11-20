# toy-lang

This is a domain-specific language for blockchain operations with a Flask web API, implemented as a programming assignment.

**Author:** Alex Morales Trevisan  
**Course:** CIIC4030 - Programming Languages

## What is it?

A custom programming language implemented in Python using the PLY library that allows you to:

- Define blockchain schemas
- Add transactions to blockchains
- Mine blocks using proof-of-work
- Validate blockchain integrity
- Export data to JSON
- Interact with blockchains via a web UI

## How to Run

1. Make sure you have Python installed
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python Main.py`

This parses the test program in `Program_Test.txt` and starts a web server at http://localhost:8080.

## How to Test

Visit http://localhost:8080 in your browser to see the blockchain web interface, or use the API endpoints:

- GET /blockchain - Get full blockchain data
- GET /block/0 - Get specific block
- GET /validate - Check if blockchain is valid
- GET /pending - View unmined transactions
