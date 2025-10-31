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
- 2048 bits = extremely secure (would take centuries to crack)

```python
def sign_data(private_key_pem, data):
    """
    Creates a digital signature using PSS padding
    - Proves that the transaction was created by the private key holder
    - Cannot be forged without the private key
    - Returns hexadecimal signature string
    """

def verify_signature(public_key_pem, data, signature_hex):
    """
    Verifies that a signature matches the data and public key
    - Prevents transaction tampering
    - Returns True/False
    """
```

---

### **2. Transaction System (`backend/blockchain/transaction.py`)**

```python
class Transaction:
    def __init__(self, sender, recipient, amount, signature=None, timestamp=None):
        """
        Represents a transfer of Group2Coin between addresses
        
        Parameters:
        - sender: Public key of sender (or 'MINING_REWARD' for mining)
        - recipient: Public key/address of recipient
        - amount: How many G2C to transfer
        - signature: Digital signature proving sender authorized this
        - timestamp: When transaction was created
        """
```

**Transaction Flow:**
1. User creates transaction with sender, recipient, amount
2. Transaction is signed with sender's private key
3. Signature proves ownership without revealing private key
4. Transaction goes into pending pool
5. Miner includes it in a block
6. Transaction becomes permanent on blockchain

```python
def sign_transaction(self, private_key):
    """
    Signs the transaction data (excluding the signature itself)
    - Creates a hash of: sender + recipient + amount + timestamp
    - Signs this hash with the private key
    - Stores signature in the transaction
    """

def is_valid(self):
    """
    Validates the transaction:
    1. Mining rewards are always valid (system-generated)
    2. Regular transactions must have signatures
    3. Signature must match the public key and data
    """
```

---

### **3. Block Structure (`backend/blockchain/block.py`)**

```python
class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None, nonce=0):
        """
        A block is a container for transactions, linked to previous block
        
        Parameters:
        - index: Position in the chain (0, 1, 2, 3...)
        - transactions: List of Transaction objects in this block
        - previous_hash: Hash of the previous block (creates the chain)
        - timestamp: When block was created
        - nonce: Number used in proof-of-work mining
        """
```

**Block Structure Visualization:**
```
Block #1                          Block #2
┌─────────────────────┐          ┌─────────────────────┐
│ Index: 1            │          │ Index: 2            │
│ Previous: 0x000abc  │◄─────────│ Previous: 0x000def  │
│ Transactions: [...]  │          │ Transactions: [...]  │
│ Nonce: 45832        │          │ Nonce: 93021        │
│ Hash: 0x000def      │          │ Hash: 0x000xyz      │
└─────────────────────┘          └─────────────────────┘
```

```python
def calculate_hash(self):
    """
    Creates unique fingerprint of the block
    - Combines: index + transactions + previous_hash + timestamp + nonce
    - Any tiny change = completely different hash
    - This is what makes blockchain tamper-proof
    """

def mine_block(self, difficulty):
    """
    PROOF OF WORK ALGORITHM
    
    Goal: Find a nonce that makes the hash start with 'difficulty' zeros
    
    Example with difficulty=4:
    - Try nonce=0: hash = 5a3b2c1d... (no leading zeros) ❌
    - Try nonce=1: hash = 9f8e7d6c... (no leading zeros) ❌
    - Try nonce=2: hash = 3c4d5e6f... (no leading zeros) ❌
    - ...
    - Try nonce=45832: hash = 0000a1b2... (4 leading zeros!) ✓
    
    Why this matters:
    - Makes mining computationally expensive
    - Prevents spam attacks (must do work to add blocks)
    - Secures the blockchain (would need massive compute to alter history)
    """
```

**Mining Difficulty:**
- Difficulty 1: ~16 attempts average (hash starts with 0)
- Difficulty 2: ~256 attempts average (00)
- Difficulty 3: ~4,096 attempts average (000)
- Difficulty 4: ~65,536 attempts average (0000)
- Each additional difficulty multiplies work by 16x

---

### **4. Blockchain Core (`backend/blockchain/blockchain.py`)**

