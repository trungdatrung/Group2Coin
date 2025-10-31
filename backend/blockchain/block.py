"""
Block class representing a single block in the blockchain
"""
import time
from utils.crypto import calculate_hash


class Block:
    """
    Represents a single block in the blockchain
    """
    
    def __init__(self, index, transactions, previous_hash, timestamp=None, nonce=0):
        """
        Initialize a block
        Args:
            index: Block number in the chain
            transactions: List of Transaction objects
            previous_hash: Hash of the previous block
            timestamp: Block creation timestamp
            nonce: Proof of work nonce
        """
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """
        Calculate SHA-256 hash of the block
        Returns:
            Block hash as hexadecimal string
        """
        block_data = {
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }
        return calculate_hash(block_data)
    
    def mine_block(self, difficulty):
        """
        Mine the block using proof of work algorithm
        Args:
            difficulty: Number of leading zeros required in hash
        """
        target = '0' * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        print(f"Block mined: {self.hash}")
    
    def to_dict(self):
        """
        Convert block to dictionary
        Returns:
            Dictionary representation of block
        """
        return {
            'index': self.index,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'hash': self.hash
        }
