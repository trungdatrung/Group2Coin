/**
 * Main App component managing navigation and view state
 */
import React, { useState } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import Wallet from './components/Wallet';
import Transactions from './components/Transactions';
import Mining from './components/Mining';
import BlockchainViewer from './components/BlockchainViewer';
import TourListing from './components/TourListing';
import MyBookings from './components/MyBookings';
import TourManagement from './components/TourManagement';
import './App.css';

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
        return <Transactions />;
      case 'mining':
        return <Mining />;
      case 'blockchain':
        return <BlockchainViewer />;
      case 'tours':
        return <TourListing wallet={wallet} />;
      case 'my-bookings':
        return <MyBookings wallet={wallet} />;
      case 'admin-tours':
        return <TourManagement wallet={wallet} />;
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