```python
class Blockchain:
    def __init__(self, difficulty=4, mining_reward=50):
        """
        The main blockchain data structure
        
        Components:
        - chain: List of all blocks (the blockchain itself)
        - pending_transactions: Pool of unconfirmed transactions
        - difficulty: How hard mining is (number of leading zeros)
        - mining_reward: Incentive for miners (50 G2C per block)
        """
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = difficulty
        self.mining_reward = mining_reward
```

**Genesis Block:**
```python
def create_genesis_block(self):
    """
    The first block in the chain (Block #0)
    - Has no previous hash (uses '0')
    - Contains a dummy transaction
    - Hardcoded and never changes
    - Foundation of the entire blockchain
    """
```

**Transaction Pool:**
```python
def add_transaction(self, transaction):
    """
    Adds a transaction to the pending pool (mempool)
    
    Validation checks:
    1. Is the signature valid?
    2. Does sender have sufficient balance?
    3. Is amount positive?
    
    If valid: Add to pool, waiting for miner
    If invalid: Reject transaction
    """
```

**Mining Process:**
```python
def mine_pending_transactions(self, mining_reward_address):
    """
    MINING WORKFLOW:
    
    1. Take all pending transactions
    2. Add a mining reward transaction (50 G2C to miner)
    3. Create new block with these transactions
    4. Perform proof-of-work (find valid nonce)
    5. Add block to chain
    6. Clear pending transactions pool
    7. Return the new block
    
    This is how:
    - Transactions get confirmed
    - New coins enter circulation
    - Miners get incentivized
    """
```

**Balance Calculation:**
```python
def get_balance(self, address):
    """
    Calculates balance by scanning entire blockchain
    
    Process:
    1. Start with balance = 0
    2. Loop through every block
    3. For each transaction:
       - If you're the sender: balance -= amount
       - If you're the recipient: balance += amount
    4. Return final balance
    
    Note: No "account" object stores your balance
    Balance is calculated from transaction history (UTXO model simplified)
    """
```

**Chain Validation:**
```python
def is_chain_valid(self):
    """
    Verifies blockchain integrity
    
    Checks:
    1. Each block's hash matches its calculated hash
    2. Each block's previous_hash matches the actual previous block
    3. All transactions in blocks are valid
    
    If ANY check fails: Chain is compromised
    This makes tampering virtually impossible
    """
```

---

### **5. Wallet System (`backend/wallet/wallet.py`)**

```python
class Wallet:
    def __init__(self):
        """
        Creates a cryptocurrency wallet
        
        Components:
        1. Private Key: Secret key (never share!)
        2. Public Key: Can be shared (like email address)
        3. Address: Shortened version of public key (easier to use)
        
        Generation process:
        - Generate random RSA key pair
        - Hash public key to create shorter address
        """
        self.private_key, self.public_key = generate_key_pair()
        self.address = self.generate_address()
```

**Address Generation:**
```python
def generate_address(self):
    """
    Creates a short wallet address from public key
    
    Process:
    1. Take public key (very long string)
    2. Hash it with SHA-256
    3. Take first 40 characters
    4. This becomes the wallet address
    
    Example:
    Public Key: -----BEGIN PUBLIC KEY----- ... (270 chars)
    Address: f42e8aeeee88ecf5a01a3b2c4d5e6f7a8b9c0d1e (40 chars)
    ```

---

### **6. Flask API Routes (`backend/api/routes.py`)**

**Blockchain Endpoints:**

```python
@api.route('/blockchain', methods=['GET'])
def get_blockchain():
    """
    Returns complete blockchain data
    
    Response includes:
    - All blocks with their transactions
    - Current difficulty
    - Pending transactions
    - Mining reward amount
    
    Used by: Dashboard, Blockchain Viewer
    """

@api.route('/blockchain/validate', methods=['GET'])
def validate_blockchain():
    """
    Checks if blockchain is valid
    
    Returns: {"valid": true/false}
    
    Used by: Dashboard to show chain status
    """
```

**Wallet Endpoints:**

