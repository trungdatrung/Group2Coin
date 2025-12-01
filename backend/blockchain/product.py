"""
Product and Supply Chain Event classes for blockchain-based supply chain management.
Provides functionality for product tracking, authenticity verification, and supply chain transparency.
"""
import hashlib
import json
import time
from typing import Dict, List, Optional, Any


class Product:
    """
    Represents a product in the supply chain with complete tracking information.
    Each product has a unique ID and tracks its journey from origin to consumer.
    """
    
    def __init__(
        self,
        product_id: str,
        name: str,
        category: str,
        manufacturer: str,
        manufacture_date: str,
        batch_number: str,
        initial_location: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new product for supply chain tracking.
        
        Args:
            product_id: Unique identifier for the product
            name: Product name/description
            category: Product category (food, pharmaceutical, electronics, etc.)
            manufacturer: Name of the manufacturing entity
            manufacture_date: Date of manufacture (ISO format)
            batch_number: Manufacturing batch number for recall purposes
            initial_location: Starting location in the supply chain
            metadata: Additional product information (specifications, certifications, etc.)
        """
        self.product_id = product_id
        self.name = name
        self.category = category
        self.manufacturer = manufacturer
        self.manufacture_date = manufacture_date
        self.batch_number = batch_number
        self.initial_location = initial_location
        self.metadata = metadata or {}
        self.registration_timestamp = time.time()
        self.events: List[SupplyChainEvent] = []
        
        # Generate a unique product hash for authenticity verification
        self.product_hash = self._generate_product_hash()
    
    def _generate_product_hash(self) -> str:
        """
        Generate a unique hash for product authenticity verification.
        This hash acts as a digital fingerprint to prevent counterfeiting.
        
        Returns:
            SHA-256 hash of product details
        """
        product_string = json.dumps({
            'product_id': self.product_id,
            'name': self.name,
            'manufacturer': self.manufacturer,
            'manufacture_date': self.manufacture_date,
            'batch_number': self.batch_number,
            'timestamp': self.registration_timestamp
        }, sort_keys=True)
        
        return hashlib.sha256(product_string.encode()).hexdigest()
    
    def add_event(self, event: 'SupplyChainEvent') -> None:
        """
        Add a supply chain event to the product's history.
        
        Args:
            event: SupplyChainEvent instance representing a tracking point
        """
        self.events.append(event)
    
    def verify_authenticity(self, claimed_hash: str) -> bool:
        """
        Verify if a product is authentic by comparing hashes.
        Used to prevent counterfeiting and ensure product legitimacy.
        
        Args:
            claimed_hash: Hash claimed to belong to this product
            
        Returns:
            True if product is authentic, False otherwise
        """
        return self.product_hash == claimed_hash
    
    def get_current_location(self) -> str:
        """
        Get the current location of the product based on latest event.
        
        Returns:
            Current location string, or initial location if no events
        """
        if self.events:
            return self.events[-1].location
        return self.initial_location
    
    def get_full_history(self) -> List[Dict[str, Any]]:
        """
        Get complete tracking history of the product.
        
        Returns:
            List of all supply chain events in chronological order
        """
        return [event.to_dict() for event in self.events]
    
    def check_safety_alerts(self) -> List[Dict[str, str]]:
        """
        Check for any safety alerts or quality issues in the supply chain.
        Particularly important for food and pharmaceutical products.
        
        Returns:
            List of alerts with severity and descriptions
        """
        alerts = []
        
        for event in self.events:
            if event.event_type == 'quality_alert':
                alerts.append({
                    'timestamp': event.timestamp,
                    'location': event.location,
                    'severity': event.metadata.get('severity', 'unknown'),
                    'description': event.metadata.get('description', 'No description')
                })
        
        return alerts
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert product to dictionary format for serialization.
        
        Returns:
            Dictionary representation of the product
        """
        return {
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'manufacturer': self.manufacturer,
            'manufacture_date': self.manufacture_date,
            'batch_number': self.batch_number,
            'initial_location': self.initial_location,
            'current_location': self.get_current_location(),
            'product_hash': self.product_hash,
            'registration_timestamp': self.registration_timestamp,
            'metadata': self.metadata,
            'events': self.get_full_history(),
            'safety_alerts': self.check_safety_alerts()
        }


class SupplyChainEvent:
    """
    Represents a single event in the product's supply chain journey.
    Each event is immutable once recorded on the blockchain.
    """
    
    def __init__(
        self,
        product_id: str,
        event_type: str,
        location: str,
        handler: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a supply chain tracking event.
        
        Args:
            product_id: ID of the product this event relates to
            event_type: Type of event (manufacture, transport, inspection, delivery, quality_alert, etc.)
            location: Geographic location where event occurred
            handler: Entity responsible for this stage (company, warehouse, transport, etc.)
            description: Human-readable description of the event
            metadata: Additional event data (temperature, humidity, inspector ID, etc.)
        """
        self.product_id = product_id
        self.event_type = event_type
        self.location = location
        self.handler = handler
        self.description = description
        self.timestamp = time.time()
        self.metadata = metadata or {}
        
        # Generate event hash for integrity verification
        self.event_hash = self._generate_event_hash()
    
    def _generate_event_hash(self) -> str:
        """
        Generate hash for event integrity verification.
        Ensures the event data hasn't been tampered with.
        
        Returns:
            SHA-256 hash of event data
        """
        event_string = json.dumps({
            'product_id': self.product_id,
            'event_type': self.event_type,
            'location': self.location,
            'handler': self.handler,
            'description': self.description,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }, sort_keys=True)
        
        return hashlib.sha256(event_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary format for serialization.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            'product_id': self.product_id,
            'event_type': self.event_type,
            'location': self.location,
            'handler': self.handler,
            'description': self.description,
            'timestamp': self.timestamp,
            'event_hash': self.event_hash,
            'metadata': self.metadata
        }


class SupplyChainManager:
    """
    Manages all supply chain operations and product tracking.
    Integrates with blockchain for immutable record keeping.
    """
    
    def __init__(self):
        """Initialize the supply chain manager with empty product registry."""
        self.products: Dict[str, Product] = {}
    
    def register_product(
        self,
        product_id: str,
        name: str,
        category: str,
        manufacturer: str,
        manufacture_date: str,
        batch_number: str,
        initial_location: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Product:
        """
        Register a new product in the supply chain system.
        
        Args:
            product_id: Unique product identifier
            name: Product name
            category: Product category
            manufacturer: Manufacturing entity
            manufacture_date: Date of manufacture
            batch_number: Batch number
            initial_location: Starting location
            metadata: Additional product information
            
        Returns:
            Created Product instance
            
        Raises:
            ValueError: If product_id already exists
        """
        if product_id in self.products:
            raise ValueError(f"Product {product_id} already registered")
        
        product = Product(
            product_id=product_id,
            name=name,
            category=category,
            manufacturer=manufacturer,
            manufacture_date=manufacture_date,
            batch_number=batch_number,
            initial_location=initial_location,
            metadata=metadata
        )
        
        self.products[product_id] = product
        return product
    
    def add_event_to_product(
        self,
        product_id: str,
        event_type: str,
        location: str,
        handler: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SupplyChainEvent:
        """
        Add a tracking event to a product's history.
        
        Args:
            product_id: ID of the product
            event_type: Type of supply chain event
            location: Event location
            handler: Responsible entity
            description: Event description
            metadata: Additional event data
            
        Returns:
            Created SupplyChainEvent instance
            
        Raises:
            ValueError: If product doesn't exist
        """
        if product_id not in self.products:
            raise ValueError(f"Product {product_id} not found")
        
        event = SupplyChainEvent(
            product_id=product_id,
            event_type=event_type,
            location=location,
            handler=handler,
            description=description,
            metadata=metadata
        )
        
        self.products[product_id].add_event(event)
        return event
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """
        Retrieve a product by its ID.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product instance or None if not found
        """
        return self.products.get(product_id)
    
    def verify_product_authenticity(self, product_id: str, claimed_hash: str) -> bool:
        """
        Verify if a product is authentic using its hash.
        
        Args:
            product_id: Product identifier
            claimed_hash: Hash to verify against
            
        Returns:
            True if authentic, False otherwise
        """
        product = self.get_product(product_id)
        if not product:
            return False
        return product.verify_authenticity(claimed_hash)
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """
        Get all products in a specific category.
        
        Args:
            category: Product category to filter by
            
        Returns:
            List of products in the category
        """
        return [p for p in self.products.values() if p.category == category]
    
    def get_products_by_manufacturer(self, manufacturer: str) -> List[Product]:
        """
        Get all products from a specific manufacturer.
        
        Args:
            manufacturer: Manufacturer name to filter by
            
        Returns:
            List of products from the manufacturer
        """
        return [p for p in self.products.values() if p.manufacturer == manufacturer]
    
    def get_all_products(self) -> List[Product]:
        """
        Get all registered products.
        
        Returns:
            List of all products in the system
        """
        return list(self.products.values())
    
    def get_products_with_alerts(self) -> List[Product]:
        """
        Get all products that have safety alerts.
        
        Returns:
            List of products with safety alerts
        """
        return [p for p in self.products.values() if p.check_safety_alerts()]
