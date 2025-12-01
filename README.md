# Group2Coin Blockchain Platform

Full-stack blockchain application with cryptocurrency and supply chain management capabilities.

## Quick Start

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```
Server runs on http://localhost:5000

### Frontend
```bash
cd frontend
npm install
npm start
```
App runs on http://localhost:3000

## Features

### Cryptocurrency
- Wallet creation with RSA key pairs
- Send and receive transactions with digital signatures
- Proof-of-work mining with configurable difficulty
- Real-time balance tracking
- Complete transaction history

### Supply Chain Management
- Product registration with unique authentication hashes
- Event tracking through supply chain journey
- Authenticity verification to prevent counterfeiting
- Safety monitoring with quality alerts
- Category and manufacturer filtering

## Technology Stack

**Backend**: Python 3.8+, Flask, Cryptography, PyCryptodome
**Frontend**: React 18, Axios, CSS3

## Architecture

```
backend/
  blockchain/     - Core blockchain logic (blocks, transactions, proof-of-work)
  wallet/         - RSA wallet generation
  utils/          - Cryptographic functions (SHA-256, RSA signing)
  api/            - REST API endpoints
  main.py         - Flask application

frontend/
  components/     - React UI components
  services/       - API client
  App.jsx         - Main application
```

## Key Algorithms

### 1. SHA-256 Hashing
Creates unique fingerprints of data. Used for block hashes, transaction verification, and wallet addresses.

### 2. Proof-of-Work Mining
Secures blockchain by requiring computational work. Difficulty adjustable. Average attempts = 16^difficulty.

### 3. RSA Digital Signatures
2048-bit RSA for transaction signing and verification. Proves transaction ownership and prevents forgery.

### 4. Balance Calculation
Iterates through blockchain to sum received and subtract sent transactions for any address.

### 5. Blockchain Validation
Verifies hash integrity, chain linkage, proof-of-work, and transaction validity for entire chain.

## API Endpoints

### Blockchain
- GET /api/blockchain - Get full chain
- GET /api/blockchain/validate - Validate integrity
- GET /api/blockchain/pending - Get pending transactions

### Wallet
- POST /api/wallet/create - Create new wallet
- GET /api/wallet/:address/balance - Get balance
- POST /api/wallet/import - Import wallet

### Transactions
- POST /api/transaction/create - Create signed transaction

### Mining
- POST /api/mine - Mine pending transactions into block

### Supply Chain
- POST /api/supplychain/product/register - Register product
- POST /api/supplychain/product/:id/event - Add tracking event
- GET /api/supplychain/product/:id - Get product details
- POST /api/supplychain/product/:id/verify - Verify authenticity

## Security Features

- SHA-256 cryptographic hashing (256-bit security)
- RSA-2048 encryption and digital signatures
- Proof-of-work consensus mechanism
- Blockchain immutability through hash chaining
- Transaction signature verification
- Balance validation before transactions
- Product authentication hashes

## Documentation

See DOCUMENTATION.md for:
- Detailed algorithm explanations
- Complete function reference
- Code structure breakdown
- Data flow diagrams
- Security analysis

## Development

This is an educational project demonstrating blockchain concepts. Not production-ready.

For production use, consider:
- Database persistence
- Distributed nodes
- Network synchronization
- User authentication
- HTTPS encryption
- Rate limiting
- Wallet encryption

## License

Educational use only.

## Authors

Group 2 Team
