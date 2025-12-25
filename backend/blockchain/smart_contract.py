"""
Smart Contract system for blockchain
Allows creation and execution of simple contracts with conditions
"""
import time
import json
from typing import Dict, List, Optional, Any
from enum import Enum


class ContractStatus(Enum):
    """Status of a smart contract"""
    PENDING = "pending"
    ACTIVE = "active"
    EXECUTED = "executed"
    FAILED = "failed"
    EXPIRED = "expired"


class ContractType(Enum):
    """Types of smart contracts"""
    ESCROW = "ESCROW"
    TIME_LOCK = "TIME_LOCK"
    CONDITIONAL = "CONDITIONAL"
    RECURRING = "RECURRING"


class SmartContract:
    """
    Represents a smart contract on the blockchain.
    Contracts hold conditions and automatically execute when conditions are met.
    """
    
    def __init__(
        self,
        contract_id: str,
        creator: str,
        contract_type: str,
        participants: List[str],
        amount: float,
        conditions: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a smart contract.
        
        Args:
            contract_id: Unique contract identifier
            creator: Address of contract creator
            contract_type: Type of contract (escrow, time_lock, etc.)
            participants: List of participant addresses
            amount: Amount locked in contract
            conditions: Conditions that must be met for execution
            metadata: Additional contract data
        """
        self.contract_id = contract_id
        self.creator = creator
        self.contract_type = contract_type
        self.participants = participants
        self.amount = amount
        self.conditions = conditions
        self.metadata = metadata or {}
        self.status = ContractStatus.PENDING.value
        self.created_at = time.time()
        self.executed_at = None
        self.execution_result = None
    
    def check_conditions(self, blockchain) -> bool:
        """
        Check if contract conditions are met.
        
        Args:
            blockchain: Blockchain instance to verify conditions
            
        Returns:
            Boolean indicating if conditions are met
        """
        if self.status == ContractStatus.EXECUTED.value:
            return False
        
        contract_type = self.contract_type
        
        if contract_type == ContractType.TIME_LOCK.value:
            # Check if unlock time has passed
            release_time = self.conditions.get('release_time', 0)
            return time.time() >= release_time
        
        elif contract_type == ContractType.ESCROW.value:
            # Check if approval condition is met
            required_approvals = self.conditions.get('required_approvals', [])
            received_approvals = self.conditions.get('received_approvals', [])
            
            # If required_approvals is an int, check count
            if isinstance(required_approvals, int):
                return len(received_approvals) >= required_approvals
            
            # Otherwise assume it's a list of specific addresses
            return all(addr in received_approvals for addr in required_approvals)
        
        elif contract_type == ContractType.CONDITIONAL.value:
            # Check custom conditions
            condition_type = self.conditions.get('condition_type')
            
            if condition_type == 'balance_threshold':
                # Check if address has minimum balance
                target_address = self.conditions.get('target_address')
                threshold = self.conditions.get('threshold', 0)
                balance = blockchain.get_balance(target_address)
                return balance >= threshold
            
            elif condition_type == 'block_height':
                # Check if blockchain reached certain height
                target_height = self.conditions.get('target_height', 0)
                return len(blockchain.chain) >= target_height
        
        elif contract_type == ContractType.RECURRING.value:
            # Check if next payment is due
            last_payment = self.conditions.get('last_payment_time', self.created_at)
            interval = self.conditions.get('interval', 0)
            payments_made = self.conditions.get('payments_made', 0)
            max_payments = self.conditions.get('max_payments', float('inf'))
            
            time_passed = time.time() - last_payment
            return time_passed >= interval and payments_made < max_payments
        
        return False
    
    def execute(self, blockchain) -> Dict[str, Any]:
        """
        Execute the contract and create transaction.
        
        Args:
            blockchain: Blockchain instance
            
        Returns:
            Execution result dictionary
        """
        if not self.check_conditions(blockchain):
            return {
                'success': False,
                'message': 'Contract conditions not met'
            }
        
        try:
            # Create transaction based on contract type
            from blockchain.transaction import Transaction
            
            if self.contract_type == ContractType.RECURRING.value:
                # For recurring, create single payment
                recipient = self.conditions.get('recipient')
                tx = Transaction(
                    sender_address=f"CONTRACT:{self.contract_id}",
                    recipient=recipient,
                    amount=self.amount,
                    signature="SMART_CONTRACT_EXECUTION"
                )
                
                # Update conditions for next payment
                self.conditions['payments_made'] = self.conditions.get('payments_made', 0) + 1
                self.conditions['last_payment_time'] = time.time()
                
                # Don't mark as executed if more payments remain
                if self.conditions['payments_made'] >= self.conditions.get('max_payments', 1):
                    self.status = ContractStatus.EXECUTED.value
                    self.executed_at = time.time()
            
            else:
                # For other types, single execution
                recipient = self.conditions.get('recipient') or self.participants[-1]
                tx = Transaction(
                    sender_address=f"CONTRACT:{self.contract_id}",
                    recipient=recipient,
                    amount=self.amount,
                    signature="SMART_CONTRACT_EXECUTION"
                )
                
                self.status = ContractStatus.EXECUTED.value
                self.executed_at = time.time()
            
            # Add transaction to blockchain
            blockchain.add_transaction(tx)
            
            self.execution_result = {
                'success': True,
                'transaction_hash': tx.calculate_hash(),
                'executed_at': self.executed_at or time.time()
            }
            
            return self.execution_result
            
        except Exception as e:
            self.status = ContractStatus.FAILED.value
            self.execution_result = {
                'success': False,
                'error': str(e)
            }
            return self.execution_result
    
    def add_approval(self, approver_address: str) -> bool:
        """
        Add approval from a participant (for escrow contracts).
        
        Args:
            approver_address: Address of approving party
            
        Returns:
            Boolean indicating if approval was added
        """
        if self.contract_type != ContractType.ESCROW.value:
            return False
        
        if approver_address not in self.participants:
            return False
        
        received_approvals = self.conditions.get('received_approvals', [])
        if approver_address not in received_approvals:
            received_approvals.append(approver_address)
            self.conditions['received_approvals'] = received_approvals
            return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contract to dictionary for serialization."""
        return {
            'contract_id': self.contract_id,
            'creator': self.creator,
            'contract_type': self.contract_type,
            'participants': self.participants,
            'amount': self.amount,
            'conditions': self.conditions,
            'metadata': self.metadata,
            'status': self.status,
            'created_at': self.created_at,
            'executed_at': self.executed_at,
            'execution_result': self.execution_result
        }


class SmartContractManager:
    """Manages all smart contracts in the system."""
    
    def __init__(self):
        """Initialize the smart contract manager."""
        self.contracts: Dict[str, SmartContract] = {}
    
    def create_contract(
        self,
        contract_id: str,
        creator: str,
        contract_type: str,
        participants: List[str],
        amount: float,
        conditions: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> SmartContract:
        """
        Create a new smart contract.
        
        Args:
            contract_id: Unique contract identifier
            creator: Address of contract creator
            contract_type: Type of contract
            participants: List of participant addresses
            amount: Amount locked in contract
            conditions: Conditions for execution
            metadata: Additional contract data
            
        Returns:
            Created SmartContract instance
            
        Raises:
            ValueError: If contract_id already exists
        """
        if contract_id in self.contracts:
            raise ValueError(f"Contract {contract_id} already exists")
        
        contract = SmartContract(
            contract_id=contract_id,
            creator=creator,
            contract_type=contract_type,
            participants=participants,
            amount=amount,
            conditions=conditions,
            metadata=metadata
        )
        
        contract.status = ContractStatus.ACTIVE.value
        self.contracts[contract_id] = contract
        return contract
    
    def get_contract(self, contract_id: str) -> Optional[SmartContract]:
        """Get contract by ID."""
        return self.contracts.get(contract_id)
    
    def get_contracts_by_participant(self, address: str) -> List[SmartContract]:
        """Get all contracts involving an address."""
        return [
            contract for contract in self.contracts.values()
            if address in contract.participants or address == contract.creator
        ]
    
    def get_pending_contracts(self) -> List[SmartContract]:
        """Get all contracts that haven't been executed."""
        return [
            contract for contract in self.contracts.values()
            if contract.status in [ContractStatus.ACTIVE.value, ContractStatus.PENDING.value]
        ]
    
    def check_and_execute_contracts(self, blockchain) -> List[Dict[str, Any]]:
        """
        Check all pending contracts and execute those with met conditions.
        
        Args:
            blockchain: Blockchain instance
            
        Returns:
            List of execution results
        """
        results = []
        pending_contracts = self.get_pending_contracts()
        
        for contract in pending_contracts:
            if contract.check_conditions(blockchain):
                result = contract.execute(blockchain)
                result['contract_id'] = contract.contract_id
                results.append(result)
        
        return results
    
    def add_approval(self, contract_id: str, approver_address: str) -> bool:
        """Add approval to an escrow contract."""
        contract = self.get_contract(contract_id)
        if not contract:
            return False
        return contract.add_approval(approver_address)
