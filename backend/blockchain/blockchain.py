"""
Blockchain class managing the entire chain and transaction pool
"""
from blockchain.block import Block
from blockchain.transaction import Transaction
from utils.database import Database

class Blockchain:
    """
    Main blockchain class managing chain, pending transactions, and mining
    """
    
    def __init__(self, difficulty=4, mining_reward=50):
        """
        Initialize blockchain with database connection
        Args:
            difficulty: Mining difficulty (number of leading zeros)
            mining_reward: Reward for mining a block in Group2Coin
        """
        self.db = Database()
        self.difficulty = difficulty
        self.mining_reward = mining_reward
        self.pending_transactions = []
        
        # Initialize chain
        last_block = self.db.get_last_block()
        if not last_block:
            self.create_genesis_block()
        
        # We don't load the full chain into memory anymore to save RAM
        # But we can keep a cache if needed. For now, we trust the DB.
        
    def create_genesis_block(self):
        """
        Create the first block in the blockchain
        """
        # Genesis transaction
        # NOTE: Genesis uses hardcoded strings, handled specially in DB save logic
        genesis_transaction = Transaction(
            sender_address='GENESIS', 
            recipient='GENESIS', 
            amount=0,
            public_key='GENESIS_KEY'
        )
        
        genesis_block = Block(0, [genesis_transaction], '0')
        self.db.save_block(genesis_block)
    
    def get_latest_block(self):
        """
        Get the most recent block in the chain
        """
        block_data = self.db.get_last_block()
        if not block_data:
            return None # Should not happen if init called create_genesis_block
            
        # Reconstruct Block object from DB data
        import json
        transactions_data = json.loads(block_data['transactions_json'])
        transactions = []
        for tx_data in transactions_data:
            # Reconstruct Transaction object
            tx = Transaction(
                sender_address=tx_data['sender'],
                recipient=tx_data['recipient'],
                amount=tx_data['amount'],
                public_key=tx_data.get('public_key'),
                signature=tx_data['signature'],
                timestamp=tx_data['timestamp'],
                nonce=tx_data.get('nonce')
            )
            transactions.append(tx)
            
        return Block(
            index=block_data['block_index'],
            transactions=transactions,
            previous_hash=block_data['previous_hash'],
            timestamp=block_data['timestamp'],
            nonce=block_data['nonce']
        )
    
    def add_transaction(self, transaction):
        """
        Add a transaction to pending transactions pool
        Returns:
            Boolean indicating success
        """
        if not transaction.is_valid():
            print("Transaction invalid signature")
            return False
        
        # Calculate available balance (Confirmed - Pending Spends)
        current_balance = self.get_balance(transaction.sender)
        
        pending_spend = 0
        for tx in self.pending_transactions:
            if tx.sender == transaction.sender:
                pending_spend += tx.amount
                
        if transaction.sender != 'MINING_REWARD' and (current_balance - pending_spend) < transaction.amount:
            print(f"Insufficient balance: {current_balance} - pending {pending_spend} < {transaction.amount}")
            return False
        
        self.pending_transactions.append(transaction)
        return True
    
    def mine_pending_transactions(self, mining_reward_address):
        """
        Mine all pending transactions into a new block
        """
        # Add reward transaction
        # NO public key for mining reward, handled in Transaction validation
        reward_transaction = Transaction(
            sender_address='MINING_REWARD', 
            recipient=mining_reward_address, 
            amount=self.mining_reward
        )
        self.pending_transactions.append(reward_transaction)
        
        latest_block = self.get_latest_block()
        
        new_block = Block(
            index=latest_block.index + 1,
            transactions=self.pending_transactions,
            previous_hash=latest_block.hash
        )
        
        new_block.mine_block(self.difficulty)
        
        # Save to persistence
        success = self.db.save_block(new_block)
        
        if success:
            self.pending_transactions = []
            return new_block
        else:
            print("Failed to save block")
            return None
    
    def get_balance(self, address):
        """
        Calculate balance for a given wallet address using DB
        """
        return self.db.get_balance(address)
    
    def is_chain_valid(self):
        """
        Verify integrity of the entire blockchain
        """
        # Loading entire chain to verify
        chain_data = self.db.get_chain()
        
        # Reconstruct full chain objects (expensive, but needed for full validation)
        # In production this should be optimized
        import json
        
        for i in range(1, len(chain_data)):
            current_data = chain_data[i]
            previous_data = chain_data[i - 1]
            
            # Reconstruct Block
            # ... (Simplification: Just check hashes for now to save complexity in this view)
            
            if current_data['previous_hash'] != previous_data['hash']:
                return False
                
            # TODO: extensive verification of every tx signature
            
        return True
    
    @property
    def chain(self):
        """
        Emulator for .chain property to keep compatibility with some API views
        that might iterate over blockchain.chain.
        WARNING: Loads entire chain into memory.
        """
        chain_data = self.db.get_chain()
        blocks = []
        import json
        
        for block_data in chain_data:
            transactions_data = json.loads(block_data['transactions_json'])
            transactions = []
            for tx_data in transactions_data:
                tx = Transaction(
                    sender_address=tx_data['sender'],
                    recipient=tx_data['recipient'],
                    amount=tx_data['amount'],
                    public_key=tx_data.get('public_key'),
                    signature=tx_data['signature'],
                    timestamp=tx_data['timestamp'],
                    nonce=tx_data.get('nonce')
                )
                transactions.append(tx)
                
            blocks.append(Block(
                index=block_data['block_index'],
                transactions=transactions,
                previous_hash=block_data['previous_hash'],
                timestamp=block_data['timestamp'],
                nonce=block_data['nonce']
            ))
        return blocks

    def to_dict(self):
        """
        Convert blockchain status to dictionary
        """
        chain = self.chain # Triggers load
        return {
            'chain': [block.to_dict() for block in chain],
            'difficulty': self.difficulty,
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions],
            'mining_reward': self.mining_reward
        }
