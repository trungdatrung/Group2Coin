import React, { useState } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import Wallet from './components/Wallet';
import Transactions from './components/Transactions';
import Mining from './components/Mining';
import BlockchainViewer from './components/BlockchainViewer';
import SupplyChain from './components/SupplyChain';
import './components/App.css';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [wallet, setWallet] = useState(null);

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'wallet':
        return <Wallet wallet={wallet} setWallet={setWallet} />;
      case 'transactions':
        return <Transactions wallet={wallet} />;
      case 'mining':
        return <Mining wallet={wallet} />;
      case 'blockchain':
        return <BlockchainViewer />;
      case 'supplychain':
        return <SupplyChain />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Header currentView={currentView} setCurrentView={setCurrentView} />
      <main className="main-content">
        {renderView()}
      </main>
      <footer className="footer">
        <div className="footer-content">
          <p>Group2Coin Blockchain Platform</p>
          <p className="footer-note">Built with Python, Flask, and React</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
