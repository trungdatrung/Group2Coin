"""
Cryptographic utility functions for hashing and key generation
"""
import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


def calculate_hash(data):
    """
    Calculate SHA-256 hash of given data
    Args:
        data: Dictionary or string to hash
    Returns:
        Hexadecimal string of the hash
    """
    if isinstance(data, dict):
        data_string = json.dumps(data, sort_keys=True)
    else:
        data_string = str(data)
    return hashlib.sha256(data_string.encode()).hexdigest()


def generate_key_pair():
    """
    Generate RSA public-private key pair for wallet
    Returns:
        Tuple of (private_key_pem, public_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem


def sign_data(private_key_pem, data):
    """
    Sign data with private key
    Args:
        private_key_pem: Private key in PEM format
        data: Data to sign
    Returns:
        Hexadecimal string of signature
    """
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
        backend=default_backend()
    )
    
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    
    signature = private_key.sign(
        data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    return signature.hex()


def verify_signature(public_key_pem, data, signature_hex):
    """
    Verify signature with public key
    Args:
        public_key_pem: Public key in PEM format
        data: Original data
        signature_hex: Hexadecimal signature string
    Returns:
        Boolean indicating if signature is valid
    """
    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode(),
            backend=default_backend()
        )
        
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        
        signature = bytes.fromhex(signature_hex)
        
        public_key.verify(
            signature,
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
