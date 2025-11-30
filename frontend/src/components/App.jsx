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
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [wallet, setWallet] = useState(null);

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard key="dashboard" />;
      case 'wallet':
        return <Wallet key="wallet" wallet={wallet} setWallet={setWallet} />;
      case 'transactions':
        return <Transactions key="transactions" wallet={wallet} />;
      case 'mining':
        return <Mining key="mining" wallet={wallet} />;
      case 'blockchain':
        return <BlockchainViewer key="blockchain" />;
      case 'tours':
        return (
          <ErrorBoundary key="tours">
            <TourListing wallet={wallet} />
          </ErrorBoundary>
        );
      case 'my-bookings':
        return (
          <ErrorBoundary key="my-bookings">
            <MyBookings wallet={wallet} />
          </ErrorBoundary>
        );
      case 'admin-tours':
        return (
          <ErrorBoundary key="admin-tours">
            <TourManagement wallet={wallet} />
          </ErrorBoundary>
        );
      default:
        return <Dashboard key="dashboard" />;
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