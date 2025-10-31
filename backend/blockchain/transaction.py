"""
Transaction class for handling cryptocurrency transactions
"""
import time
from utils.crypto import calculate_hash, sign_data, verify_signature


class Transaction:
    """
    Represents a transaction in the blockchain
    """
    
    def __init__(self, sender, recipient, amount, signature=None, timestamp=None):
        """
        Initialize a transaction
        Args:
            sender: Public key of sender (or 'MINING_REWARD' for mining rewards)
            recipient: Public key of recipient
            amount: Amount of Group2Coin to transfer
            signature: Digital signature of transaction
            timestamp: Transaction timestamp
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
        self.timestamp = timestamp or time.time()
    
    def to_dict(self):
        """
        Convert transaction to dictionary
        Returns:
            Dictionary representation of transaction
        """
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'signature': self.signature
        }
    
    def calculate_hash(self):
        """
        Calculate hash of transaction (excluding signature)
        Returns:
            Transaction hash
        """
        transaction_data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
        return calculate_hash(transaction_data)
    
    def sign_transaction(self, private_key):
        """
        Sign the transaction with private key
        Args:
            private_key: Private key in PEM format
        """
        if self.sender == 'MINING_REWARD':
            return
        
        transaction_data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
        
        self.signature = sign_data(private_key, transaction_data)
    
    def is_valid(self):
        """
        Verify transaction signature and validity
        Returns:
            Boolean indicating if transaction is valid
        """
        if self.sender == 'MINING_REWARD':
            return True
        
        if not self.signature:
            return False
        
        transaction_data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp
        }
        
        return verify_signature(self.sender, transaction_data, self.signature)