```python
@api.route('/wallet/create', methods=['POST'])
def create_wallet():
    """
    Creates a new wallet with keys
    
    Process:
    1. Generate new Wallet object
    2. Store in server memory (wallets dict)
    3. Return wallet data to user
    
    Response includes:
    - address
    - public_key
    - private_key (WARNING: Save this!)
    """

@api.route('/wallet/<address>/balance', methods=['GET'])
def get_balance(address):
    """
    Calculates and returns wallet balance
    
    Parameters:
    - address: Wallet address to check
    
    Returns: {"address": "...", "balance": 150.5}
    """
```

**Transaction Endpoints:**

```python
@api.route('/transaction/create', methods=['POST'])
def create_transaction():
    """
    Creates and adds a new transaction
    
    Request body:
    {
        "sender": "public_key_here",
        "recipient": "address_here",
        "amount": 25.5,
        "private_key": "private_key_here"
    }
    
    Process:
    1. Validate all fields present
    2. Create Transaction object
    3. Sign with private key
    4. Validate signature and balance
    5. Add to pending pool
    6. Return confirmation
    """
```

**Mining Endpoints:**

```python
@api.route('/mine', methods=['POST'])
def mine_block():
    """
    Mines all pending transactions
    
    Request body:
    {
        "miner_address": "address_to_receive_reward"
    }
    
    Process:
    1. Call blockchain.mine_pending_transactions()
    2. Proof-of-work algorithm finds valid nonce
    3. Block added to chain
    4. Miner receives 50 G2C reward
    5. Return new block data
    """
```

---

### **7. Main Application (`backend/main.py`)**

```python
def create_app():
    """
    Application factory pattern
    
    Sets up:
    1. Flask app instance
    2. CORS (allows frontend on different port to connect)
    3. Creates blockchain instance
    4. Registers API routes
    
    Returns configured Flask app
    """
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize blockchain with settings
    blockchain = Blockchain(difficulty=4, mining_reward=50)
    
    # Connect blockchain to API routes
    init_routes(blockchain)
    
    # Register routes under /api prefix
    app.register_blueprint(api, url_prefix='/api')
    
    return app
```

---

## **FRONTEND ARCHITECTURE**

### **1. API Service Layer (`frontend/src/services/api.js`)**

```javascript
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**Purpose:** Centralizes all HTTP requests to backend

**API Organization:**
- `blockchainAPI`: Blockchain operations
- `walletAPI`: Wallet management
- `transactionAPI`: Transaction creation
- `miningAPI`: Mining operations

**Example:**
```javascript
export const walletAPI = {
  createWallet: () => api.post('/wallet/create'),
  getBalance: (address) => api.get(`/wallet/${address}/balance`),
  getTransactions: (address) => api.get(`/wallet/${address}/transactions`),
};
```

---

### **2. Main App Component (`frontend/src/App.jsx`)**

```javascript
function App() {
  // Global state management
  const [currentView, setCurrentView] = useState('dashboard');
  const [wallet, setWallet] = useState(null);  // Persists across navigation

  const renderView = () => {
    // Renders different components based on navigation
    switch (currentView) {
      case 'dashboard': return <Dashboard />;
      case 'wallet': return <Wallet wallet={wallet} setWallet={setWallet} />;
      // ... etc
    }
  };
```

**State Management:**
- `currentView`: Which tab is active (dashboard, wallet, transactions, etc.)
- `wallet`: Global wallet object shared across components

**Why lift state up?**
- Wallet persists when navigating between pages
- Mining and Transactions can access wallet data
- Prevents losing wallet on navigation

---

### **3. Header Component (`frontend/src/components/Header.jsx`)**

```javascript
function Header({ currentView, setCurrentView }) {
  return (
    <header className="header">
      <div className="header-title">
        <h1>Group2Coin</h1>
      </div>
      
      <nav className="header-nav">
        <button
          className={`nav-button ${currentView === 'dashboard' ? 'active' : ''}`}
          onClick={() => setCurrentView('dashboard')}
        >
          Dashboard
        </button>
        // ... more buttons
      </nav>
    </header>
  );
}
```

**Features:**
- Navigation buttons
- Active state highlighting
- Responsive layout

---

### **4. Dashboard Component (`frontend/src/components/Dashboard.jsx`)**

```javascript
function Dashboard() {
  const [stats, setStats] = useState({
    totalBlocks: 0,
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