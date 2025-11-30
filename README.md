# Group2Coin Full Source Code Explanation

Let me explain the entire project architecture and how everything works together.

## **Project Overview**

Group2Coin is a full-stack blockchain cryptocurrency application with:
- **Backend**: Python/Flask REST API managing the blockchain
- **Frontend**: React single-page application for user interaction

---

## **BACKEND ARCHITECTURE**

### **1. Cryptographic Utilities (`backend/utils/crypto.py`)**

This module handles all cryptographic operations:

```python
def calculate_hash(data):
    """
    Uses SHA-256 to create unique fingerprints of data
    - Converts dictionaries/objects to JSON strings
    - Creates a 64-character hexadecimal hash
    - Used for: block hashes, transaction hashes, wallet addresses
    """
```

**Why SHA-256?** It's:
- Deterministic (same input = same output)
- One-way (cannot reverse the hash)
- Collision-resistant (virtually impossible to find two inputs with same hash)

```python
def generate_key_pair():
    """
    Creates RSA 2048-bit public-private key pairs
    - Private key: Used to sign transactions (proves ownership)
    - Public key: Used to verify signatures and receive coins
    - Returns both keys in PEM format (text-based encoding)
    """
```

**RSA Encryption**: Asymmetric cryptography where:
- You can encrypt with public key, decrypt with private key
- You can sign with private key, verify with public key
## Group2Coin

Group2Coin is a small educational full-stack blockchain application implemented with:

- Backend: Python + Flask (REST API)
- Frontend: React (single-page app)

This repository contains a basic blockchain implementation (blocks, transactions, proof-of-work), a wallet generator, a simple mining flow, and a React UI that interacts with the Flask API.

---

## Quick Start (development)

Requirements:
- Python 3.8+
- Node.js 16+ / npm

1) Start the backend

```bash
cd backend
python3 -m venv venv        # create venv if needed
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

The backend runs on `http://localhost:5000` and exposes the API under `/api`.

2) Start the frontend (dev server)

```bash
cd frontend
npm install
npm start
```

The frontend runs on `http://localhost:3000` by default and calls the backend at `http://localhost:5000/api`.

## Build (production)

```bash
npm --prefix frontend run build
# Serve the build/ directory with a static server
```

## API Reference (most-used endpoints)

- GET `/api/blockchain` — returns the full chain, difficulty, mining_reward and a snapshot of pending transactions
- GET `/api/blockchain/pending` — returns pending transactions
- GET `/api/blockchain/difficulty` — returns current difficulty
- GET `/api/blockchain/validate` — returns chain validity

- POST `/api/wallet/create` — create a new wallet (returns address, public_key, private_key)
- GET `/api/wallet/<address>/balance` — get calculated balance for an address
- GET `/api/wallet/<address>/transactions` — return transactions involving the address
- GET `/api/wallet/export/<address>` — download JSON export of a wallet
- POST `/api/wallet/import` — import wallet JSON into server memory

- POST `/api/transaction/create` — create & sign a transaction (sender public key, recipient, amount, private_key)
- GET `/api/transaction/pending` — pending transactions (short view)

- POST `/api/mine` — mine pending transactions; body: `{ "miner_address": "..." }`
- GET `/api/blockchain/reward` — current mining reward

## Notes, recent fixes & behavior

- Wallets are stored in-memory on the server in `backend/api/routes.py`. They are ephemeral and will be lost on server restart. If you need persistence, add a simple file/db store.
- The `/api/blockchain` endpoint now includes a `pending_transactions` array so the frontend can show pending counts without extra requests.
- Frontend defensive updates: `frontend/src/components/BlockchainViewer.jsx` now guards accesses to `pending_transactions` and `block.transactions` to avoid runtime errors if data is missing.
- Dashboard refresh behavior: `frontend/src/components/Dashboard.jsx` now sets a loading state when refreshing, disables the Refresh button while fetching, and shows an alert on failure.

