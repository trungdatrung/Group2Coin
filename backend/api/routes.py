from flask import Blueprint, jsonify, request, send_file
import json
import io
from datetime import datetime

api = Blueprint('api', __name__)

# Global variables to store blockchain, wallets, and supply chain manager
blockchain = None
wallets = {}
supply_chain_manager = None

def init_routes(bc):
    global blockchain, supply_chain_manager
    blockchain = bc
    
    # Initialize supply chain manager
    from blockchain.product import SupplyChainManager
    supply_chain_manager = SupplyChainManager()

# ============================================
# BLOCKCHAIN ROUTES
# ============================================

@api.route('/blockchain', methods=['GET'])
def get_blockchain():
    """Get the entire blockchain"""
    try:
        chain_data = []
        for block in blockchain.chain:
            block_data = {
                'index': block.index,
                'timestamp': block.timestamp,
                'transactions': [
                    {
                        'sender': tx.sender,
                        'recipient': tx.recipient,
                        'amount': tx.amount,
                        'timestamp': tx.timestamp
                    } for tx in block.transactions
                ],
                'previous_hash': block.previous_hash,
                'nonce': block.nonce,
                'hash': block.hash
            }
            chain_data.append(block_data)
        # include pending transactions snapshot so frontend can show counts
        pending = [
            {
                'sender': tx.sender,
                'recipient': tx.recipient,
                'amount': tx.amount,
                'timestamp': tx.timestamp
            } for tx in blockchain.pending_transactions
        ]

        return jsonify({
            'chain': chain_data,
            'length': len(chain_data),
            'difficulty': blockchain.difficulty,
            'mining_reward': blockchain.mining_reward,
            'pending_transactions': pending
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/blockchain/validate', methods=['GET'])
def validate_blockchain():
    """Validate the blockchain integrity"""
    try:
        is_valid = blockchain.is_chain_valid()
        return jsonify({'valid': is_valid}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/blockchain/pending', methods=['GET'])
def get_pending_transactions():
    """Get all pending transactions"""
    try:
        pending = [
            {
                'sender': tx.sender,
                'recipient': tx.recipient,
                'amount': tx.amount,
                'timestamp': tx.timestamp
            } for tx in blockchain.pending_transactions
        ]
        return jsonify({'pending_transactions': pending, 'count': len(pending)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/blockchain/difficulty', methods=['GET'])
def get_difficulty():
    """Get current mining difficulty"""
    try:
        return jsonify({'difficulty': blockchain.difficulty}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/blockchain/difficulty', methods=['POST'])
def set_difficulty():
    """Set mining difficulty"""
    try:
        data = request.get_json()
        difficulty = data.get('difficulty')
        
        if not difficulty:
            return jsonify({'error': 'Difficulty value required'}), 400
        
        if difficulty < 1 or difficulty > 10:
            return jsonify({'error': 'Difficulty must be between 1 and 10'}), 400
        
        blockchain.difficulty = int(difficulty)
        
        return jsonify({
            'message': 'Difficulty updated successfully',
            'difficulty': blockchain.difficulty
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# WALLET ROUTES
# ============================================

@api.route('/wallet/create', methods=['POST'])
def create_wallet():
    """Create a new wallet"""
    try:
        from wallet.wallet import Wallet
        
        wallet = Wallet()
        wallets[wallet.address] = wallet
        
        return jsonify({
            'address': wallet.address,
            'public_key': wallet.public_key,
            'private_key': wallet.private_key
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/wallet/<address>/balance', methods=['GET'])
def get_balance(address):
    """Get wallet balance"""
    try:
        balance = blockchain.get_balance(address)
        return jsonify({'address': address, 'balance': balance}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/wallet/<address>/transactions', methods=['GET'])
def get_transactions(address):
    """Get wallet transaction history"""
    try:
        transactions = []
        
        for block in blockchain.chain:
            for tx in block.transactions:
                if tx.sender == address or tx.recipient == address:
                    tx_type = 'received' if tx.recipient == address else 'sent'
                    transactions.append({
                        'type': tx_type,
                        'sender': tx.sender,
                        'recipient': tx.recipient,
                        'amount': tx.amount,
                        'timestamp': tx.timestamp,
                        'block_index': block.index
                    })
        
        return jsonify({'transactions': transactions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/wallet/export/<address>', methods=['GET'])
def export_wallet(address):
    """Export wallet data as JSON file"""
    try:
        if address not in wallets:
            return jsonify({"error": "Wallet not found"}), 404
        
        wallet = wallets[address]
        balance = blockchain.get_balance(address)
        
        transactions = []
        for block in blockchain.chain:
            for tx in block.transactions:
                if tx.sender == wallet.public_key or tx.recipient == address:
                    transactions.append({
                        "sender": tx.sender[:20] + "..." if len(tx.sender) > 20 else tx.sender,
                        "recipient": tx.recipient,
                        "amount": tx.amount,
                        "timestamp": tx.timestamp
                    })
        
        export_data = {
            "address": wallet.address,
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "balance": balance,
            "transaction_count": len(transactions),
            "exported_at": datetime.now().isoformat(),
            "blockchain_info": {
                "total_blocks": len(blockchain.chain),
                "difficulty": blockchain.difficulty
            }
        }
        
        json_str = json.dumps(export_data, indent=2)
        json_bytes = io.BytesIO(json_str.encode('utf-8'))
        
        return send_file(
            json_bytes,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'wallet_{address[:8]}.json'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/wallet/import', methods=['POST'])
def import_wallet():
    """Import wallet from exported JSON data"""
    try:
        data = request.get_json()
        wallet_data = data.get('wallet_data')
        
        if not wallet_data:
            return jsonify({"error": "No wallet data provided"}), 400
        
        required_fields = ['address', 'public_key', 'private_key']
        for field in required_fields:
            if field not in wallet_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        from wallet.wallet import Wallet
        
        wallet = Wallet.__new__(Wallet)
        wallet.address = wallet_data['address']
        wallet.public_key = wallet_data['public_key']
        wallet.private_key = wallet_data['private_key']
        
        wallets[wallet.address] = wallet
        
        current_balance = blockchain.get_balance(wallet.address)
        
        transactions = []
        for block in blockchain.chain:
            for tx in block.transactions:
                if tx.sender == wallet.public_key or tx.recipient == wallet.address:
                    transactions.append({
                        "sender": tx.sender[:20] + "..." if len(tx.sender) > 20 else tx.sender,
                        "recipient": tx.recipient,
                        "amount": tx.amount,
                        "timestamp": tx.timestamp,
                        "block_index": block.index
                    })
        
        return jsonify({
            "message": "Wallet imported successfully",
            "wallet": {
                "address": wallet.address,
                "public_key": wallet.public_key,
                "balance": current_balance,
                "transaction_count": len(transactions),
                "transactions": transactions[-10:]
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/wallet/load/<address>', methods=['GET'])
def load_wallet_by_address(address):
    """Load wallet information by address"""
    try:
        balance = blockchain.get_balance(address)
        
        transactions = []
        for block in blockchain.chain:
            for tx in block.transactions:
                if tx.recipient == address or (hasattr(tx, 'sender') and tx.sender == address):
                    transactions.append({
                        "type": "received" if tx.recipient == address else "sent",
                        "sender": tx.sender[:20] + "..." if len(tx.sender) > 20 else tx.sender,
                        "recipient": tx.recipient,
                        "amount": tx.amount,
                        "timestamp": tx.timestamp,
                        "block_index": block.index
                    })
        
        total_received = sum(tx['amount'] for tx in transactions if tx['type'] == 'received')
        total_sent = sum(tx['amount'] for tx in transactions if tx['type'] == 'sent')
        
        return jsonify({
            "address": address,
            "balance": balance,
            "statistics": {
                "total_received": total_received,
                "total_sent": total_sent,
                "transaction_count": len(transactions)
            },
            "transactions": transactions,
            "wallet_exists": address in wallets
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/wallet/validate', methods=['POST'])
def validate_wallet():
    """Validate if wallet keys are correct and match"""
    try:
        data = request.get_json()
        address = data.get('address')
        public_key = data.get('public_key')
        private_key = data.get('private_key')
        
        if not all([address, public_key, private_key]):
            return jsonify({"error": "Missing required fields"}), 400
        
        from wallet.wallet import Wallet
        from utils.crypto import calculate_hash, sign_data, verify_signature
        
        expected_address = calculate_hash(public_key)[:40]
        
        if expected_address != address:
            return jsonify({
                "valid": False,
                "error": "Address does not match public key"
            }), 200
        
        test_message = "wallet_validation_test"
        try:
            signature = sign_data(private_key, test_message)
            is_valid = verify_signature(public_key, test_message, signature)
            
            if is_valid:
                return jsonify({
                    "valid": True,
                    "message": "Wallet keys are valid and match"
                }), 200
            else:
                return jsonify({
                    "valid": False,
                    "error": "Private key does not match public key"
                }), 200
                
        except Exception as e:
            return jsonify({
                "valid": False,
                "error": f"Key validation failed: {str(e)}"
            }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# TRANSACTION ROUTES
# ============================================

@api.route('/transaction/create', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    try:
        data = request.get_json()
        sender = data.get('sender')
        recipient = data.get('recipient')
        amount = data.get('amount')
        private_key = data.get('private_key')
        
        if not all([sender, recipient, amount, private_key]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        from blockchain.transaction import Transaction
        
        transaction = Transaction(sender, recipient, amount)
        transaction.sign_transaction(private_key)
        
        if not transaction.is_valid():
            return jsonify({'error': 'Invalid transaction signature'}), 400
        
        blockchain.add_transaction(transaction)
        
        return jsonify({
            'message': 'Transaction created successfully',
            'transaction': {
                'sender': transaction.sender[:20] + '...',
                'recipient': transaction.recipient,
                'amount': transaction.amount,
                'timestamp': transaction.timestamp
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/transaction/pending', methods=['GET'])
def get_pending():
    """Get pending transactions"""
    try:
        pending = [
            {
                'sender': tx.sender[:20] + '...',
                'recipient': tx.recipient,
                'amount': tx.amount,
                'timestamp': tx.timestamp
            } for tx in blockchain.pending_transactions
        ]
        return jsonify({'pending_transactions': pending}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# MINING ROUTES
# ============================================

@api.route('/mine', methods=['POST'])
def mine_block():
    """Mine a new block"""
    try:
        data = request.get_json()
        miner_address = data.get('miner_address')
        
        if not miner_address:
            return jsonify({'error': 'Miner address required'}), 400
        
        # Allow mining even without pending transactions (just for mining rewards)
        # Comment this out if you want to require transactions
        # if len(blockchain.pending_transactions) == 0:
        #     return jsonify({'error': 'No transactions to mine'}), 400
        
        block = blockchain.mine_pending_transactions(miner_address)
        
        return jsonify({
            'message': 'Block mined successfully',
            'block': {
                'index': block.index,
                'hash': block.hash,
                'previous_hash': block.previous_hash,
                'nonce': block.nonce,
                'transactions': len(block.transactions)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/blockchain/reward', methods=['GET'])
def get_reward():
    """Get mining reward"""
    try:
        return jsonify({'reward': blockchain.mining_reward}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# SUPPLY CHAIN ROUTES
# ============================================

@api.route('/supplychain/product/register', methods=['POST'])
def register_product():
    """
    Register a new product in the supply chain system.
    This creates an immutable record of the product's origin.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['product_id', 'name', 'category', 'manufacturer', 
                         'manufacture_date', 'batch_number', 'initial_location']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Register the product
        product = supply_chain_manager.register_product(
            product_id=data['product_id'],
            name=data['name'],
            category=data['category'],
            manufacturer=data['manufacturer'],
            manufacture_date=data['manufacture_date'],
            batch_number=data['batch_number'],
            initial_location=data['initial_location'],
            metadata=data.get('metadata', {})
        )
        
        return jsonify({
            'message': 'Product registered successfully',
            'product': product.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/supplychain/product/<product_id>/event', methods=['POST'])
def add_product_event(product_id):
    """
    Add a tracking event to a product's supply chain history.
    Each event represents a movement or status change in the supply chain.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['event_type', 'location', 'handler', 'description']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add event to product
        event = supply_chain_manager.add_event_to_product(
            product_id=product_id,
            event_type=data['event_type'],
            location=data['location'],
            handler=data['handler'],
            description=data['description'],
            metadata=data.get('metadata', {})
        )
        
        return jsonify({
            'message': 'Event added successfully',
            'event': event.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/supplychain/product/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Retrieve complete product information including full tracking history.
    """
    try:
        product = supply_chain_manager.get_product(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/supplychain/product/<product_id>/verify', methods=['POST'])
def verify_product(product_id):
    """
    Verify product authenticity using its unique hash.
    This helps prevent counterfeiting by confirming product legitimacy.
    """
    try:
        data = request.get_json()
        claimed_hash = data.get('product_hash')
        
        if not claimed_hash:
            return jsonify({'error': 'Product hash required'}), 400
        
        is_authentic = supply_chain_manager.verify_product_authenticity(
            product_id, 
            claimed_hash
        )
        
        product = supply_chain_manager.get_product(product_id)
        
        return jsonify({
            'authentic': is_authentic,
            'product_id': product_id,
            'actual_hash': product.product_hash if product else None,
            'message': 'Product is authentic' if is_authentic else 'Product verification failed'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/supplychain/products', methods=['GET'])
def get_all_products():
    """
    Get all registered products in the supply chain.
    Supports filtering by category and manufacturer.
    """
    try:
        category = request.args.get('category')
        manufacturer = request.args.get('manufacturer')
        
        if category:
            products = supply_chain_manager.get_products_by_category(category)
        elif manufacturer:
            products = supply_chain_manager.get_products_by_manufacturer(manufacturer)
        else:
            products = supply_chain_manager.get_all_products()
        
        return jsonify({
            'products': [p.to_dict() for p in products],
            'count': len(products)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/supplychain/products/alerts', methods=['GET'])
def get_products_with_alerts():
    """
    Get all products that have safety or quality alerts.
    Critical for food safety and pharmaceutical monitoring.
    """
    try:
        products = supply_chain_manager.get_products_with_alerts()
        
        return jsonify({
            'products': [p.to_dict() for p in products],
            'count': len(products),
            'alert_summary': [
                {
                    'product_id': p.product_id,
                    'product_name': p.name,
                    'alerts': p.check_safety_alerts()
                } for p in products
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/supplychain/categories', methods=['GET'])
def get_categories():
    """
    Get list of all product categories in the system.
    """
    try:
        products = supply_chain_manager.get_all_products()
        categories = list(set(p.category for p in products))
        
        category_counts = {}
        for cat in categories:
            category_counts[cat] = len(supply_chain_manager.get_products_by_category(cat))
        
        return jsonify({
            'categories': categories,
            'category_counts': category_counts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/supplychain/manufacturers', methods=['GET'])
def get_manufacturers():
    """
    Get list of all manufacturers in the system.
    """
    try:
        products = supply_chain_manager.get_all_products()
        manufacturers = list(set(p.manufacturer for p in products))
        
        manufacturer_counts = {}
        for mfr in manufacturers:
            manufacturer_counts[mfr] = len(supply_chain_manager.get_products_by_manufacturer(mfr))
        
        return jsonify({
            'manufacturers': manufacturers,
            'manufacturer_counts': manufacturer_counts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500