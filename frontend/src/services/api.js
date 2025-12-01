import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const blockchainAPI = {
  getBlockchain: () => api.get('/blockchain'),
  validateBlockchain: () => api.get('/blockchain/validate'),
  getPendingTransactions: () => api.get('/blockchain/pending'),
  getDifficulty: () => api.get('/blockchain/difficulty'),
};

export const walletAPI = {
  createWallet: () => api.post('/wallet/create'),
  getBalance: (address) => api.get(`/wallet/${address}/balance`),
  getTransactions: (address) => api.get(`/wallet/${address}/transactions`),
  
  exportWallet: async (address) => {
    try {
      const response = await api.get(`/wallet/export/${address}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `wallet_${address.substring(0, 8)}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      return { success: true };
    } catch (error) {
      console.error('Export wallet error:', error);
      throw error;
    }
  },
  
  importWallet: (walletData) => {
    return api.post('/wallet/import', { wallet_data: walletData });
  },
  
  loadWalletByAddress: (address) => {
    return api.get(`/wallet/load/${address}`);
  },
  
  validateWallet: (address, publicKey, privateKey) => {
    return api.post('/wallet/validate', {
      address: address,
      public_key: publicKey,
      private_key: privateKey
    });
  }
};

export const transactionAPI = {
  createTransaction: (senderPublicKey, recipientAddress, amount, senderPrivateKey) => {
    return api.post('/transaction/create', {
      sender: senderPublicKey,
      recipient: recipientAddress,
      amount: amount,
      private_key: senderPrivateKey
    });
  },
  getPendingTransactions: () => api.get('/transaction/pending'),
};

export const miningAPI = {
  mineBlock: (minerAddress) => {
    return api.post('/mine', {
      miner_address: minerAddress
    });
  },
  getDifficulty: () => api.get('/blockchain/difficulty'),
  getReward: () => api.get('/blockchain/reward'),
};

export const supplyChainAPI = {
  // Register a new product in the supply chain
  registerProduct: (productData) => {
    return api.post('/supplychain/product/register', productData);
  },
  
  // Add a tracking event to a product
  addProductEvent: (productId, eventData) => {
    return api.post(`/supplychain/product/${productId}/event`, eventData);
  },
  
  // Get detailed information about a specific product
  getProduct: (productId) => {
    return api.get(`/supplychain/product/${productId}`);
  },
  
  // Verify product authenticity using its hash
  verifyProduct: (productId, productHash) => {
    return api.post(`/supplychain/product/${productId}/verify`, {
      product_hash: productHash
    });
  },
  
  // Get all products with optional filtering
  getAllProducts: (category = null, manufacturer = null) => {
    let url = '/supplychain/products';
    const params = new URLSearchParams();
    
    if (category) params.append('category', category);
    if (manufacturer) params.append('manufacturer', manufacturer);
    
    const queryString = params.toString();
    if (queryString) url += `?${queryString}`;
    
    return api.get(url);
  },
  
  // Get products that have safety or quality alerts
  getProductsWithAlerts: () => {
    return api.get('/supplychain/products/alerts');
  },
  
  // Get list of all product categories
  getCategories: () => {
    return api.get('/supplychain/categories');
  },
  
  // Get list of all manufacturers
  getManufacturers: () => {
    return api.get('/supplychain/manufacturers');
  }
};

export default api;