## Testing

- A quick backend smoke test script is available at `backend/test_setup.py` — run `python3 backend/test_setup.py` to verify imports and simple blockchain operations.

## Development notes & TODOs

- Improve wallet persistence (file or database) to avoid in-memory loss.
- Add more robust error handling and user-friendly toasts instead of `alert()`.
- Add unit tests for blockchain functions (mining, validation, balances).

## Directory layout

```
backend/
  ├─ api/
  ├─ blockchain/
  ├─ utils/
  ├─ wallet/
  └─ main.py

frontend/
  ├─ src/
  └─ package.json
```

## How I validated changes

- Ran `python3 backend/test_setup.py` — backend imports and basic transactions succeeded.
- Built the frontend with `npm run build` to ensure components compile (there is an unrelated ESLint warning in `Wallet.jsx`).

## License

This repository is for educational purposes. Add a license file if you want to share publicly.

----

If you'd like, I can also open a small PR with these README changes, or add CI steps / unit tests next. Let me know which you'd prefer.

    pendingTransactions: 0,
    difficulty: 0,
    isValid: true,
  });

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 5000);  // Refresh every 5s
    return () => clearInterval(interval);  // Cleanup on unmount
  }, []);

  const loadDashboardData = async () => {
    // Makes 4 parallel API calls
    const [blockchainRes, pendingRes, difficultyRes, validationRes] = 
      await Promise.all([
        blockchainAPI.getBlockchain(),
        blockchainAPI.getPendingTransactions(),
        blockchainAPI.getDifficulty(),
        blockchainAPI.validateBlockchain(),
      ]);
    
    // Updates state with all data
    setStats({ ... });
  };
```

**Features:**
- Real-time stats display
- Auto-refresh every 5 seconds
- Blockchain validation status
- Network overview

---

### **5. Wallet Component (`frontend/src/components/Wallet.jsx`)**

```javascript
function Wallet({ wallet, setWallet }) {  // Receives wallet as prop
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [showPrivateKey, setShowPrivateKey] = useState(false);

  useEffect(() => {
    if (wallet) {
      loadWalletData();  // Auto-load balance when wallet exists
    }
  }, [wallet]);

  const createNewWallet = async () => {
    const response = await walletAPI.createWallet();
    setWallet(response.data);  // Updates global wallet state
    alert('Wallet created! Save your private key!');
  };
```

**Features:**
- Create new wallets
- Display address, public key, private key
- Toggle private key visibility (security)
- Copy keys to clipboard
- Show balance and transaction history
- Persistent wallet across navigation

**Security:**
- Private key hidden by default
- Warning messages
- Copy functionality for safe storage

---

### **6. Transactions Component (`frontend/src/components/Transactions.jsx`)**

```javascript
function Transactions({ wallet }) {
  const [formData, setFormData] = useState({
    senderPublicKey: '',
    senderPrivateKey: '',
    recipientAddress: '',
    amount: '',
  });

  useEffect(() => {
    if (wallet) {
      // Auto-fill keys from wallet
      setFormData(prev => ({
        ...prev,
        senderPublicKey: wallet.public_key,
        senderPrivateKey: wallet.private_key,
      }));
    }
  }, [wallet]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (amount <= 0) {
      alert('Amount must be positive');
      return;
    }
    
    // Create transaction
    const response = await transactionAPI.createTransaction(
      formData.senderPublicKey,
      formData.recipientAddress,
      amount,
      formData.senderPrivateKey
    );
    
    alert('Transaction submitted!');
  };
```

**Features:**
- Auto-fills keys from global wallet
- Form validation
- Transaction submission
- Success/error feedback
- Clear form functionality

**Transaction Flow:**
1. User fills recipient and amount
2. Keys auto-filled from wallet
3. Frontend sends to backend
4. Backend validates and signs
5. Transaction added to pending pool
6. User receives confirmation

---

### **7. Mining Component (`frontend/src/components/Mining.jsx`)**

```javascript
function Mining({ wallet }) {
  const [minerAddress, setMinerAddress] = useState('');
  const [mining, setMining] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    if (wallet) {
      setMinerAddress(wallet.address);  // Auto-fill miner address
    }
  }, [wallet]);

  const handleMine = async () => {
    if (!minerAddress) {
      alert('Enter miner address');
      return;
    }

    setMining(true);  // Show loading state
    
    try {
      const response = await miningAPI.mineBlock(minerAddress);
      alert('Block mined! You earned 50 G2C!');
    } catch (error) {
      alert('Mining failed');
    }
    
    setMining(false);  // Hide loading
  };
```

**Features:**
- Real-time pending transaction count
- Current difficulty display
- Mining reward information
- Auto-fill miner address from wallet
- Mining progress indicator
- Difficulty adjustment controls

**Mining Process:**
1. User clicks "Start Mining"
2. Frontend calls backend mine endpoint
3. Backend performs proof-of-work
4. May take seconds to minutes depending on difficulty
5. Block added to chain
6. Miner receives 50 G2C reward

---

### **8. Blockchain Viewer (`frontend/src/components/BlockchainViewer.jsx`)**

```javascript
function BlockchainViewer() {
  const [blockchain, setBlockchain] = useState(null);
  const [expandedBlocks, setExpandedBlocks] = useState(new Set([0]));

  const loadBlockchain = async () => {
    const response = await blockchainAPI.getBlockchain();
    setBlockchain(response.data);
  };

  const toggleBlock = (index) => {
    setExpandedBlocks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);  // Collapse
      } else {
        newSet.add(index);  // Expand
      }
      return newSet;
    });
  };
