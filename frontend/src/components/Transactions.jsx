import React, { useState, useEffect } from 'react';
import { transactionAPI } from '../services/api';
import './Transactions.css';

function Transactions({ wallet }) {
  const [formData, setFormData] = useState({
    senderPublicKey: '',
    senderPrivateKey: '',
    recipientAddress: '',
    amount: '',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (wallet) {
      setFormData(prev => ({
        ...prev,
        senderPublicKey: wallet.public_key,
        senderPrivateKey: wallet.private_key,
      }));
    }
  }, [wallet]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.senderPublicKey || !formData.senderPrivateKey || 
        !formData.recipientAddress || !formData.amount) {
      alert('Please fill in all fields');
      return;
    }

    const amount = parseFloat(formData.amount);
    if (isNaN(amount) || amount <= 0) {
      alert('Please enter a valid amount greater than 0');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await transactionAPI.createTransaction(
        formData.senderPublicKey,
        formData.recipientAddress,
        amount,
        formData.senderPrivateKey
      );

      setResult({
        success: true,
        message: 'Transaction submitted successfully!',
        data: response.data
      });

      setFormData(prev => ({
        ...prev,
        recipientAddress: '',
        amount: '',
      }));
    } catch (error) {
      setResult({
        success: false,
        message: error.response?.data?.error || 'Failed to create transaction',
        data: null
      });
    }

    setLoading(false);
  };

  const clearForm = () => {
    setFormData({
      senderPublicKey: wallet ? wallet.public_key : '',
      senderPrivateKey: wallet ? wallet.private_key : '',
      recipientAddress: '',
      amount: '',
    });
    setResult(null);
  };

  return (
    <div className="transactions">
      <h2 className="transactions-title">Send Group2Coin</h2>

      {!wallet && (
        <div className="warning-banner">
          <strong>Note:</strong> Create a wallet first to send transactions. Go to the Wallet tab to create one.
        </div>
      )}

      <div className="transaction-form-container">
        <form className="transaction-form" onSubmit={handleSubmit}>
          <div className="form-group full-width">
            <label htmlFor="senderPublicKey">Your Public Key</label>
            <textarea
              id="senderPublicKey"
              name="senderPublicKey"
              value={formData.senderPublicKey}
              onChange={handleInputChange}
              placeholder="Paste your public key here"
              rows="4"
              required
            />
          </div>

          <div className="form-group full-width">
            <label htmlFor="senderPrivateKey">Your Private Key</label>
            <textarea
              id="senderPrivateKey"
              name="senderPrivateKey"
              value={formData.senderPrivateKey}
              onChange={handleInputChange}
              placeholder="Paste your private key here"
              rows="4"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="recipientAddress">Recipient Address</label>
            <input
              type="text"
              id="recipientAddress"
              name="recipientAddress"
              value={formData.recipientAddress}
              onChange={handleInputChange}
              placeholder="Enter recipient wallet address"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="amount">Amount (G2C)</label>
            <input
              type="number"
              id="amount"
              name="amount"
              value={formData.amount}
              onChange={handleInputChange}
              placeholder="0.00"
              step="0.01"
              min="0.01"
              required
            />
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="submit-button"
              disabled={loading}
            >
              {loading ? 'Processing...' : 'Send Transaction'}
            </button>
            <button
              type="button"
              className="clear-button"
              onClick={clearForm}
              disabled={loading}
            >
              Clear Form
            </button>
          </div>
        </form>

        {result && (
          <div className={`result-box ${result.success ? 'success' : 'error'}`}>
            <h3>{result.success ? 'Success' : 'Error'}</h3>
            <p>{result.message}</p>
            {result.success && result.data && (
              <div className="transaction-details">
                <p className="pending-note">
                  Your transaction is now pending. It will be included in the next mined block.
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="info-box">
        <h3>How to Send Transactions</h3>
        <ol>
          <li>Create or load a wallet with sufficient balance</li>
          <li>Your keys will auto-fill if you have a wallet</li>
          <li>Get the recipient's wallet address</li>
          <li>Enter the amount you want to send</li>
          <li>Submit the transaction</li>
        </ol>
      </div>
    </div>
  );
}

export default Transactions;
