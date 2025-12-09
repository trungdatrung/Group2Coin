"""
Supply Chain Transaction class for recording supply chain events on the blockchain
"""
import time
import json
from blockchain.transaction import Transaction


class SupplyChainTransaction(Transaction):
    """
    Special transaction type for supply chain events.
    Extends the base Transaction class to include supply chain metadata.
    Amount is always 0 as these are data transactions, not financial.
    """
    
    def __init__(self, event_type, product_data, signature=None, timestamp=None):
        """
        Initialize a supply chain transaction
        
        Args:
            event_type: Type of supply chain event (register_product, add_event, quality_alert)
            product_data: Dictionary containing product/event information
            signature: Digital signature (system-signed)
            timestamp: Transaction timestamp
        """
        # Supply chain transactions use special sender/recipient format
        sender = f"SUPPLY_CHAIN:{event_type}"
        recipient = f"PRODUCT:{product_data.get('product_id', 'UNKNOWN')}"
        
        # Initialize base transaction with amount=0 (data transaction)
        super().__init__(sender, recipient, 0, signature, timestamp)
        
        self.event_type = event_type
        self.product_data = product_data
    
    def to_dict(self):
        """
        Convert supply chain transaction to dictionary
        
        Returns:
            Dictionary representation including supply chain data
        """
        base_dict = super().to_dict()
        base_dict.update({
            'transaction_type': 'supply_chain',
            'event_type': self.event_type,
            'product_data': self.product_data
        })
        return base_dict
    
    def calculate_hash(self):
        """
        Calculate hash including supply chain data
        
        Returns:
            Transaction hash
        """
        from utils.crypto import calculate_hash
        
        transaction_data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'product_data': self.product_data
        }
        return calculate_hash(transaction_data)
    
    def is_valid(self):
        """
        Verify supply chain transaction validity
        Supply chain transactions are system-generated and always valid
        
        Returns:
            Boolean indicating if transaction is valid
        """
        # Supply chain transactions are system-signed, always valid
        return True
    
    @staticmethod
    def create_product_registration(product):
        """
        Create a transaction for product registration
        
        Args:
            product: Product instance
            
        Returns:
            SupplyChainTransaction instance
        """
        product_data = {
            'product_id': product.product_id,
            'name': product.name,
            'category': product.category,
            'manufacturer': product.manufacturer,
            'manufacture_date': product.manufacture_date,
            'batch_number': product.batch_number,
            'initial_location': product.initial_location,
            'product_hash': product.product_hash,
            'metadata': product.metadata
        }
        
        return SupplyChainTransaction('register_product', product_data)
    
    @staticmethod
    def create_tracking_event(product_id, event):
        """
        Create a transaction for a tracking event
        
        Args:
            product_id: Product identifier
            event: SupplyChainEvent instance
            
        Returns:
            SupplyChainTransaction instance
        """
        event_data = {
            'product_id': product_id,
            'event_type': event.event_type,
            'location': event.location,
            'handler': event.handler,
            'description': event.description,
            'event_hash': event.event_hash,
            'metadata': event.metadata
        }
        
        return SupplyChainTransaction('add_event', event_data)
