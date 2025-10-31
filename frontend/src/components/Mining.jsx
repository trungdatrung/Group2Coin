import React, { useState, useEffect } from 'react';
import { miningAPI, blockchainAPI } from '../services/api';
import './Mining.css';

function Mining({ wallet }) {
  const [minerAddress, setMinerAddress] = useState('');
  const [mining, setMining] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);
  const [difficulty, setDifficulty] = useState(4);
  const [newDifficulty, setNewDifficulty] = useState(4);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (wallet && wallet.address) {
      setMinerAddress(wallet.address);
    }
  }, [wallet]);

  useEffect(() => {
    loadMiningData();
    const interval = setInterval(loadMiningData, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadMiningData = async () => {
    try {
      const [pendingRes, difficultyRes] = await Promise.all([
        blockchainAPI.getPendingTransactions(),
        blockchainAPI.getDifficulty(),
      ]);

      setPendingCount(pendingRes.data.pending_transactions.length);
      setDifficulty(difficultyRes.data.difficulty);
      setNewDifficulty(difficultyRes.data.difficulty);
    } catch (error) {
      console.error('Error loading mining data:', error);
    }
  };

  const handleMine = async () => {
    if (!minerAddress) {
      alert('Please enter your miner address');
      return;
    }

    setMining(true);
    setResult(null);

    try {
      const response = await miningAPI.mineBlock(minerAddress);
      setResult({
        success: true,
        message: 'Block mined successfully!',
        data: response.data
      });
      await loadMiningData();
    } catch (error) {
      setResult({
        success: false,
        message: error.response?.data?.error || 'Failed to mine block',
        data: null
      });
    }

    setMining(false);
  };

  const handleDifficultyChange = async () => {
    const diffValue = parseInt(newDifficulty);
    
    if (isNaN(diffValue) || diffValue < 1 || diffValue > 10) {
      alert('Difficulty must be between 1 and 10');
      return;
    }

    try {
      await blockchainAPI.setDifficulty(diffValue);
      setDifficulty(diffValue);
      alert('Mining difficulty updated successfully!');
      await loadMiningData();
    } catch (error) {
      alert('Failed to update difficulty: ' + (error.response?.data?.error || error.message));
    }
  };

  return (
    <div className="mining">
      <h2 className="mining-title">Mining Dashboard</h2>

      {!wallet && (
        <div className="warning-banner">
          <strong>Note:</strong> Create a wallet first to receive mining rewards. Go to the Wallet tab to create one.
        </div>
      )}

      <div className="mining-stats">
        <div className="stat-card-mining">
          <div className="stat-label-mining">Pending Transactions</div>
          <div className="stat-value-mining">{pendingCount}</div>
          <div className="stat-description-mining">
            {pendingCount === 0 ? 'No transactions to mine' : 'Ready to mine'}
          </div>
        </div>

        <div className="stat-card-mining">
          <div className="stat-label-mining">Current Difficulty</div>
          <div className="stat-value-mining">{difficulty}</div>
          <div className="stat-description-mining">Mining complexity level</div>
        </div>

        <div className="stat-card-mining">
          <div className="stat-label-mining">Block Reward</div>
          <div className="stat-value-mining">50 G2C</div>
          <div className="stat-description-mining">Reward per mined block</div>
        </div>
      </div>

      <div className="mining-section">
        <h3>Mine New Block</h3>
        <div className="mining-form">
          <div className="form-group-mining">
            <label htmlFor="minerAddress">Your Miner Address</label>
            <input
              type="text"
              id="minerAddress"
              value={minerAddress}
              onChange={(e) => setMinerAddress(e.target.value)}
              placeholder="Enter your wallet address to receive mining reward"
              disabled={mining}
            />
          </div>

          <button
            className="mine-button"
            onClick={handleMine}
            disabled={mining}
          >
            {mining ? 'Mining in progress...' : 'Start Mining'}
          </button>

          {mining && (
            <div className="mining-progress">
              <div className="progress-spinner"></div>
              <p>Mining block with difficulty {difficulty}...</p>
              <p className="progress-note">This may take some time</p>
            </div>
          )}
        </div>

        {result && (
          <div className={`result-box-mining ${result.success ? 'success' : 'error'}`}>
            <h3>{result.success ? 'Mining Successful' : 'Mining Failed'}</h3>
            <p>{result.message}</p>
            {result.success && result.data && (
              <div className="mining-result-details">
                <p><strong>Block Index:</strong> {result.data.block.index}</p>
                <p><strong>Transactions:</strong> {result.data.block.transactions.length}</p>
                <p className="reward-note">You have earned 50 G2C mining reward!</p>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="difficulty-section">
        <h3>Adjust Mining Difficulty</h3>
        <div className="difficulty-form">
          <div className="form-group-mining">
            <label htmlFor="newDifficulty">New Difficulty Level (1-10)</label>
            <input
              type="number"
              id="newDifficulty"
              value={newDifficulty}
              onChange={(e) => setNewDifficulty(e.target.value)}
              min="1"
              max="10"
            />
          </div>
          <button className="difficulty-button" onClick={handleDifficultyChange}>
            Update Difficulty
          </button>
        </div>
      </div>
    </div>
  );
}

export default Mining;
