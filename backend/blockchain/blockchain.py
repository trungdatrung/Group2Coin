"""
Blockchain class managing the entire chain and transaction pool
"""
from blockchain.block import Block
from blockchain.transaction import Transaction


class Blockchain:
    """
    Main blockchain class managing chain, pending transactions, and mining
    """
    
    def __init__(self, difficulty=4, mining_reward=50):
        """
        Initialize blockchain with genesis block
        Args:
            difficulty: Mining difficulty (number of leading zeros)
            mining_reward: Reward for mining a block in Group2Coin
        """
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions = []
        self.mining_reward = mining_reward
    
    def create_genesis_block(self):
        """
        Create the first block in the blockchain
        Returns:
            Genesis Block object
        """
        genesis_transaction = Transaction('GENESIS', 'GENESIS', 0)
        genesis_block = Block(0, [genesis_transaction], '0')
        return genesis_block
    
    def get_latest_block(self):
        """
        Get the most recent block in the chain
        Returns:
            Latest Block object
        """
        return self.chain[-1]
    
    def add_transaction(self, transaction):
        """
        Add a transaction to pending transactions pool
        Args:
            transaction: Transaction object to add
        Returns:
            Boolean indicating success
        """
        if not transaction.is_valid():
            return False
        
        sender_balance = self.get_balance(transaction.sender)
        if transaction.sender != 'MINING_REWARD' and sender_balance < transaction.amount:
            return False
        
        self.pending_transactions.append(transaction)
        return True
    
    def mine_pending_transactions(self, mining_reward_address):
        """
        Mine all pending transactions into a new block
        Args:
            mining_reward_address: Wallet address to receive mining reward
        Returns:
            Newly mined Block object
        """
        reward_transaction = Transaction('MINING_REWARD', mining_reward_address, self.mining_reward)
        self.pending_transactions.append(reward_transaction)
        
        new_block = Block(
            len(self.chain),
            self.pending_transactions,
            self.get_latest_block().hash
        )
        
        new_block.mine_block(self.difficulty)
        
        self.chain.append(new_block)
        self.pending_transactions = []
        
        return new_block
    
    def get_balance(self, address):
        """
        Calculate balance for a given wallet address
        Args:
            address: Public key of wallet
        Returns:
            Balance in Group2Coin
        """
        balance = 0
        
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == address:
                    balance -= transaction.amount
                
                if transaction.recipient == address:
                    balance += transaction.amount
        
        return balance
    
    def is_chain_valid(self):
        """
        Verify integrity of the entire blockchain
        Returns:
            Boolean indicating if chain is valid
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
            
            for transaction in current_block.transactions:
                if not transaction.is_valid():
                    return False
        
        return True
    
    def get_transaction_history(self, address):
        """
        Get all transactions for a given address
        Args:
            address: Wallet public key
        Returns:
            List of transactions involving the address
        """
        transactions = []
        
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == address or transaction.recipient == address:
                    tx_dict = transaction.to_dict()
                    tx_dict['block_index'] = block.index
                    transactions.append(tx_dict)
        
        return transactions
    
    def to_dict(self):
        """
        Convert entire blockchain to dictionary
        Returns:
            Dictionary representation of blockchain
        """
        return {
            'chain': [block.to_dict() for block in self.chain],
            'difficulty': self.difficulty,
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions],
            'mining_reward': self.mining_reward
        }
