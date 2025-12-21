from blockchain.blockchain import Blockchain
from blockchain.product import SupplyChainManager
from blockchain.smart_contract import SmartContractManager
from blockchain.transaction import Transaction
from wallet.wallet import Wallet
from utils.database import Database
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class NodeService:
    def __init__(self):
        self.blockchain = Blockchain()
        self.supply_chain_manager = SupplyChainManager()
        self.smart_contract_manager = SmartContractManager()
        self.db = self.blockchain.db # Share the same DB connection if possible, or new one
        self.wallets = {} # Cache wallets
        self.load_wallets()

    def load_wallets(self):
        wallets_data = self.db.get_all_wallets()
        for w_data in wallets_data:
            # Reconstruct simple wallet object or just dict
            # Wallet class in wallet.py generates new keys on init, so we can't use it directly to load
            # We will just store data in dict
            self.wallets[w_data['address']] = w_data

    # Wallet Methods
    def create_wallet(self):
        wallet = Wallet()
        self.db.save_wallet(wallet)
        self.wallets[wallet.address] = wallet.to_dict()
        return wallet

    def get_wallet(self, address):
        return self.wallets.get(address)
    
    def import_wallet(self, wallet_data):
        # Determine if valid keys? We trust the wallet_data structure for now
        # Ideally verify keys match address
        self.wallets[wallet_data['address']] = wallet_data
        
        # Save to DB - Adapting Wallet object interface for save_wallet expects .address, .public_key, .private_key
        class WalletMock:
            def __init__(self, data):
                self.address = data['address']
                self.public_key = data['public_key']
                self.private_key = data['private_key']
        
        self.db.save_wallet(WalletMock(wallet_data))
        return wallet_data

    def get_balance(self, address):
        return self.blockchain.get_balance(address)
    
    # Transaction Methods
    def create_transaction(self, sender_address, recipient_address, amount, private_key):
        # 1. Extract public key from private key to include in transaction
        try:
            private_key_obj = serialization.load_pem_private_key(
                private_key.encode(), 
                password=None, 
                backend=default_backend()
            )
            public_key_pem = private_key_obj.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Invalid private key: {e}")

        # 2. Create Transaction
        tx = Transaction(
            sender_address=sender_address,
            recipient=recipient_address,
            amount=amount,
            public_key=public_key_pem
        )
        
        # 3. Sign
        tx.sign_transaction(private_key)
        
        # 4. Add to blockchain
        success = self.blockchain.add_transaction(tx)
        if not success:
            raise ValueError("Failed to add transaction (Invalid signature or insufficient balance)")
            
        return tx

    def get_pending_transactions(self):
        return self.blockchain.pending_transactions

    # Mining Methods
    def mine_block(self, miner_address):
        return self.blockchain.mine_pending_transactions(miner_address)

    # Blockchain Info
    def get_chain(self):
        return self.blockchain.chain

    def get_difficulty(self):
        return self.blockchain.difficulty

    def set_difficulty(self, difficulty):
        self.blockchain.difficulty = difficulty

    def is_chain_valid(self):
        return self.blockchain.is_chain_valid()
