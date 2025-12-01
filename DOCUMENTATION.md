# Group2Coin Complete Technical Documentation

## Table of Contents
1. [Algorithms and Implementation](#algorithms-and-implementation)
2. [Code Structure](#code-structure)
3. [Function Reference](#function-reference)
4. [Data Flow](#data-flow)

---

## Algorithms and Implementation

### 1. SHA-256 Hashing Algorithm

**Purpose**: Creates unique, irreversible fingerprints of data

**Implementation**:
```python
def calculate_hash(data):
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()
```

**Mathematical Properties**:
- Output length: Always 256 bits (64 hexadecimal characters)
- Deterministic: Same input always produces same output
- Avalanche effect: One bit change in input changes ~50% of output bits
- Pre-image resistance: Cannot find input from hash
- Collision resistance: Probability of two inputs having same hash is 1/2^256

**Use Cases in Project**:
- Block hashing: Creates unique block identifier
- Transaction hashing: Ensures transaction integrity
- Address generation: Derives wallet address from public key
- Product authentication: Generates anti-counterfeit fingerprints

### 2. Proof-of-Work Mining Algorithm

**Purpose**: Secures blockchain by requiring computational work

**Pseudocode**:
```
function mine_block(block, difficulty):
    target = string of 'difficulty' zeros
    nonce = 0
    
    loop:
        block.nonce = nonce
        hash = SHA256(block_data + nonce)
        
        if hash starts with target:
            block.hash = hash
            return block  // Success
        
        nonce = nonce + 1  // Try next value
```

**Complexity Analysis**:
- Average attempts needed: 16^difficulty
- Difficulty 1: ~16 attempts
- Difficulty 2: ~256 attempts  
- Difficulty 3: ~4,096 attempts
- Difficulty 4: ~65,536 attempts
- Time complexity: O(16^n) where n is difficulty

**Security Analysis**:
```
To alter block at position k in chain of length n:
1. Must recalculate block k hash (16^d attempts)
2. Must recalculate blocks k+1 through n (16^d × (n-k) attempts)
3. Must outpace honest network adding new blocks
4. Total work: exponential in difficulty and chain length
```

### 3. RSA Digital Signature Algorithm

**Key Generation**:
```python
def generate_key_pair():
    # Generate random prime numbers p and q
    # Calculate n = p × q (modulus)
    # Calculate φ(n) = (p-1) × (q-1)
    # Choose public exponent e = 65537
    # Calculate private exponent d = e^-1 mod φ(n)
    # Public key: (n, e)
    # Private key: (n, d)
```

**Signing Process**:
```
1. Create transaction data: T
2. Hash transaction: H = SHA256(T)
3. Sign hash: S = H^d mod n  (using private key d)
4. Attach signature S to transaction
```

**Verification Process**:
```
1. Receive transaction T with signature S
2. Calculate hash: H = SHA256(T)
3. Decrypt signature: H' = S^e mod n  (using public key e)
4. Compare H == H'
5. If equal: signature valid, transaction authentic
```

**Security Properties**:
- Key size: 2048 bits provides ~112-bit security level
- RSA problem: Factoring n = p × q is computationally hard
- Signing: Only holder of private key d can create valid signature
- Verification: Anyone with public key (n, e) can verify

**Attack Resistance**:
- Brute force: 2^2048 possible keys (computationally infeasible)
- Factorization: Best known algorithms are sub-exponential but still impractical for 2048-bit keys
- Chosen plaintext: OAEP padding prevents attacks
- Signature forgery: Requires solving RSA problem

### 4. Balance Calculation Algorithm

**UTXO-Inspired Implementation**:
```python
def get_balance(address):
    balance = 0.0
    
    for block in blockchain.chain:
        for transaction in block.transactions:
            # Subtract outgoing transactions
            if transaction.sender == address:
                balance -= transaction.amount
            
            # Add incoming transactions
            if transaction.recipient == address:
                balance += transaction.amount
    
    return balance
```

**Optimization Techniques**:

1. **Caching**:
```python
# Cache balances after each block
balance_cache = {}

def update_cache_for_block(block):
    for tx in block.transactions:
        balance_cache[tx.sender] -= tx.amount
        balance_cache[tx.recipient] += tx.amount
```

2. **Incremental Updates**:
```python
# Only process new blocks since last query
def get_balance_optimized(address, last_cached_block):
    balance = balance_cache.get(address, 0)
    
    for block in blockchain.chain[last_cached_block + 1:]:
        for tx in block.transactions:
            if tx.sender == address:
                balance -= tx.amount
            if tx.recipient == address:
                balance += tx.amount
    
    return balance
```

**Complexity**:
- Naive: O(B × T) where B = blocks, T = transactions per block
- Cached: O(1) for read, O(T) for update
- Space: O(A) where A = number of addresses

### 5. Blockchain Validation Algorithm

**Complete Validation Process**:
```python
def is_chain_valid():
    # Step 1: Validate genesis block
    genesis = chain[0]
    if genesis.hash != genesis.calculate_hash():
        return False
    if genesis.previous_hash != "0":
        return False
    
    # Step 2: Validate each subsequent block
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i-1]
        
        # Check hash integrity
        if current.hash != current.calculate_hash():
            return False
        
        # Check chain linkage
        if current.previous_hash != previous.hash:
            return False
        
        # Check proof-of-work
        if not current.hash.startswith('0' * difficulty):
            return False
        
        # Check timestamp ordering
        if current.timestamp < previous.timestamp:
            return False
        
        # Validate all transactions
        for tx in current.transactions:
            if not tx.is_valid():
                return False
            
            # Check sender has sufficient balance
            balance = get_balance_at_block(tx.sender, i-1)
            if balance < tx.amount:
                return False
    
    return True
```

**Validation Levels**:

Level 1 - **Hash Integrity**:
```
Verify: hash(block_data) == stored_hash
Detects: Data corruption, tampering
```

Level 2 - **Chain Continuity**:
```
Verify: block[i].previous_hash == block[i-1].hash
Detects: Missing blocks, reordering
```

Level 3 - **Proof-of-Work**:
```
Verify: hash starts with required zeros
Detects: Invalid mining, insufficient work
```

Level 4 - **Transaction Validity**:
```
Verify: signatures, balances, double-spends
Detects: Fraudulent transactions
```

### 6. Supply Chain Event Tracking

**Event Hash Generation**:
```python
def generate_event_hash(event):
    event_data = {
        'product_id': event.product_id,
        'event_type': event.event_type,
        'location': event.location,
        'handler': event.handler,
        'timestamp': event.timestamp,
        'metadata': event.metadata
    }
    
    # Sort keys for deterministic hashing
    canonical_data = json.dumps(event_data, sort_keys=True)
    
    # Generate SHA-256 hash
    return hashlib.sha256(canonical_data.encode()).hexdigest()
```

**Product Authentication**:
```python
def verify_product_authenticity(product_id, claimed_hash):
    # Retrieve product from blockchain
    product = get_product(product_id)
    
    if not product:
        return False  # Product not registered
    
    # Regenerate hash from product data
    product_data = {
        'product_id': product.product_id,
        'name': product.name,
        'manufacturer': product.manufacturer,
        'manufacture_date': product.manufacture_date,
        'batch_number': product.batch_number,
        'registration_timestamp': product.registration_timestamp
    }
    
    actual_hash = calculate_hash(product_data)
    
    # Compare hashes
    return actual_hash == claimed_hash
```

**Event Chain Validation**:
```python
def validate_event_chain(product):
    previous_timestamp = product.registration_timestamp
    
    for event in product.events:
        # Verify event hash
        if event.event_hash != event._generate_event_hash():
            return False
        
        # Verify temporal ordering
        if event.timestamp < previous_timestamp:
            return False
        
        # Verify event belongs to product
        if event.product_id != product.product_id:
            return False
        
        previous_timestamp = event.timestamp
    
    return True
```

---

## Code Structure

### Backend Architecture

#### 1. Crypto Module (`backend/utils/crypto.py`)

**Functions**:

```python
def calculate_hash(data: Union[dict, str]) -> str:
    """
    Calculates SHA-256 hash of input data.
    
    Args:
        data: Dictionary or string to hash
    
    Returns:
        64-character hexadecimal hash string
    
    Example:
        >>> calculate_hash({'key': 'value'})
        '3a7bd3e2360a3d29eea436fcfb7e44c735d117c42d1c1835420b6b9942dd4f1b'
    """

def generate_key_pair() -> Tuple[str, str]:
    """
    Generates RSA-2048 key pair.
    
    Returns:
        Tuple of (private_key_pem, public_key_pem)
    
    Security:
        - 2048-bit key size
        - PKCS1 format
        - PEM encoding
    """

def sign_data(private_key_pem: str, data: str) -> str:
    """
    Creates digital signature using RSA private key.
    
    Args:
        private_key_pem: Private key in PEM format
        data: Data to sign
    
    Returns:
        Base64-encoded signature
    
    Process:
        1. Load private key from PEM
        2. Hash data with SHA-256
        3. Sign hash with PSS padding
        4. Encode signature as base64
    """

def verify_signature(public_key_pem: str, data: str, signature: str) -> bool:
    """
    Verifies digital signature using RSA public key.
    
    Args:
        public_key_pem: Public key in PEM format
        data: Original data
        signature: Base64-encoded signature
    
    Returns:
        True if signature valid, False otherwise
    """
```

#### 2. Block Class (`backend/blockchain/block.py`)

**Attributes**:
```python
class Block:
    index: int                    # Position in blockchain
    timestamp: float              # Unix timestamp
    transactions: List[Transaction]  # List of transactions
    previous_hash: str            # Hash of previous block
    nonce: int                    # Proof-of-work counter
    hash: str                     # This block's hash
```

**Methods**:
```python
def __init__(self, index, timestamp, transactions, previous_hash):
    """Initializes block with data, calculates initial hash"""

def calculate_hash(self) -> str:
    """
    Calculates SHA-256 hash of block data.
    
    Includes: index, timestamp, transactions, previous_hash, nonce
    
    Returns:
        Block hash string
    """

def mine_block(self, difficulty: int):
    """
    Performs proof-of-work to find valid hash.
    
    Args:
        difficulty: Number of leading zeros required
    
    Process:
        1. Set target pattern (e.g., "0000" for difficulty=4)
        2. Increment nonce
        3. Calculate hash
        4. Check if hash meets target
        5. Repeat until valid hash found
    
    Modifies:
        self.nonce: Updated to winning value
        self.hash: Updated to valid hash
    """
```

#### 3. Transaction Class (`backend/blockchain/transaction.py`)

**Attributes**:
```python
class Transaction:
    sender: str        # Sender's public key
    recipient: str     # Recipient's address
    amount: float      # Transaction amount
    timestamp: float   # Creation time
    signature: str     # Digital signature
```

**Methods**:
```python
def __init__(self, sender, recipient, amount):
    """Initializes transaction without signature"""

def calculate_hash(self) -> str:
    """Hashes transaction data for signing"""

def sign_transaction(self, private_key_pem: str):
    """
    Signs transaction with private key.
    
    Args:
        private_key_pem: Sender's private key
    
    Process:
        1. Calculate transaction hash
        2. Sign hash with private key
        3. Store signature in transaction
    
    Raises:
        Exception: If transaction is mining reward
    """

def is_valid(self) -> bool:
    """
    Validates transaction signature.
    
    Returns:
        True if signature valid or mining reward
        False if signature invalid
    
    Checks:
        - Mining rewards always valid (sender == "MINING_REWARD")
        - Signature verifies with sender's public key
    """
```

#### 4. Blockchain Class (`backend/blockchain/blockchain.py`)

**Attributes**:
```python
class Blockchain:
    chain: List[Block]                    # List of blocks
    difficulty: int                       # Mining difficulty
    pending_transactions: List[Transaction]  # Unconfirmed transactions
    mining_reward: float                  # Block reward amount
```

**Methods**:
```python
def __init__(self, difficulty=4, mining_reward=50):
    """
    Initializes blockchain with genesis block.
    
    Args:
        difficulty: Proof-of-work difficulty (default 4)
        mining_reward: Mining reward amount (default 50)
    """

def create_genesis_block() -> Block:
    """
    Creates first block in chain.
    
    Returns:
        Genesis block with:
        - index: 0
        - previous_hash: "0"
        - Empty transactions list
    """

def get_latest_block() -> Block:
    """Returns most recent block in chain"""

def add_transaction(self, transaction: Transaction):
    """
    Adds transaction to pending pool.
    
    Args:
        transaction: Validated transaction
    
    Validates:
        - Transaction signature valid
        - Sender has sufficient balance
    
    Raises:
        Exception: If validation fails
    """

def mine_pending_transactions(self, miner_address: str) -> Block:
    """
    Mines pending transactions into new block.
    
    Args:
        miner_address: Address to receive mining reward
    
    Process:
        1. Create reward transaction
        2. Add pending transactions to block
        3. Mine block (proof-of-work)
        4. Add block to chain
        5. Clear pending transactions
        6. Create new reward transaction for next block
    
    Returns:
        Newly mined block
    """

def get_balance(self, address: str) -> float:
    """
    Calculates balance for address.
    
    Args:
        address: Wallet address
    
    Returns:
        Current balance
    
    Algorithm:
        Sums all received transactions
        Subtracts all sent transactions
    """

def is_chain_valid(self) -> bool:
    """
    Validates entire blockchain.
    
    Returns:
        True if valid, False if tampering detected
    
    Checks:
        - Hash integrity
        - Chain linkage
        - Proof-of-work
        - Transaction validity
    """
```

#### 5. Product Class (`backend/blockchain/product.py`)

**Attributes**:
```python
class Product:
    product_id: str           # Unique identifier
    name: str                 # Product name
    category: str             # Product category
    manufacturer: str         # Manufacturing company
    manufacture_date: str     # Date of manufacture
    batch_number: str         # Manufacturing batch
    initial_location: str     # Origin location
    metadata: dict            # Additional data
    registration_timestamp: float  # Registration time
    events: List[SupplyChainEvent]  # Tracking events
    product_hash: str         # Authentication hash
```

**Methods**:
```python
def _generate_product_hash(self) -> str:
    """
    Generates unique authentication hash.
    
    Returns:
        SHA-256 hash of product details
    
    Purpose:
        - Prevents counterfeiting
        - Enables authenticity verification
        - Immutable after creation
    """

def add_event(self, event: SupplyChainEvent):
    """Appends tracking event to product history"""

def verify_authenticity(self, claimed_hash: str) -> bool:
    """
    Verifies product is authentic.
    
    Args:
        claimed_hash: Hash to verify
    
    Returns:
        True if authentic, False if counterfeit
    """

def check_safety_alerts(self) -> List[dict]:
    """
    Returns all safety alerts for product.
    
    Returns:
        List of alerts with severity and description
    """

def get_full_history(self) -> List[dict]:
    """Returns complete tracking event history"""
```

#### 6. API Routes (`backend/api/routes.py`)

**Blockchain Routes**:
```python
GET /api/blockchain
    Returns complete blockchain data
    
GET /api/blockchain/validate
    Validates blockchain integrity
    
GET /api/blockchain/pending
    Returns pending transactions
```

**Wallet Routes**:
```python
POST /api/wallet/create
    Creates new wallet
    Returns: {address, public_key, private_key}
    
GET /api/wallet/<address>/balance
    Returns balance for address
    
POST /api/wallet/import
    Imports wallet from JSON data
```

**Transaction Routes**:
```python
POST /api/transaction/create
    Creates and signs transaction
    Body: {sender, recipient, amount, private_key}
```

**Mining Routes**:
```python
POST /api/mine
    Mines pending transactions
    Body: {miner_address}
```

**Supply Chain Routes**:
```python
POST /api/supplychain/product/register
    Registers new product
    
POST /api/supplychain/product/<id>/event
    Adds tracking event
    
GET /api/supplychain/product/<id>
    Returns product details and history
    
POST /api/supplychain/product/<id>/verify
    Verifies product authenticity
```

---

## Function Reference

### Utility Functions

```python
calculate_hash(data)
    Purpose: SHA-256 hashing
    Input: dict or string
    Output: 64-char hex string
    Time: O(n) where n = data size

generate_key_pair()
    Purpose: RSA key generation
    Input: None
    Output: (private_key, public_key)
    Time: O(k^2) where k = key size

sign_data(private_key, data)
    Purpose: Digital signature
    Input: PEM key, string data
    Output: base64 signature
    Time: O(k^2)

verify_signature(public_key, data, signature)
    Purpose: Signature verification
    Input: PEM key, data, signature
    Output: boolean
    Time: O(k^2)
```

### Core Blockchain Functions

```python
Block.mine_block(difficulty)
    Purpose: Proof-of-work mining
    Input: difficulty level
    Output: None (modifies block)
    Expected iterations: 16^difficulty
    Time: O(16^d) probabilistic

Blockchain.add_transaction(transaction)
    Purpose: Add to pending pool
    Input: Transaction object
    Output: None
    Validates: signature, balance
    Time: O(B×T) for balance check

Blockchain.mine_pending_transactions(miner_address)
    Purpose: Mine new block
    Input: miner address string
    Output: Block object
    Time: O(16^d) for mining
    
Blockchain.get_balance(address)
    Purpose: Calculate balance
    Input: address string
    Output: float balance
    Time: O(B×T) naive, O(1) cached

Blockchain.is_chain_valid()
    Purpose: Validate integrity
    Input: None
    Output: boolean
    Time: O(B×T×V) where V = verification time
```

### Supply Chain Functions

```python
Product._generate_product_hash()
    Purpose: Create authentication hash
    Input: None (uses instance data)
    Output: hash string
    Time: O(1)

Product.verify_authenticity(claimed_hash)
    Purpose: Verify product genuine
    Input: hash string
    Output: boolean
    Time: O(1)

SupplyChainEvent._generate_event_hash()
    Purpose: Create event hash
    Input: None (uses instance data)
    Output: hash string
    Time: O(1)

SupplyChainManager.register_product(...)
    Purpose: Register new product
    Input: product details
    Output: Product object
    Time: O(1)

SupplyChainManager.add_event_to_product(...)
    Purpose: Add tracking event
    Input: product_id, event details
    Output: SupplyChainEvent object
    Time: O(1)
```

---

## Data Flow

### Complete Transaction Flow

```
1. USER ACTION: Create wallet
   Frontend: Click "Create Wallet"
   ↓
   API Call: POST /api/wallet/create
   ↓
   Backend: generate_key_pair()
   Backend: Create Wallet(private_key, public_key)
   Backend: Calculate address = hash(public_key)
   ↓
   Response: {address, public_key, private_key}
   ↓
   Frontend: Display wallet, store in state
   User: Save private key securely

2. USER ACTION: Mine coins
   Frontend: Enter address, click "Mine"
   ↓
   API Call: POST /api/mine {miner_address}
   ↓
   Backend: Create reward transaction
   Backend: Create new Block
   Backend: mine_block(difficulty) → Find valid nonce
   Backend: Add block to chain
   Backend: Clear pending transactions
   ↓
   Response: {block details}
   ↓
   Frontend: Show success
   Result: Miner has +50 G2C

3. USER ACTION: Send transaction
   Frontend: Fill form (recipient, amount)
   Frontend: Get keys from wallet state
   ↓
   API Call: POST /api/transaction/create
   Body: {sender_public_key, recipient, amount, private_key}
   ↓
   Backend: Create Transaction
   Backend: sign_transaction(private_key)
   Backend: is_valid() → Verify signature
   Backend: Check balance sufficient
   Backend: add_transaction() → Add to pending
   ↓
   Response: {transaction details}
   ↓
   Frontend: Show confirmation
   Result: Transaction pending

4. USER ACTION: Mine pending transactions
   Frontend: Click "Mine"
   ↓
   API Call: POST /api/mine
   ↓
   Backend: Include pending transaction in block
   Backend: mine_block() → Proof-of-work
   Backend: Add block to chain
   Backend: Update balances
   ↓
   Response: {block details}
   ↓
   Frontend: Show success
   Result: Transaction confirmed
   Sender: -amount
   Recipient: +amount
   Miner: +50 G2C
```

### Supply Chain Product Flow

```
1. REGISTER PRODUCT
   Frontend: Fill registration form
   ↓
   API Call: POST /api/supplychain/product/register
   Body: {product_id, name, manufacturer, ...}
   ↓
   Backend: Create Product object
   Backend: _generate_product_hash()
   Backend: Store in supply_chain_manager
   ↓
   Response: {product details with hash}
   ↓
   Frontend: Display product with QR code
   Physical: Print hash on product label

2. TRACK PRODUCT
   Frontend: Select product, fill event form
   ↓
   API Call: POST /api/supplychain/product/<id>/event
   Body: {event_type, location, handler, metadata}
   ↓
   Backend: Create SupplyChainEvent
   Backend: _generate_event_hash()
   Backend: product.add_event(event)
   ↓
   Response: {event details}
   ↓
   Frontend: Update timeline display
   Result: Event recorded on blockchain

3. VERIFY AUTHENTICITY
   User: Scan product QR code → Get hash
   Frontend: Enter product_id and hash
   ↓
   API Call: POST /api/supplychain/product/<id>/verify
   Body: {product_hash}
   ↓
   Backend: Get product from blockchain
   Backend: Compare claimed_hash with product.product_hash
   ↓
   Response: {authentic: true/false, message}
   ↓
   Frontend: Display verification result
   Result: Consumer knows if product genuine
```

---

This documentation provides comprehensive technical details for understanding, maintaining, and extending the Group2Coin blockchain platform.
