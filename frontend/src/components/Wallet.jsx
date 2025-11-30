import React, { useState, useEffect } from 'react';
import { walletAPI } from '../services/api';
import './Wallet.css';

function Wallet({ wallet, setWallet }) {
  // State for wallet data
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [showPrivateKey, setShowPrivateKey] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // State for importing wallet
  const [showImport, setShowImport] = useState(false);
  const [importMethod, setImportMethod] = useState('file');
  const [importData, setImportData] = useState({
    address: '',
    publicKey: '',
    privateKey: ''
  });

  // State for loading wallet by address
  const [loadAddress, setLoadAddress] = useState('');
  const [loadedWalletInfo, setLoadedWalletInfo] = useState(null);

  // Load wallet data when wallet changes
  useEffect(() => {
    if (wallet) {
      loadWalletData();
    }
  }, [wallet]);

  // Function to load wallet balance and transactions
  const loadWalletData = async () => {
    if (!wallet) return;
    
    try {
      const balanceRes = await walletAPI.getBalance(wallet.address);
      setBalance(balanceRes.data.balance);
      
      const txRes = await walletAPI.getTransactions(wallet.address);
      setTransactions(txRes.data.transactions || []);
    } catch (error) {
      console.error('Error loading wallet data:', error);
    }
  };

  // Create a new wallet
  const createNewWallet = async () => {
    try {
      setLoading(true);
      const response = await walletAPI.createWallet();
      setWallet(response.data);
      alert('Wallet created successfully! Please save your private key safely.');
    } catch (error) {
      alert('Failed to create wallet: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Export wallet to JSON file
  const handleExportWallet = async () => {
    if (!wallet) {
      alert('No wallet to export');
      return;
    }
    
    try {
      setLoading(true);
      await walletAPI.exportWallet(wallet.address);
      alert('Wallet exported successfully!');
    } catch (error) {
      alert('Failed to export wallet: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Import wallet from file
  const handleFileImport = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const walletData = JSON.parse(e.target.result);
        await importWalletData(walletData);
      } catch (error) {
        alert('Invalid wallet file: ' + error.message);
      }
    };
    reader.readAsText(file);
  };

  // Import wallet manually
  const handleManualImport = async () => {
    if (!importData.address || !importData.publicKey || !importData.privateKey) {
      alert('Please fill in all fields');
      return;
    }

    const walletData = {
      address: importData.address,
      public_key: importData.publicKey,
      private_key: importData.privateKey
    };

    await importWalletData(walletData);
  };

  // Import wallet data (common function)
  const importWalletData = async (walletData) => {
    try {
      setLoading(true);
      
      // Validate wallet first
      const validateRes = await walletAPI.validateWallet(
        walletData.address,
        walletData.public_key,
        walletData.private_key
      );

      if (!validateRes.data.valid) {
        alert('Invalid wallet keys: ' + validateRes.data.error);
        return;
      }

      // Import the wallet
      const response = await walletAPI.importWallet(walletData);
      
      // Set as current wallet
      setWallet({
        address: walletData.address,
        public_key: walletData.public_key,
        private_key: walletData.private_key
      });

      alert(`Wallet imported successfully! Balance: ${response.data.wallet.balance} G2C`);
      setShowImport(false);
      setImportData({ address: '', publicKey: '', privateKey: '' });
      
    } catch (error) {
      alert('Failed to import wallet: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Load wallet information by address
  const handleLoadByAddress = async () => {
    if (!loadAddress) {
      alert('Please enter a wallet address');
      return;
    }

    try {
      setLoading(true);
      const response = await walletAPI.loadWalletByAddress(loadAddress);
      setLoadedWalletInfo(response.data);
    } catch (error) {
      alert('Failed to load wallet: ' + error.message);
      setLoadedWalletInfo(null);
    } finally {
      setLoading(false);
    }
  };

  // Copy text to clipboard
  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    alert(`${label} copied to clipboard!`);
  };

  return (
    <div className="wallet-container">
      <h2>Wallet Management</h2>

      {/* Action Buttons */}
      <div className="wallet-actions">
        <button onClick={createNewWallet} disabled={loading} className="btn-primary">
          {loading ? 'Creating...' : 'Create New Wallet'}
        </button>
        
        {wallet && (
          <button onClick={handleExportWallet} disabled={loading} className="btn-success">
            {loading ? 'Exporting...' : 'Export Wallet'}
          </button>
        )}
        
        <button 
          onClick={() => setShowImport(!showImport)} 
          className="btn-info"
        >
          {showImport ? 'Cancel Import' : 'Import Wallet'}
        </button>
      </div>

      {/* Import Wallet Section */}
      {showImport && (
        <div className="import-section">
          <h3>Import Wallet</h3>
          
          <div className="import-method-toggle">
            <button
              className={importMethod === 'file' ? 'active' : ''}
              onClick={() => setImportMethod('file')}
            >
              Import from File
            </button>
            <button
              className={importMethod === 'manual' ? 'active' : ''}
              onClick={() => setImportMethod('manual')}
            >
              Manual Entry
            </button>
          </div>

          {importMethod === 'file' ? (
            <div className="file-import">
              <input
                type="file"
                accept=".json"
                onChange={handleFileImport}
                disabled={loading}
              />
              <p className="help-text">Select a wallet JSON file to import</p>
            </div>
          ) : (
            <div className="manual-import">
              <input
                type="text"
                placeholder="Wallet Address"
                value={importData.address}
                onChange={(e) => setImportData({...importData, address: e.target.value})}
              />
              <textarea
                placeholder="Public Key"
                value={importData.publicKey}
                onChange={(e) => setImportData({...importData, publicKey: e.target.value})}
                rows="4"
              />
              <textarea
                placeholder="Private Key"
                value={importData.privateKey}
                onChange={(e) => setImportData({...importData, privateKey: e.target.value})}
                rows="4"
              />
              <button 
                onClick={handleManualImport} 
                disabled={loading}
                className="btn-primary"
              >
                {loading ? 'Importing...' : 'Import Wallet'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Current Wallet Info */}
      {wallet && (
        <div className="wallet-info">
          <h3>Your Wallet</h3>
          
          <div className="info-group">
            <label>Address:</label>
            <div className="info-value">
              <code>{wallet.address}</code>
              <button onClick={() => copyToClipboard(wallet.address, 'Address')}>
                Copy
              </button>
            </div>
          </div>

          <div className="info-group">
            <label>Balance:</label>
            <div className="balance-display">
              {balance !== null ? `${balance} G2C` : 'Loading...'}
            </div>
          </div>

          <div className="info-group">
            <label>Public Key:</label>
            <div className="info-value">
              <code>{wallet.public_key.substring(0, 50)}...</code>
              <button onClick={() => copyToClipboard(wallet.public_key, 'Public Key')}>
                Copy
              </button>
            </div>
          </div>

          <div className="info-group">
            <label>Private Key:</label>
            <div className="info-value">
              <code>
                {showPrivateKey 
                  ? wallet.private_key.substring(0, 50) + '...'
                  : '••••••••••••••••••••••••••••••••'}
              </code>
              <button onClick={() => setShowPrivateKey(!showPrivateKey)}>
                {showPrivateKey ? 'Hide' : 'Show'}
              </button>
              {showPrivateKey && (
                <button onClick={() => copyToClipboard(wallet.private_key, 'Private Key')}>
                  Copy
                </button>
              )}
            </div>
          </div>

          {transactions.length > 0 && (
            <div className="transactions-list">
              <h4>Recent Transactions</h4>
              {transactions.slice(0, 5).map((tx, index) => (
                <div key={index} className="transaction-item">
                  <span>{tx.type === 'received' ? 'Received' : 'Sent'}</span>
                  <span>{tx.amount} G2C</span>
                  <span className="tx-time">{new Date(tx.timestamp).toLocaleString()}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Load Wallet by Address */}
      <div className="load-wallet-section">
        <h3>View Any Wallet</h3>
        <div className="load-wallet-input">
          <input
            type="text"
            placeholder="Enter wallet address to view"
            value={loadAddress}
            onChange={(e) => setLoadAddress(e.target.value)}
          />
          <button onClick={handleLoadByAddress} disabled={loading}>
            {loading ? 'Loading...' : 'Load'}
          </button>
        </div>

        {loadedWalletInfo && (
          <div className="loaded-wallet-info">
            <h4>Wallet Information</h4>
            <p><strong>Address:</strong> {loadedWalletInfo.address}</p>
            <p><strong>Balance:</strong> {loadedWalletInfo.balance} G2C</p>
            <p><strong>Total Received:</strong> {loadedWalletInfo.statistics.total_received} G2C</p>
            <p><strong>Total Sent:</strong> {loadedWalletInfo.statistics.total_sent} G2C</p>
            <p><strong>Transactions:</strong> {loadedWalletInfo.statistics.transaction_count}</p>
            
            {loadedWalletInfo.transactions.length > 0 && (
              <div className="loaded-transactions">
                <h5>Recent Transactions:</h5>
                {loadedWalletInfo.transactions.slice(0, 10).map((tx, index) => (
                  <div key={index} className="transaction-item">
                    <span>{tx.type === 'received' ? 'Received' : 'Sent'}</span>
                    <span>{tx.amount} G2C</span>
                    <span className="tx-block">Block #{tx.block_index}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Security Warning */}
      <div className="wallet-warning">
        <strong>Security Warning:</strong> Never share your private key with anyone! 
        It gives full access to your wallet.
      </div>
    </div>
  );
}

export default Wallet;