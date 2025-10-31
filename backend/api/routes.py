"""
Flask API routes for blockchain interactions
"""
from flask import Blueprint, jsonify, request
from blockchain.transaction import Transaction

api = Blueprint('api', __name__)

blockchain = None
wallets = {}


def init_routes(bc):
    """
    Initialize routes with blockchain instance
    Args:
        bc: Blockchain instance
    """
    global blockchain
    blockchain = bc


@api.route('/blockchain', methods=['GET'])
def get_blockchain():
    """
    Get entire blockchain data
    Returns:
        JSON representation of blockchain
    """
    return jsonify(blockchain.to_dict()), 200


@api.route('/blockchain/validate', methods=['GET'])
def validate_blockchain():
    """
    Validate blockchain integrity
    Returns:
        JSON with validation result
    """
    is_valid = blockchain.is_chain_valid()
    return jsonify({'valid': is_valid}), 200


@api.route('/wallet/create', methods=['POST'])
def create_wallet():
    """
    Create a new wallet
    Returns:
        JSON with wallet information
    """
    from wallet.wallet import Wallet
    
    new_wallet = Wallet()
    wallet_data = new_wallet.to_dict()
    
    wallets[wallet_data['address']] = wallet_data
    
    return jsonify(wallet_data), 201


@api.route('/wallet/<address>/balance', methods=['GET'])
def get_balance(address):
    """
    Get balance for a wallet address
    Args:
        address: Wallet address
    Returns:
        JSON with balance information
    """
    balance = blockchain.get_balance(address)
    return jsonify({'address': address, 'balance': balance}), 200


@api.route('/wallet/<address>/transactions', methods=['GET'])
def get_transactions(address):
    """
    Get transaction history for a wallet
    Args:
        address: Wallet address
    Returns:
        JSON with transaction history
    """
    transactions = blockchain.get_transaction_history(address)
    return jsonify({'address': address, 'transactions': transactions}), 200


@api.route('/transaction/create', methods=['POST'])
def create_transaction():
    """
    Create and add a new transaction
    Request body should contain:
        - sender: sender public key
        - recipient: recipient address
        - amount: transaction amount
        - private_key: sender's private key for signing
    Returns:
        JSON with transaction status
    """
    data = request.get_json()
    
    required_fields = ['sender', 'recipient', 'amount', 'private_key']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        transaction = Transaction(
            data['sender'],
            data['recipient'],
            amount
        )
        
        transaction.sign_transaction(data['private_key'])
        
        if blockchain.add_transaction(transaction):
            return jsonify({
                'message': 'Transaction added to pending pool',
                'transaction': transaction.to_dict()
            }), 201
        else:
            return jsonify({'error': 'Invalid transaction or insufficient balance'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/mine', methods=['POST'])
def mine_block():
    """
    Mine pending transactions
    Request body should contain:
        - miner_address: address to receive mining reward
    Returns:
        JSON with mined block information
    """
    data = request.get_json()
    
    if 'miner_address' not in data:
        return jsonify({'error': 'Miner address required'}), 400
    
    try:
        new_block = blockchain.mine_pending_transactions(data['miner_address'])
        return jsonify({
            'message': 'Block mined successfully',
            'block': new_block.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/pending-transactions', methods=['GET'])
def get_pending_transactions():
    """
    Get all pending transactions
    Returns:
        JSON with pending transactions
    """
    pending = [tx.to_dict() for tx in blockchain.pending_transactions]
    return jsonify({'pending_transactions': pending}), 200


@api.route('/difficulty', methods=['GET'])
def get_difficulty():
    """
    Get current mining difficulty
    Returns:
        JSON with difficulty level
    """
    return jsonify({'difficulty': blockchain.difficulty}), 200


@api.route('/difficulty', methods=['POST'])
def set_difficulty():
    """
    Set mining difficulty
    Request body should contain:
        - difficulty: new difficulty level (1-10)
    Returns:
        JSON with confirmation
    """
    data = request.get_json()
    
    if 'difficulty' not in data:
        return jsonify({'error': 'Difficulty level required'}), 400
    
    try:
        difficulty = int(data['difficulty'])
        if difficulty < 1 or difficulty > 10:
            return jsonify({'error': 'Difficulty must be between 1 and 10'}), 400
        
        blockchain.difficulty = difficulty
        return jsonify({
            'message': 'Difficulty updated',
            'difficulty': blockchain.difficulty
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
