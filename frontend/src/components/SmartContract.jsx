/**
 * Smart Contract Component
 * 
 * Provides smart contract functionality including:
 * - Create different types of contracts (Escrow, Time-Lock, Conditional, Recurring)
 * - View all contracts
 * - Approve escrow contracts
 * - Execute contracts manually
 * - Check contract conditions
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SmartContract.css';

const API_BASE_URL = 'http://localhost:5000/api';

function SmartContract({ wallet }) {
  const [contracts, setContracts] = useState([]);
  const [selectedContract, setSelectedContract] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [contractType, setContractType] = useState('ESCROW');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  
  // Form state
  const [contractForm, setContractForm] = useState({
    contract_id: '',
    participants: '',
    amount: '',
    // Escrow specific
    required_approvals: '',
    // Time-lock specific
    release_time: '',
    // Conditional specific
    condition_type: 'balance_threshold',
    threshold_value: '',
    target_address: '',
    // Recurring specific
    interval_seconds: '',
    max_payments: ''
  });

  useEffect(() => {
    loadContracts();
  }, []);

  const loadContracts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/contracts`);
      setContracts(response.data.contracts);
      setError('');
    } catch (err) {
      setError('Failed to load contracts: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleCreateContract = async (e) => {
    e.preventDefault();
    
    if (!wallet) {
      setError('Please create a wallet first');
      return;
    }

    try {
      const participants = contractForm.participants.split(',').map(p => p.trim()).filter(p => p);
      
      if (participants.length === 0) {
        setError('Please enter at least one participant address');
        return;
      }

      let conditions = {};
      
      // Build conditions based on contract type
      switch (contractType) {
        case 'ESCROW':
          conditions = {
            required_approvals: parseInt(contractForm.required_approvals) || participants.length
          };
          break;
        case 'TIME_LOCK':
          if (!contractForm.release_time) {
            setError('Please enter release time');
            return;
          }
          const releaseTimestamp = new Date(contractForm.release_time).getTime() / 1000;
          conditions = {
            release_time: releaseTimestamp
          };
          break;
        case 'CONDITIONAL':
          conditions = {
            condition_type: contractForm.condition_type,
            threshold: parseFloat(contractForm.threshold_value),
            target_address: contractForm.target_address || wallet.address
          };
          break;
        case 'RECURRING':
          conditions = {
            interval: parseInt(contractForm.interval_seconds),
            max_payments: parseInt(contractForm.max_payments)
          };
          break;
        default:
          conditions = {};
      }

      const contractData = {
        contract_id: contractForm.contract_id || `contract_${Date.now()}`,
        creator: wallet.address,
        contract_type: contractType,
        participants: participants,
        amount: parseFloat(contractForm.amount),
        conditions: conditions,
        metadata: {
          created_at: new Date().toISOString(),
          description: `${contractType} contract`
        }
      };

      const response = await axios.post(`${API_BASE_URL}/contracts/create`, contractData);
      
      setMessage(`Contract created successfully: ${response.data.contract.contract_id}`);
      setError('');
      setShowCreateForm(false);
      resetForm();
      loadContracts();
      
      setTimeout(() => setMessage(''), 5000);
    } catch (err) {
      setError('Failed to create contract: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleApproveContract = async (contractId) => {
    if (!wallet) {
      setError('Please create a wallet first');
      return;
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/contracts/${contractId}/approve`, {
        approver: wallet.address
      });
      
      setMessage(`Approval added successfully`);
      setError('');
      loadContracts();
      
      if (selectedContract?.contract_id === contractId) {
        setSelectedContract(response.data.contract);
      }
      
      setTimeout(() => setMessage(''), 5000);
    } catch (err) {
      setError('Failed to approve: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleExecuteContract = async (contractId) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/contracts/${contractId}/execute`);
      
      if (response.data.execution_result.success) {
        setMessage(`Contract executed successfully! Transaction: ${response.data.execution_result.transaction_id}`);
      } else {
        setError(`Execution failed: ${response.data.execution_result.message}`);
      }
      
      loadContracts();
      
      setTimeout(() => {
        setMessage('');
        setError('');
      }, 5000);
    } catch (err) {
      setError('Failed to execute: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleCheckExecuteAll = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/contracts/check-execute`);
      setMessage(response.data.message);
      loadContracts();
      
      setTimeout(() => setMessage(''), 5000);
    } catch (err) {
      setError('Failed to check and execute: ' + (err.response?.data?.error || err.message));
    }
  };

  const viewContractDetails = async (contractId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/contracts/${contractId}`);
      setSelectedContract(response.data.contract);
      setError('');
    } catch (err) {
      setError('Failed to load contract details: ' + (err.response?.data?.error || err.message));
    }
  };

  const resetForm = () => {
    setContractForm({
      contract_id: '',
      participants: '',
      amount: '',
      required_approvals: '',
      release_time: '',
      condition_type: 'balance_threshold',
      threshold_value: '',
      target_address: '',
      interval_seconds: '',
      max_payments: ''
    });
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'PENDING': return 'status-pending';
      case 'ACTIVE': return 'status-active';
      case 'EXECUTED': return 'status-executed';
      case 'FAILED': return 'status-failed';
      case 'EXPIRED': return 'status-expired';
      default: return '';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  return (
    <div className="smart-contract-container">
      <div className="smart-contract-header">
        <h1>Smart Contracts</h1>
        <p className="subtitle">Create and manage automated blockchain contracts</p>
      </div>

      {message && (
        <div className="message-banner success">
          {message}
        </div>
      )}

      {error && (
        <div className="message-banner error">
          {error}
        </div>
      )}

      <div className="contract-actions">
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? 'Cancel' : 'Create New Contract'}
        </button>
        <button 
          className="btn btn-secondary"
          onClick={handleCheckExecuteAll}
        >
          Check & Execute Ready Contracts
        </button>
        <button 
          className="btn btn-secondary"
          onClick={loadContracts}
        >
          Refresh Contracts
        </button>
      </div>

      {showCreateForm && (
        <div className="create-contract-form">
          <h2>Create Smart Contract</h2>
          
          <div className="form-group">
            <label>Contract Type</label>
            <select 
              value={contractType} 
              onChange={(e) => setContractType(e.target.value)}
              className="form-control"
            >
              <option value="ESCROW">Escrow (Multi-Party Approval)</option>
              <option value="TIME_LOCK">Time-Lock (Scheduled Release)</option>
              <option value="CONDITIONAL">Conditional (Trigger-Based)</option>
              <option value="RECURRING">Recurring (Periodic Payments)</option>
            </select>
          </div>

          <form onSubmit={handleCreateContract}>
            <div className="form-row">
              <div className="form-group">
                <label>Contract ID (optional)</label>
                <input
                  type="text"
                  className="form-control"
                  value={contractForm.contract_id}
                  onChange={(e) => setContractForm({...contractForm, contract_id: e.target.value})}
                  placeholder="Auto-generated if empty"
                />
              </div>

              <div className="form-group">
                <label>Amount</label>
                <input
                  type="number"
                  step="0.01"
                  className="form-control"
                  value={contractForm.amount}
                  onChange={(e) => setContractForm({...contractForm, amount: e.target.value})}
                  required
                  placeholder="Contract amount"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Participants (comma-separated addresses)</label>
              <textarea
                className="form-control"
                value={contractForm.participants}
                onChange={(e) => setContractForm({...contractForm, participants: e.target.value})}
                required
                placeholder="Enter participant addresses separated by commas"
                rows="2"
              />
            </div>

            {/* Contract Type Specific Fields */}
            {contractType === 'ESCROW' && (
              <div className="form-group">
                <label>Required Approvals</label>
                <input
                  type="number"
                  className="form-control"
                  value={contractForm.required_approvals}
                  onChange={(e) => setContractForm({...contractForm, required_approvals: e.target.value})}
                  placeholder="Number of approvals needed (default: all participants)"
                />
                <small>Leave empty to require all participants to approve</small>
              </div>
            )}

            {contractType === 'TIME_LOCK' && (
              <div className="form-group">
                <label>Release Time</label>
                <input
                  type="datetime-local"
                  className="form-control"
                  value={contractForm.release_time}
                  onChange={(e) => setContractForm({...contractForm, release_time: e.target.value})}
                  required
                />
                <small>Funds will be released at this time</small>
              </div>
            )}

            {contractType === 'CONDITIONAL' && (
              <>
                <div className="form-group">
                  <label>Condition Type</label>
                  <select
                    className="form-control"
                    value={contractForm.condition_type}
                    onChange={(e) => setContractForm({...contractForm, condition_type: e.target.value})}
                  >
                    <option value="balance_threshold">Balance Threshold</option>
                    <option value="block_height">Block Height</option>
                  </select>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Threshold Value</label>
                    <input
                      type="number"
                      step="0.01"
                      className="form-control"
                      value={contractForm.threshold_value}
                      onChange={(e) => setContractForm({...contractForm, threshold_value: e.target.value})}
                      required
                      placeholder={contractForm.condition_type === 'balance_threshold' ? 'Minimum balance' : 'Block number'}
                    />
                  </div>

                  {contractForm.condition_type === 'balance_threshold' && (
                    <div className="form-group">
                      <label>Target Address (optional)</label>
                      <input
                        type="text"
                        className="form-control"
                        value={contractForm.target_address}
                        onChange={(e) => setContractForm({...contractForm, target_address: e.target.value})}
                        placeholder="Your address if empty"
                      />
                    </div>
                  )}
                </div>
              </>
            )}

            {contractType === 'RECURRING' && (
              <div className="form-row">
                <div className="form-group">
                  <label>Interval (seconds)</label>
                  <input
                    type="number"
                    className="form-control"
                    value={contractForm.interval_seconds}
                    onChange={(e) => setContractForm({...contractForm, interval_seconds: e.target.value})}
                    required
                    placeholder="Time between payments"
                  />
                  <small>3600 = 1 hour, 86400 = 1 day</small>
                </div>

                <div className="form-group">
                  <label>Maximum Payments</label>
                  <input
                    type="number"
                    className="form-control"
                    value={contractForm.max_payments}
                    onChange={(e) => setContractForm({...contractForm, max_payments: e.target.value})}
                    required
                    placeholder="Total number of payments"
                  />
                </div>
              </div>
            )}

            <div className="form-actions">
              <button type="submit" className="btn btn-primary">Create Contract</button>
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={() => {
                  setShowCreateForm(false);
                  resetForm();
                }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="contracts-section">
        <h2>All Contracts ({contracts.length})</h2>
        
        <div className="contracts-grid">
          {contracts.map((contract) => (
            <div key={contract.contract_id} className="contract-card">
              <div className="contract-card-header">
                <h3>{contract.contract_id}</h3>
                <span className={`status-badge ${getStatusBadgeClass(contract.status)}`}>
                  {contract.status}
                </span>
              </div>
              
              <div className="contract-details">
                <div className="detail-row">
                  <span className="detail-label">Type:</span>
                  <span className="detail-value">{contract.contract_type}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Amount:</span>
                  <span className="detail-value">{contract.amount} G2C</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Creator:</span>
                  <span className="detail-value address">{contract.creator.substring(0, 20)}...</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Participants:</span>
                  <span className="detail-value">{contract.participants.length}</span>
                </div>
                
                {contract.contract_type === 'ESCROW' && (
                  <div className="detail-row">
                    <span className="detail-label">Approvals:</span>
                    <span className="detail-value">
                      {contract.approvals?.length || 0} / {contract.conditions.required_approvals}
                    </span>
                  </div>
                )}
                
                {contract.contract_type === 'TIME_LOCK' && contract.conditions.release_time && (
                  <div className="detail-row">
                    <span className="detail-label">Release:</span>
                    <span className="detail-value">{formatTimestamp(contract.conditions.release_time)}</span>
                  </div>
                )}
                
                {contract.executed_at && (
                  <div className="detail-row">
                    <span className="detail-label">Executed:</span>
                    <span className="detail-value">{formatTimestamp(contract.executed_at)}</span>
                  </div>
                )}
              </div>
              
              <div className="contract-actions-grid">
                <button 
                  className="btn btn-small btn-info"
                  onClick={() => viewContractDetails(contract.contract_id)}
                >
                  View Details
                </button>
                
                {contract.status === 'ACTIVE' && contract.contract_type === 'ESCROW' && (
                  <button 
                    className="btn btn-small btn-success"
                    onClick={() => handleApproveContract(contract.contract_id)}
                  >
                    Approve
                  </button>
                )}
                
                {(contract.status === 'ACTIVE' || contract.status === 'PENDING') && (
                  <button 
                    className="btn btn-small btn-primary"
                    onClick={() => handleExecuteContract(contract.contract_id)}
                  >
                    Execute
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
        
        {contracts.length === 0 && (
          <div className="empty-state">
            <p>No contracts created yet</p>
            <p>Create your first smart contract to get started!</p>
          </div>
        )}
      </div>

      {selectedContract && (
        <div className="contract-modal-overlay" onClick={() => setSelectedContract(null)}>
          <div className="contract-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Contract Details</h2>
              <button className="close-btn" onClick={() => setSelectedContract(null)}>×</button>
            </div>
            
            <div className="modal-content">
              <div className="detail-section">
                <h3>Basic Information</h3>
                <div className="detail-row">
                  <span className="detail-label">Contract ID:</span>
                  <span className="detail-value">{selectedContract.contract_id}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Type:</span>
                  <span className="detail-value">{selectedContract.contract_type}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Status:</span>
                  <span className={`status-badge ${getStatusBadgeClass(selectedContract.status)}`}>
                    {selectedContract.status}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Amount:</span>
                  <span className="detail-value">{selectedContract.amount} G2C</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Creator:</span>
                  <span className="detail-value address">{selectedContract.creator}</span>
                </div>
              </div>
              
              <div className="detail-section">
                <h3>Participants</h3>
                {selectedContract.participants.map((participant, index) => (
                  <div key={index} className="participant-item">
                    <span className="address">{participant}</span>
                  </div>
                ))}
              </div>
              
              <div className="detail-section">
                <h3>Conditions</h3>
                <pre className="conditions-json">
                  {JSON.stringify(selectedContract.conditions, null, 2)}
                </pre>
              </div>
              
              {selectedContract.approvals && selectedContract.approvals.length > 0 && (
                <div className="detail-section">
                  <h3>Approvals ({selectedContract.approvals.length})</h3>
                  {selectedContract.approvals.map((approval, index) => (
                    <div key={index} className="approval-item">
                      <span className="address">{approval}</span>
                    </div>
                  ))}
                </div>
              )}
              
              {selectedContract.transaction_id && (
                <div className="detail-section">
                  <h3>Execution</h3>
                  <div className="detail-row">
                    <span className="detail-label">Transaction ID:</span>
                    <span className="detail-value">{selectedContract.transaction_id}</span>
                  </div>
                  {selectedContract.executed_at && (
                    <div className="detail-row">
                      <span className="detail-label">Executed At:</span>
                      <span className="detail-value">{formatTimestamp(selectedContract.executed_at)}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SmartContract;