```

**Features:**
- View all blocks in the chain
- Expand/collapse individual blocks
- View block details (hash, previous hash, nonce)
- View all transactions in each block
- Genesis block badge
- Expand all / Collapse all functionality

**Data Display:**
- Block index and timestamp
- Full block hash
- Previous block hash (shows chain linkage)
- Nonce (proof-of-work)
- All transactions with sender, recipient, amount

---

## **KEY CONCEPTS EXPLAINED**

### **1. How Blockchain Works**

```
Genesis Block → Block 1 → Block 2 → Block 3
    ↓              ↓          ↓          ↓
  Hash: 0x00abc  Hash:0x00def Hash:0x00xyz ...
                    ↑
              prev_hash: 0x00abc
```

Each block:
- Contains transactions
- Has a hash (unique fingerprint)
- References previous block's hash
- Cannot be altered without breaking the chain

### **2. Proof of Work**

```python
target = '0000'  # difficulty = 4
nonce = 0

while True:
    hash = calculate_hash(block_data + nonce)
    if hash.startswith(target):
        # Found valid nonce!
        break
    nonce += 1  # Try next nonce
```

**Why it matters:**
- Makes mining difficult and expensive
- Prevents spam/attacks
- Secures the network
- Higher difficulty = more security

### **3. Digital Signatures**

```
Transaction Creation:
1. User creates transaction: "Send 10 G2C to Bob"
2. Hash the transaction: hash = SHA256(transaction)
3. Sign the hash: signature = RSA_sign(hash, private_key)
4. Attach signature to transaction

Transaction Verification:
1. Receive transaction with signature
2. Hash the transaction data
3. Verify: RSA_verify(hash, signature, public_key)
4. If valid: Sender authorized this transaction
```

### **4. Balance Calculation (UTXO Model Simplified)**

```javascript
balance = 0

for (block in blockchain) {
  for (tx in block.transactions) {
    if (tx.sender == myAddress) {
      balance -= tx.amount  // Spent money
    }
    if (tx.recipient == myAddress) {
      balance += tx.amount  // Received money
    }
  }
}

