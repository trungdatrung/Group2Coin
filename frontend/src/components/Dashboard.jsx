import React, { useState, useEffect } from 'react';
import { blockchainAPI } from '../services/api';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState({
    totalBlocks: 0,
    pendingTransactions: 0,
    difficulty: 0,
    isValid: true,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [blockchainRes, pendingRes, difficultyRes, validationRes] = await Promise.all([
        blockchainAPI.getBlockchain(),
        blockchainAPI.getPendingTransactions(),
        blockchainAPI.getDifficulty(),
        blockchainAPI.validateBlockchain(),
      ]);

      setStats({
        totalBlocks: blockchainRes.data.chain.length,
        pendingTransactions: pendingRes.data.pending_transactions.length,
        difficulty: difficultyRes.data.difficulty,
        isValid: validationRes.data.valid,
      });
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      // keep previous stats but show error state briefly
      setLoading(false);
      alert('Failed to refresh dashboard data. Is the backend running?');
    }
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Loading dashboard data...</div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <h2 className="dashboard-title">Blockchain Overview</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Blocks</div>
          <div className="stat-value">{stats.totalBlocks}</div>
          <div className="stat-description">Blocks in the chain</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Pending Transactions</div>
          <div className="stat-value">{stats.pendingTransactions}</div>
          <div className="stat-description">Waiting to be mined</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Mining Difficulty</div>
          <div className="stat-value">{stats.difficulty}</div>
          <div className="stat-description">Current difficulty level</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Chain Status</div>
          <div className={`stat-value ${stats.isValid ? 'valid' : 'invalid'}`}>
            {stats.isValid ? 'Valid' : 'Invalid'}
          </div>
          <div className="stat-description">Blockchain integrity</div>
        </div>
      </div>

      <div className="info-section">
        <h3>About Group2Coin</h3>
        <p>
          Group2Coin is a blockchain-based cryptocurrency platform built with Python and React.
          This dashboard provides real-time information about the blockchain network.
        </p>
      </div>

      <button className="refresh-button" onClick={loadDashboardData} disabled={loading}>
        {loading ? 'Refreshing...' : 'Refresh Data'}
      </button>
    </div>
  );
}

export default Dashboard;
