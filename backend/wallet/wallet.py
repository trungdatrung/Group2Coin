"""
Wallet class for managing user cryptocurrency wallets
"""
from utils.crypto import generate_key_pair, calculate_hash


class Wallet:
    """
    Cryptocurrency wallet with public-private key pair
    """
    
    def __init__(self):
        """
        Initialize wallet with new key pair
        """
        self.private_key, self.public_key = generate_key_pair()
        self.address = self.generate_address()
    
    def generate_address(self):
        """
        Generate wallet address from public key
        Returns:
            Wallet address (shortened hash of public key)
        """
        return calculate_hash(self.public_key)[:40]
    
    def to_dict(self):
        """
        Convert wallet to dictionary
        Returns:
            Dictionary with wallet information
        """
        return {
            'address': self.address,
            'public_key': self.public_key,
            'private_key': self.private_key
        }
