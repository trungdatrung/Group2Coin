import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const blockchainAPI = {
  getBlockchain: () => api.get('/blockchain'),
  validateBlockchain: () => api.get('/blockchain/validate'),
  getDifficulty: () => api.get('/difficulty'),
  setDifficulty: (difficulty) => api.post('/difficulty', { difficulty }),
  getPendingTransactions: () => api.get('/pending-transactions'),
};

export const walletAPI = {
  createWallet: () => api.post('/wallet/create'),
  getBalance: (address) => api.get(`/wallet/${address}/balance`),
  getTransactions: (address) => api.get(`/wallet/${address}/transactions`),
};

export const transactionAPI = {
  createTransaction: (sender, recipient, amount, privateKey) =>
    api.post('/transaction/create', {
      sender,
      recipient,
      amount,
      private_key: privateKey,
    }),
};

export const miningAPI = {
  mineBlock: (minerAddress) => api.post('/mine', { miner_address: minerAddress }),
};

export default api;