return balance
```

### **5. Mining Incentive**

```
Pending Transactions:
- Alice → Bob: 5 G2C
- Charlie → Dave: 10 G2C
- Eve → Frank: 3 G2C

Miner mines block:
- Includes all pending transactions
- Adds reward transaction: MINING_REWARD → Miner: 50 G2C
- Performs proof-of-work
- Block added to chain

Result:
- Alice, Charlie, Eve transactions confirmed
- Bob, Dave, Frank receive coins
- Miner receives 50 G2C reward
```

---

## **SECURITY FEATURES**

### **1. Cryptographic Security**
- SHA-256 hashing (impossible to reverse)
- RSA-2048 encryption (extremely strong)
- Digital signatures (proves ownership)

### **2. Blockchain Immutability**
```
If you try to change Block 1:
- Block 1 hash changes
- Block 2's previous_hash no longer matches
- Chain breaks!
- Everyone knows it's tampered
```

### **3. Proof of Work**
- Must perform computational work to add blocks
- Prevents spam attacks
- Makes history rewriting computationally infeasible

### **4. Transaction Validation**
- Signature verification
- Balance checking
- Double-spend prevention

---

## **DATA FLOW EXAMPLE**

Let's trace a complete transaction:

**1. Alice creates a wallet:**
```
Frontend: Click "Create Wallet"
→ API call: POST /api/wallet/create
→ Backend: Generate RSA keys, create wallet
→ Response: {address, public_key, private_key}
→ Frontend: Display wallet, user saves keys
```

**2. Alice receives 50 G2C from mining:**
```
Frontend: Enter address, click "Mine"
→ API call: POST /api/mine {miner_address: "alice"}
→ Backend: Create block with reward transaction
→ Backend: Perform proof-of-work
→ Backend: Add block to chain
→ Response: Block mined successfully
→ Frontend: Show success message
```

**3. Alice sends 10 G2C to Bob:**
```
Frontend: Fill form (Bob's address, amount:10)
→ Frontend: Sign transaction with Alice's private key
→ API call: POST /api/transaction/create
→ Backend: Verify signature
→ Backend: Check Alice has balance ≥ 10
→ Backend: Add to pending pool
→ Response: Transaction pending
→ Frontend: Show confirmation
```

**4. Someone mines the pending transaction:**
```
Frontend: Click "Mine"
→ API call: POST /api/mine
→ Backend: Include Alice→Bob transaction in block
→ Backend: Perform proof-of-work
→ Backend: Add block to chain
→ Alice balance: 50 - 10 = 40 G2C
→ Bob balance: 0 + 10 = 10 G2C
→ Transaction confirmed!
```

---

## **FILE STRUCTURE SUMMARY**

```
backend/
├── blockchain/          # Core blockchain logic
│   ├── block.py        # Block structure + mining
│   ├── blockchain.py   # Chain management
│   └── transaction.py  # Transaction handling
├── wallet/
│   └── wallet.py       # Wallet creation
├── utils/
│   └── crypto.py       # Cryptographic functions
├── api/
│   └── routes.py       # REST API endpoints
└── main.py             # Flask app entry point

frontend/
├── src/
│   ├── components/     # UI components
│   │   ├── Header.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Wallet.jsx
│   │   ├── Transactions.jsx
│   │   ├── Mining.jsx
│   │   └── BlockchainViewer.jsx
│   ├── services/
│   │   └── api.js      # Backend communication
│   ├── App.jsx         # Main app component
│   └── index.js        # React entry point
```

---

This is a complete, working blockchain implementation! It demonstrates:
- **Cryptography**: Hashing, encryption, digital signatures
- **Distributed Systems**: Blockchain, consensus, validation
- **Web Development**: REST APIs, React, state management
- **Security**: Private keys, signatures, proof-of-work

The code is educational but includes real production concepts used in actual cryptocurrencies like Bitcoin and Ethereum!
