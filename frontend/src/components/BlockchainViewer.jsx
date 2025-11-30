import React, { useState, useEffect } from 'react';
import { blockchainAPI } from '../services/api';
import './BlockchainViewer.css';

function BlockchainViewer() {
  const [blockchain, setBlockchain] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedBlocks, setExpandedBlocks] = useState(new Set([0]));

  useEffect(() => {
    loadBlockchain();
  }, []);

  const loadBlockchain = async () => {
    setLoading(true);
    try {
      const response = await blockchainAPI.getBlockchain();
      setBlockchain(response.data);
    } catch (error) {
      console.error('Error loading blockchain:', error);
      alert('Failed to load blockchain data');
    }
    setLoading(false);
  };

  const toggleBlock = (index) => {
    setExpandedBlocks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const expandAll = () => {
    if (blockchain) {
      const allIndices = blockchain.chain.map((_, index) => index);
      setExpandedBlocks(new Set(allIndices));
    }
  };

  const collapseAll = () => {
    setExpandedBlocks(new Set());
  };

  if (loading) {
    return (
      <div className="blockchain-viewer">
        <div className="loading">Loading blockchain data...</div>
      </div>
    );
  }

  if (!blockchain) {
    return (
      <div className="blockchain-viewer">
        <div className="error">Failed to load blockchain</div>
      </div>
    );
  }

  return (
    <div className="blockchain-viewer">
      <div className="viewer-header">
        <h2 className="viewer-title">Blockchain Explorer</h2>
        <div className="viewer-actions">
          <button className="action-button" onClick={expandAll}>
            Expand All
          </button>
          <button className="action-button" onClick={collapseAll}>
            Collapse All
          </button>
          <button className="action-button refresh" onClick={loadBlockchain}>
            Refresh
          </button>
        </div>
      </div>

      <div className="blockchain-info">
        <div className="info-item">
          <span className="info-label">Total Blocks:</span>
          <span className="info-value">{blockchain.chain.length}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Difficulty:</span>
          <span className="info-value">{blockchain.difficulty}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Mining Reward:</span>
          <span className="info-value">{blockchain.mining_reward} G2C</span>
        </div>
        <div className="info-item">
          <span className="info-label">Pending Transactions:</span>
          <span className="info-value">{blockchain.pending_transactions ? blockchain.pending_transactions.length : 0}</span>
        </div>
      </div>

      <div className="blocks-container">
        {blockchain.chain.map((block, index) => (
          <div key={index} className="block-card">
            <div className="block-header" onClick={() => toggleBlock(index)}>
              <div className="block-header-left">
                <span className="block-index">Block #{block.index}</span>
                {block.index === 0 && <span className="genesis-badge">Genesis</span>}
              </div>
              <div className="block-header-right">
                <span className="block-time">
                  {new Date(block.timestamp * 1000).toLocaleString()}
                </span>
                <span className={`expand-icon ${expandedBlocks.has(index) ? 'expanded' : ''}`}>
                  ▼
                </span>
              </div>
            </div>

            {expandedBlocks.has(index) && (
              <div className="block-content">
                <div className="block-field">
                  <label>Hash:</label>
                  <code className="hash-code">{block.hash}</code>
                </div>

                <div className="block-field">
                  <label>Previous Hash:</label>
                  <code className="hash-code">{block.previous_hash}</code>
                </div>

                <div className="block-field">
                  <label>Nonce:</label>
                  <span>{block.nonce}</span>
                </div>

                <div className="block-field">
                  <label>Transactions ({block.transactions.length}):</label>
                  <div className="transactions-container">
                    {(block.transactions || []).map((tx, txIndex) => (
                      <div key={txIndex} className="transaction-card">
                        <div className="transaction-row">
                          <span className="tx-label">From:</span>
                          <span className="tx-value">
                            {tx && tx.sender === 'GENESIS' ? 'GENESIS BLOCK' :
                             tx && tx.sender === 'MINING_REWARD' ? 'MINING REWARD' :
                             tx && tx.sender ? `${tx.sender.substring(0, 30)}...` : 'Unknown'}
                          </span>
                        </div>
                        <div className="transaction-row">
                          <span className="tx-label">To:</span>
                          <span className="tx-value">
                            {tx && tx.recipient === 'GENESIS' ? 'GENESIS BLOCK' :
                             tx && tx.recipient ? `${tx.recipient.substring(0, 30)}...` : 'Unknown'}
                          </span>
                        </div>
                        <div className="transaction-row">
                          <span className="tx-label">Amount:</span>
                          <span className="tx-amount">{tx.amount} G2C</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default BlockchainViewer;
