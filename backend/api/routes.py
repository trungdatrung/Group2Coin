from flask import Blueprint, jsonify, request, send_file
import json
import io
from datetime import datetime
from utils.crypto import calculate_hash

api = Blueprint('api', __name__)

# Global NodeService instance
node_service = None
# Aliases for compatibility with existing Manager logic if they are used directly in routes (though we should delegate)
supply_chain_manager = None
smart_contract_manager = None

def init_routes(service):
    global node_service, supply_chain_manager, smart_contract_manager
    node_service = service
    supply_chain_manager = service.supply_chain_manager
    smart_contract_manager = service.smart_contract_manager

# ============================================
# BLOCKCHAIN ROUTES
# ============================================

@api.route('/blockchain', methods=['GET'])
def get_blockchain():
    """Get the entire blockchain"""
    try:
        chain_data = []
        chain = node_service.get_chain()
        for block in chain:
            block_data = block.to_dict()
            chain_data.append(block_data)
            
        # include pending transactions snapshot
        pending = [tx.to_dict() for tx in node_service.get_pending_transactions()]

        return jsonify({
            'chain': chain_data,
            'length': len(chain_data),
            'difficulty': node_service.get_difficulty(),
            'mining_reward': node_service.blockchain.mining_reward,
            'pending_transactions': pending
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/blockchain/validate', methods=['GET'])
def validate_blockchain():
    """Validate the blockchain integrity"""
    try:
        is_valid = node_service.is_chain_valid()
        return jsonify({'valid': is_valid}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/blockchain/pending', methods=['GET'])
def get_pending_transactions():
    """Get all pending transactions"""
    try:
        pending = [tx.to_dict() for tx in node_service.get_pending_transactions()]
        return jsonify({'pending_transactions': pending, 'count': len(pending)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/blockchain/difficulty', methods=['GET'])
def get_difficulty():
    """Get current mining difficulty"""
    try:
        return jsonify({'difficulty': node_service.get_difficulty()}), 200
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
        
        node_service.set_difficulty(int(difficulty))
        
        return jsonify({
            'message': 'Difficulty updated successfully',
            'difficulty': node_service.get_difficulty()
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
        wallet = node_service.create_wallet()
        return jsonify(wallet.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/wallet/<address>/balance', methods=['GET'])
def get_balance(address):
    """Get wallet balance"""
    try:
        balance = node_service.get_balance(address)
        return jsonify({'address': address, 'balance': balance}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/wallet/<address>/transactions', methods=['GET'])
def get_transactions(address):
    """Get wallet transaction history"""
    try:
        # TODO: Move this logic to NodeService or Blockchain class strictly
        # For now, replicating logic using node_service.blockchain
        transactions = []
        
        # This is expensive O(N) iteration, should be optimized in future with DB queries
        # But we are using `node_service.get_chain()` which loads from DB
        chain = node_service.get_chain()
        for block in chain:
            for tx in block.transactions:
                if tx.sender == address or tx.recipient == address:
                    tx_type = 'received' if tx.recipient == address else 'sent'
                    transactions.append({
                        'type': tx_type,
                        'sender': tx.sender,
                        'recipient': tx.recipient,
                        'amount': tx.amount,
                        'timestamp': tx.timestamp,
                        'block_index': block.index,
                        'nonce': getattr(tx, 'nonce', None)
                    })
        
        return jsonify({'transactions': transactions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/wallet/export/<address>', methods=['GET'])
def export_wallet(address):
    """Export wallet data as JSON file"""
    try:
        wallet_data = node_service.get_wallet(address)
        if not wallet_data:
            return jsonify({"error": "Wallet not found"}), 404
        
        balance = node_service.get_balance(address)
        
        # Simple transaction count for export
        # Optimization: Don't iterate everything if not needed
        tx_count = 0 
        
        export_data = {
            "address": wallet_data['address'],
            "public_key": wallet_data['public_key'],
            "private_key": wallet_data['private_key'],
            "balance": balance,
            "transaction_count": "Unknown (Calculation Pending)", # skipped for perf
            "exported_at": datetime.now().isoformat()
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
        
        imported = node_service.import_wallet(wallet_data)
        balance = node_service.get_balance(imported['address'])
        
        return jsonify({
            "message": "Wallet imported successfully",
            "wallet": {
                "address": imported['address'],
                "public_key": imported['public_key'],
                "balance": balance
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/wallet/load/<address>', methods=['GET'])
def load_wallet_by_address(address):
    """Load wallet information by address"""
    try:
        balance = node_service.get_balance(address)
        
        # Statistics logic (simplified)
        # In a real app, use DB aggregation
        return jsonify({
            "address": address,
            "balance": balance,
            "wallet_exists": node_service.get_wallet(address) is not None
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
            
        from utils.crypto import calculate_hash, sign_data, verify_signature
        expected_address = calculate_hash(public_key)[:40]
        
        if expected_address != address:
            return jsonify({"valid": False, "error": "Address does not match public key"}), 200
            
        test_message = "wallet_validation_test"
        try:
            signature = sign_data(private_key, test_message)
            is_valid = verify_signature(public_key, test_message, signature)
            return jsonify({"valid": is_valid}), 200
        except Exception:
            return jsonify({"valid": False, "error": "Key validation failed"}), 200
            
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
        sender_pk = data.get('sender') # Legacy: Frontend sends Public Key
        recipient = data.get('recipient')
        amount = data.get('amount')
        private_key = data.get('private_key')
        
        if not all([sender_pk, recipient, amount, private_key]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        # Derive Address from PK to fix infinite money and standardize on Address
        sender_address = calculate_hash(sender_pk)[:40]
        
        # Delegate to NodeService
        # Note: NodeService recalculates public key from private key to ensure validity
        transaction = node_service.create_transaction(sender_address, recipient, amount, private_key)
        
        return jsonify({
            'message': 'Transaction created successfully',
            'transaction': transaction.to_dict()
        }), 201
        
    except ValueError as e:
         return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/transaction/pending', methods=['GET'])
def get_pending():
    """Get pending transactions"""
    try:
        pending = [tx.to_dict() for tx in node_service.get_pending_transactions()]
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
        
        block = node_service.mine_block(miner_address)
        
        if block:
            return jsonify({
                'message': 'Block mined successfully',
                'block': block.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Mining failed'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/blockchain/reward', methods=['GET'])
def get_reward():
    """Get mining reward"""
    try:
        return jsonify({'reward': node_service.blockchain.mining_reward}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# SUPPLY CHAIN ROUTES
# ============================================

@api.route('/supplychain/product/register', methods=['POST'])
def register_product():
    """Register a new product in the supply chain system."""
    try:
        data = request.get_json()
        required_fields = ['product_id', 'name', 'category', 'manufacturer', 'manufacture_date', 'batch_number', 'initial_location']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        product = supply_chain_manager.register_product(
            product_id=data['product_id'], name=data['name'], category=data['category'],
            manufacturer=data['manufacturer'], manufacture_date=data['manufacture_date'],
            batch_number=data['batch_number'], initial_location=data['initial_location'],
            metadata=data.get('metadata', {})
        )
        
        from blockchain.supply_chain_transaction import SupplyChainTransaction
        sc_transaction = SupplyChainTransaction.create_product_registration(product)
        # Use node_service blockchain
        node_service.blockchain.add_transaction(sc_transaction)
        
        return jsonify({
            'message': 'Product registered successfully and recorded on blockchain',
            'product': product.to_dict(),
            'blockchain_pending': True
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supplychain/product/<product_id>/event', methods=['POST'])
def add_product_event(product_id):
    """Add a tracking event to a product's supply chain history."""
    try:
        data = request.get_json()
        required_fields = ['event_type', 'location', 'handler', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        event = supply_chain_manager.add_event_to_product(
            product_id=product_id, event_type=data['event_type'],
            location=data['location'], handler=data['handler'],
            description=data['description'], metadata=data.get('metadata', {})
        )
        
        from blockchain.supply_chain_transaction import SupplyChainTransaction
        sc_transaction = SupplyChainTransaction.create_tracking_event(product_id, event)
        node_service.blockchain.add_transaction(sc_transaction)
        
        return jsonify({
            'message': 'Event added successfully and recorded on blockchain',
            'event': event.to_dict(),
            'blockchain_pending': True
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supplychain/product/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = supply_chain_manager.get_product(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify({'product': product.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supplychain/product/<product_id>/verify', methods=['POST'])
def verify_product(product_id):
    try:
        data = request.get_json()
        claimed_hash = data.get('product_hash')
        if not claimed_hash:
            return jsonify({'error': 'Product hash required'}), 400
        is_authentic = supply_chain_manager.verify_product_authenticity(product_id, claimed_hash)
        product = supply_chain_manager.get_product(product_id)
        return jsonify({'authentic': is_authentic, 'product_id': product_id, 'actual_hash': product.product_hash if product else None}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supplychain/products', methods=['GET'])
def get_all_products():
    try:
        category = request.args.get('category')
        manufacturer = request.args.get('manufacturer')
        if category:
            products = supply_chain_manager.get_products_by_category(category)
        elif manufacturer:
            products = supply_chain_manager.get_products_by_manufacturer(manufacturer)
        else:
            products = supply_chain_manager.get_all_products()
        return jsonify({'products': [p.to_dict() for p in products], 'count': len(products)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supplychain/products/alerts', methods=['GET'])
def get_products_with_alerts():
    try:
        products = supply_chain_manager.get_products_with_alerts()
        return jsonify({'products': [p.to_dict() for p in products]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supplychain/categories', methods=['GET'])
def get_categories():
    try:
        products = supply_chain_manager.get_all_products()
        categories = list(set(p.category for p in products))
        return jsonify({'categories': categories}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supplychain/manufacturers', methods=['GET'])
def get_manufacturers():
    try:
        products = supply_chain_manager.get_all_products()
        manufacturers = list(set(p.manufacturer for p in products))
        return jsonify({'manufacturers': manufacturers}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supplychain/products/clear', methods=['DELETE'])
def clear_all_supply_chain_data():
    global supply_chain_manager
    try:
        from blockchain.product import SupplyChainManager
        supply_chain_manager = SupplyChainManager()
        # Also update node_service reference
        node_service.supply_chain_manager = supply_chain_manager
        return jsonify({'message': 'All supply chain data cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# SMART CONTRACT ROUTES
# ============================================

@api.route('/contracts/create', methods=['POST'])
def create_smart_contract():
    try:
        data = request.get_json()
        contract = smart_contract_manager.create_contract(
            contract_id=data['contract_id'], creator=data['creator'],
            contract_type=data['contract_type'], participants=data['participants'],
            amount=float(data['amount']), conditions=data['conditions'],
            metadata=data.get('metadata', {})
        )
        return jsonify({'message': 'Smart contract created successfully', 'contract': contract.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/contracts/<contract_id>', methods=['GET'])
def get_smart_contract(contract_id):
    try:
        contract = smart_contract_manager.get_contract(contract_id)
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404
        return jsonify({'contract': contract.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/contracts', methods=['GET'])
def get_all_contracts():
    try:
        address = request.args.get('address')
        if address:
            contracts = smart_contract_manager.get_contracts_by_participant(address)
        else:
            contracts = list(smart_contract_manager.contracts.values())
        return jsonify({'contracts': [c.to_dict() for c in contracts]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/contracts/pending', methods=['GET'])
def get_pending_contracts():
    try:
        contracts = smart_contract_manager.get_pending_contracts()
        return jsonify({'contracts': [c.to_dict() for c in contracts]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/contracts/<contract_id>/approve', methods=['POST'])
def approve_contract(contract_id):
    try:
        data = request.get_json()
        if 'approver' not in data:
             return jsonify({'error': 'Missing approver address'}), 400
        success = smart_contract_manager.add_approval(contract_id, data['approver'])
        if not success:
             return jsonify({'error': 'Failed to add approval'}), 400
        contract = smart_contract_manager.get_contract(contract_id)
        return jsonify({'message': 'Approval added', 'contract': contract.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/contracts/<contract_id>/execute', methods=['POST'])
def execute_contract(contract_id):
    try:
        contract = smart_contract_manager.get_contract(contract_id)
        if not contract:
             return jsonify({'error': 'Contract not found'}), 404
        result = contract.execute(node_service.blockchain)
        return jsonify({'execution_result': result, 'contract': contract.to_dict()}), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/contracts/check-execute', methods=['POST'])
def check_and_execute_contracts():
    try:
        results = smart_contract_manager.check_and_execute_contracts(node_service.blockchain)
        return jsonify({'message': f'Checked contracts, executed {len(results)}', 'executions': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/contracts/<contract_id>/check', methods=['GET'])
def check_contract_conditions(contract_id):
    try:
        contract = smart_contract_manager.get_contract(contract_id)
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404
        conditions_met = contract.check_conditions(node_service.blockchain)
        return jsonify({'conditions_met': conditions_met, 'contract': contract.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
