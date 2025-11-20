# Programming Languages Assignment #4 Report

**Name:** Alex Morales Trevisan  
**Course:** CIIC4030

## How to Run the Code

1. Make sure you have Python installed
2. Install required packages: `pip install -r requirements.txt`
3. For easier installation, check out the GitHub repo: https://github.com/AlexMoralesDev/toy-lang
4. Run the main program: `python Main.py`

This will parse `Program_Test.txt` and start a web server at http://localhost:8080. Note: The web server requires the `static/` (CSS and JS files) and `templates/` (HTML files) directories to be present in the project for the UI to work.

## How to Test

The `Program_Test.txt` file contains a test program written in the blockchain language:

### Test Program Commands:

- `block CryptoChain = (sender:str, receiver:str, amount:float, timestamp:int)` - Creates blockchain with schema
- `add CryptoChain = (sender:"Alice", receiver:"Bob", amount:50.5, timestamp:1234567890)` - Adds transaction data
- `mine CryptoChain` - Mines a block using proof-of-work
- `print CryptoChain` - Shows blockchain details in console
- `view CryptoChain` - Validates the blockchain integrity
- `export CryptoChain` - Saves blockchain to JSON file
- `run CryptoChain` - Starts the Flask web server

### Test Output Meaning:

1. **Blockchain 'CryptoChain' created** - Schema defined successfully
2. **Data added: {...}** - Transaction added to pending queue
3. **Block mined: 000...** - Mining completed, new block added
4. **Blockchain Details** - Shows blocks, hashes, nonces, and data
5. **Blockchain 'CryptoChain' is VALID** - All hash links verified
6. **Server running at http://localhost:8080** - Web interface available

### Web API Testing:

After running, visit http://localhost:8080 in browser or use API endpoints:

- `GET /blockchain` - View full blockchain
- `GET /block/0` - View specific block
- `GET /validate` - Check blockchain validity
- `GET /pending` - View unmined transactions

Expected outputs confirm proper blockchain creation, mining, and validation.
