import React, { useState, useEffect } from 'react';
import { walletAPI } from '../services/api';
import './Wallet.css';

function Wallet({ wallet, setWallet }) {
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showPrivateKey, setShowPrivateKey] = useState(false);

  useEffect(() => {
    if (wallet) {
      loadWalletData();
    }
  }, [wallet]);

  const createNewWallet = async () => {
    setLoading(true);
    try {
      const response = await walletAPI.createWallet();
      setWallet(response.data);
      setBalance(null);
      setTransactions([]);
      alert('Wallet created successfully! Please save your private key securely.');
    } catch (error) {
      console.error('Error creating wallet:', error);
      alert('Failed to create wallet. Please try again.');
    }
    setLoading(false);
  };

  const loadWalletData = async () => {
    if (!wallet) return;
    
    setLoading(true);
    try {
      const [balanceRes, transactionsRes] = await Promise.all([
        walletAPI.getBalance(wallet.address),
        walletAPI.getTransactions(wallet.address),
      ]);

      setBalance(balanceRes.data.balance);
      setTransactions(transactionsRes.data.transactions);
    } catch (error) {
      console.error('Error loading wallet data:', error);
      alert('Failed to load wallet data.');
    }
    setLoading(false);
  };

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    alert(`${label} copied to clipboard!`);
  };

  return (
    <div className="wallet">
      <h2 className="wallet-title">Wallet Management</h2>

      <div className="wallet-actions">
        <button
          className="create-wallet-button"
          onClick={createNewWallet}
          disabled={loading}
        >
          {loading ? 'Creating...' : 'Create New Wallet'}
        </button>

        {wallet && (
          <button
            className="load-data-button"
            onClick={loadWalletData}
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Refresh Wallet Data'}
          </button>
        )}
      </div>

      {wallet && (
        <div className="wallet-details">
          <div className="wallet-info-card">
            <h3>Wallet Information</h3>
            
            <div className="info-row">
              <label>Address:</label>
              <div className="info-value">
                <code className="address-code">{wallet.address}</code>
                <button
                  className="copy-button"
                  onClick={() => copyToClipboard(wallet.address, 'Address')}
                >
                  Copy
                </button>
              </div>
            </div>

            <div className="info-row">
              <label>Public Key:</label>
              <div className="info-value">
                <textarea
                  className="key-textarea"
                  value={wallet.public_key}
                  readOnly
                  rows="4"
                />
                <button
                  className="copy-button"
                  onClick={() => copyToClipboard(wallet.public_key, 'Public Key')}
                >
                  Copy
                </button>
              </div>
            </div>

            <div className="info-row">
              <label>Private Key:</label>
              <div className="info-value">
                <textarea
                  className="key-textarea"
                  value={showPrivateKey ? wallet.private_key : '••••••••••••••••••••'}
                  readOnly
                  rows="4"
                />
                <div className="key-actions">
                  <button
                    className="toggle-button"
                    onClick={() => setShowPrivateKey(!showPrivateKey)}
                  >
                    {showPrivateKey ? 'Hide' : 'Show'}
                  </button>
                  <button
                    className="copy-button"
                    onClick={() => copyToClipboard(wallet.private_key, 'Private Key')}
                  >
                    Copy
                  </button>
                </div>
              </div>
            </div>

            <div className="warning-box">
              <strong>Warning:</strong> Never share your private key with anyone.
            </div>
          </div>

          {balance !== null && (
            <div className="balance-card">
              <h3>Balance</h3>
              <div className="balance-amount">{balance} G2C</div>
              <div className="balance-label">Group2Coin</div>
            </div>
          )}

          {transactions.length > 0 && (
            <div className="transactions-card">
              <h3>Transaction History</h3>
              <div className="transactions-list">
                {transactions.map((tx, index) => (
                  <div key={index} className="transaction-item">
                    <div className="transaction-header">
                      <span className="transaction-type">
                        {tx.sender === wallet.public_key ? 'Sent' : 'Received'}
                      </span>
                      <span className="transaction-amount">
                        {tx.sender === wallet.public_key ? '-' : '+'}{tx.amount} G2C
                      </span>
                    </div>
                    <div className="transaction-details">
                      <div>Block: {tx.block_index}</div>
                      <div className="transaction-time">
                        {new Date(tx.timestamp * 1000).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!wallet && (
        <div className="empty-state">
          <p>No wallet loaded. Create a new wallet to get started.</p>
        </div>
      )}
    </div>
  );
}

export default Wallet;
