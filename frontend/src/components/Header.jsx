import React from 'react';
import './Header.css';

function Header({ currentView, setCurrentView }) {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title">
          <h1>Group2Coin</h1>
          <span className="header-subtitle">Blockchain Platform</span>
        </div>
        
        <nav className="header-nav">
          <button
            className={`nav-button ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentView('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`nav-button ${currentView === 'wallet' ? 'active' : ''}`}
            onClick={() => setCurrentView('wallet')}
          >
            Wallet
          </button>
          <button
            className={`nav-button ${currentView === 'transactions' ? 'active' : ''}`}
            onClick={() => setCurrentView('transactions')}
          >
            Transactions
          </button>
          <button
            className={`nav-button ${currentView === 'mining' ? 'active' : ''}`}
            onClick={() => setCurrentView('mining')}
          >
            Mining
          </button>
          <button
            className={`nav-button ${currentView === 'blockchain' ? 'active' : ''}`}
            onClick={() => setCurrentView('blockchain')}
          >
            Blockchain
          </button>
          <button
            className={`nav-button ${currentView === 'supplychain' ? 'active' : ''}`}
            onClick={() => setCurrentView('supplychain')}
          >
            Supply Chain
          </button>
        </nav>
      </div>
    </header>
  );
}

export default Header;
