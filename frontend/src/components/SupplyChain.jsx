/**
 * Supply Chain Management Component
 * 
 * Provides comprehensive supply chain tracking functionality including:
 * - Product registration and authentication
 * - Real-time tracking from origin to consumer
 * - Quality monitoring and safety alerts
 * - Counterfeit prevention through blockchain verification
 * 
 * Designed for food safety, pharmaceutical distribution, and general supply chain transparency.
 */

import React, { useState, useEffect } from 'react';
import { supplyChainAPI } from '../services/api';
import './SupplyChain.css';

function SupplyChain() {
  // State for product list and filtering
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [manufacturers, setManufacturers] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedManufacturer, setSelectedManufacturer] = useState('');
  
  // State for selected product details
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [productDetails, setProductDetails] = useState(null);
  
  // State for product registration form
  const [showRegisterForm, setShowRegisterForm] = useState(false);
  const [registerForm, setRegisterForm] = useState({
    product_id: '',
    name: '',
    category: '',
    manufacturer: '',
    manufacture_date: '',
    batch_number: '',
    initial_location: '',
    quantity: '',
    description: '',
    specifications: ''
  });
  
  // State for adding tracking events
  const [showEventForm, setShowEventForm] = useState(false);
  const [eventForm, setEventForm] = useState({
    event_type: 'transport',
    location: '',
    handler: '',
    description: '',
    temperature: '',
    humidity: ''
  });
  
  // State for product verification
  const [showVerifyForm, setShowVerifyForm] = useState(false);
  const [verifyProductId, setVerifyProductId] = useState('');
  const [verifyHash, setVerifyHash] = useState('');
  const [verificationResult, setVerificationResult] = useState(null);
  
  // State for alerts
  const [alertProducts, setAlertProducts] = useState([]);
  const [showAlerts, setShowAlerts] = useState(false);
  
  // Loading and error states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load initial data on component mount
  useEffect(() => {
    loadProducts();
    loadCategories();
    loadManufacturers();
    loadAlerts();
  }, []);

  // Filter products when category or manufacturer changes
  useEffect(() => {
    filterProducts();
  }, [selectedCategory, selectedManufacturer, products]);

  /**
   * Load all products from the supply chain system
   */
  const loadProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await supplyChainAPI.getAllProducts();
      setProducts(response.data.products || []);
    } catch (err) {
      setError('Failed to load products: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Load all available product categories
   */
  const loadCategories = async () => {
    try {
      const response = await supplyChainAPI.getCategories();
      setCategories(response.data.categories || []);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  };

  /**
   * Load all registered manufacturers
   */
  const loadManufacturers = async () => {
    try {
      const response = await supplyChainAPI.getManufacturers();
      setManufacturers(response.data.manufacturers || []);
    } catch (err) {
      console.error('Failed to load manufacturers:', err);
    }
  };

  /**
   * Load products with safety or quality alerts
   */
  const loadAlerts = async () => {
    try {
      const response = await supplyChainAPI.getProductsWithAlerts();
      setAlertProducts(response.data.products || []);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    }
  };

  /**
   * Clear all supply chain data
   */
  const clearAllData = async () => {
    if (!window.confirm('Are you sure you want to clear ALL supply chain data? This action cannot be undone.')) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Clear all products from the system
      const response = await supplyChainAPI.clearAllData();
      
      alert('All supply chain data has been cleared successfully');
      
      // Reset all state
      setProducts([]);
      setFilteredProducts([]);
      setCategories([]);
      setManufacturers([]);
      setAlertProducts([]);
      setSelectedProduct(null);
      setProductDetails(null);
      setSelectedCategory('');
      setSelectedManufacturer('');
      
    } catch (err) {
      setError('Failed to clear data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Filter products based on selected category and manufacturer
   */
  const filterProducts = () => {
    let filtered = [...products];

    if (selectedCategory) {
      filtered = filtered.filter(p => p.category === selectedCategory);
    }

    if (selectedManufacturer) {
      filtered = filtered.filter(p => p.manufacturer === selectedManufacturer);
    }

    setFilteredProducts(filtered);
  };

  /**
   * Register a new product in the supply chain
   */
  const handleRegisterProduct = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);

      // Prepare metadata from additional fields
      const metadata = {
        description: registerForm.description,
        specifications: registerForm.specifications
      };
      
      // Add quantity to metadata if provided
      if (registerForm.quantity) {
        metadata.quantity = registerForm.quantity;
      }

      // Create product registration payload
      const productData = {
        product_id: registerForm.product_id,
        name: registerForm.name,
        category: registerForm.category,
        manufacturer: registerForm.manufacturer,
        manufacture_date: registerForm.manufacture_date,
        batch_number: registerForm.batch_number,
        initial_location: registerForm.initial_location,
        metadata: metadata
      };

      const response = await supplyChainAPI.registerProduct(productData);
      
      alert('Product registered successfully and recorded on blockchain! Mine a block to permanently store this registration.');
      
      // Reset form and reload products
      setRegisterForm({
        product_id: '',
        name: '',
        category: '',
        manufacturer: '',
        manufacture_date: '',
        batch_number: '',
        initial_location: '',
        quantity: '',
        description: '',
        specifications: ''
      });
      
      setShowRegisterForm(false);
      await loadProducts();
      await loadCategories();
      await loadManufacturers();
      
    } catch (err) {
      setError('Failed to register product: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Load detailed information for a specific product
   */
  const handleSelectProduct = async (productId) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await supplyChainAPI.getProduct(productId);
      setProductDetails(response.data.product);
      setSelectedProduct(productId);
      setShowEventForm(false);
      
    } catch (err) {
      setError('Failed to load product details: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Add a tracking event to the selected product
   */
  const handleAddEvent = async (e) => {
    e.preventDefault();
    
    if (!selectedProduct) {
      setError('Please select a product first');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Prepare event metadata
      const metadata = {};
      if (eventForm.temperature) {
        metadata.temperature = eventForm.temperature;
      }
      if (eventForm.humidity) {
        metadata.humidity = eventForm.humidity;
      }

      // Create event payload
      const eventData = {
        event_type: eventForm.event_type,
        location: eventForm.location,
        handler: eventForm.handler,
        description: eventForm.description,
        metadata: metadata
      };

      await supplyChainAPI.addProductEvent(selectedProduct, eventData);
      
      alert('Event added successfully and recorded on blockchain! Mine a block to permanently store this event.');
      
      // Reset form and reload product details
      setEventForm({
        event_type: 'transport',
        location: '',
        handler: '',
        description: '',
        temperature: '',
        humidity: ''
      });
      
      setShowEventForm(false);
      await handleSelectProduct(selectedProduct);
      await loadProducts();
      
    } catch (err) {
      setError('Failed to add event: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Verify product authenticity using its hash
   */
  const handleVerifyProduct = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await supplyChainAPI.verifyProduct(verifyProductId, verifyHash);
      setVerificationResult(response.data);
      
    } catch (err) {
      setError('Verification failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Format timestamp to readable date string
   */
  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  /**
   * Copy text to clipboard
   */
  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    alert(`${label} copied to clipboard`);
  };

  return (
    <div className="supply-chain-container">
      <div className="supply-chain-header">
        <h1>Supply Chain Management</h1>
        <p className="header-description">
          Blockchain-based product tracking for transparency, authenticity verification, and safety monitoring
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
          <button onClick={() => setError(null)} className="close-btn">Close</button>
        </div>
      )}

      {/* Blockchain Integration Info */}
      <div className="blockchain-info-banner">
        <div className="info-icon">ℹ</div>
        <div className="info-content">
          <strong>Blockchain Integration:</strong> All product registrations and tracking events are recorded as transactions on the blockchain, ensuring immutability and transparency. Visit the Blockchain tab to see supply chain transactions. Mine blocks to permanently store pending transactions.
        </div>
      </div>

      {/* Action Buttons */}
      <div className="action-bar">
        <button 
          onClick={() => {
            setShowRegisterForm(!showRegisterForm);
            setShowEventForm(false);
            setShowVerifyForm(false);
            setShowAlerts(false);
          }}
          className="btn-primary"
        >
          {showRegisterForm ? 'Cancel Registration' : 'Register New Product'}
        </button>

        <button 
          onClick={() => {
            setShowVerifyForm(!showVerifyForm);
            setShowRegisterForm(false);
            setShowEventForm(false);
            setShowAlerts(false);
            setVerificationResult(null);
          }}
          className="btn-secondary"
        >
          {showVerifyForm ? 'Cancel Verification' : 'Verify Product'}
        </button>

        <button 
          onClick={() => {
            setShowAlerts(!showAlerts);
            setShowRegisterForm(false);
            setShowEventForm(false);
            setShowVerifyForm(false);
          }}
          className={alertProducts.length > 0 ? 'btn-alert' : 'btn-secondary'}
        >
          Safety Alerts ({alertProducts.length})
        </button>

        <button 
          onClick={() => {
            loadProducts();
            loadCategories();
            loadManufacturers();
            loadAlerts();
          }}
          className="btn-refresh"
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </button>

        <button 
          onClick={clearAllData}
          className="btn-danger"
          disabled={loading}
        >
          Clear All Data
        </button>
      </div>

      {/* Product Registration Form */}
      {showRegisterForm && (
        <div className="form-section">
          <h2>Register New Product</h2>
          <form onSubmit={handleRegisterProduct} className="registration-form">
            <div className="form-row">
              <div className="form-group">
                <label>Product ID</label>
                <input
                  type="text"
                  value={registerForm.product_id}
                  onChange={(e) => setRegisterForm({...registerForm, product_id: e.target.value})}
                  placeholder="Unique product identifier"
                  required
                />
              </div>

              <div className="form-group">
                <label>Product Name</label>
                <input
                  type="text"
                  value={registerForm.name}
                  onChange={(e) => setRegisterForm({...registerForm, name: e.target.value})}
                  placeholder="Product name"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Category</label>
                <input
                  type="text"
                  value={registerForm.category}
                  onChange={(e) => setRegisterForm({...registerForm, category: e.target.value})}
                  placeholder="e.g., Food, Pharmaceutical, Electronics"
                  list="category-suggestions"
                  required
                />
                <datalist id="category-suggestions">
                  <option value="Food" />
                  <option value="Pharmaceutical" />
                  <option value="Electronics" />
                  <option value="Textiles" />
                  <option value="Automotive" />
                </datalist>
              </div>

              <div className="form-group">
                <label>Manufacturer</label>
                <input
                  type="text"
                  value={registerForm.manufacturer}
                  onChange={(e) => setRegisterForm({...registerForm, manufacturer: e.target.value})}
                  placeholder="Manufacturing company"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Manufacture Date</label>
                <input
                  type="date"
                  value={registerForm.manufacture_date}
                  onChange={(e) => setRegisterForm({...registerForm, manufacture_date: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label>Batch Number</label>
                <input
                  type="text"
                  value={registerForm.batch_number}
                  onChange={(e) => setRegisterForm({...registerForm, batch_number: e.target.value})}
                  placeholder="Manufacturing batch number"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Initial Location</label>
              <input
                type="text"
                value={registerForm.initial_location}
                onChange={(e) => setRegisterForm({...registerForm, initial_location: e.target.value})}
                placeholder="Origin location (city, country)"
                required
              />
            </div>

            <div className="form-group">
              <label>Quantity</label>
              <input
                type="number"
                value={registerForm.quantity}
                onChange={(e) => setRegisterForm({...registerForm, quantity: e.target.value})}
                placeholder="Product quantity or units"
                min="0"
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                value={registerForm.description}
                onChange={(e) => setRegisterForm({...registerForm, description: e.target.value})}
                placeholder="Product description"
                rows="3"
              />
            </div>

            <div className="form-group">
              <label>Specifications</label>
              <textarea
                value={registerForm.specifications}
                onChange={(e) => setRegisterForm({...registerForm, specifications: e.target.value})}
                placeholder="Technical specifications, ingredients, materials, etc."
                rows="3"
              />
            </div>

            <button type="submit" disabled={loading} className="btn-submit">
              {loading ? 'Registering...' : 'Register Product'}
            </button>
          </form>
        </div>
      )}

      {/* Product Verification Form */}
      {showVerifyForm && (
        <div className="form-section">
          <h2>Verify Product Authenticity</h2>
          <p className="form-description">
            Enter the product ID and its authentication hash to verify if the product is genuine.
            This helps prevent counterfeiting and ensures product legitimacy.
          </p>
          
          <form onSubmit={handleVerifyProduct} className="verification-form">
            <div className="form-group">
              <label>Product ID</label>
              <input
                type="text"
                value={verifyProductId}
                onChange={(e) => setVerifyProductId(e.target.value)}
                placeholder="Enter product ID"
                required
              />
            </div>

            <div className="form-group">
              <label>Product Hash</label>
              <input
                type="text"
                value={verifyHash}
                onChange={(e) => setVerifyHash(e.target.value)}
                placeholder="Enter product authentication hash"
                required
              />
            </div>

            <button type="submit" disabled={loading} className="btn-submit">
              {loading ? 'Verifying...' : 'Verify Authenticity'}
            </button>
          </form>

          {verificationResult && (
            <div className={`verification-result ${verificationResult.authentic ? 'authentic' : 'not-authentic'}`}>
              <h3>{verificationResult.authentic ? 'Product is Authentic' : 'Verification Failed'}</h3>
              <p>{verificationResult.message}</p>
              {verificationResult.actual_hash && (
                <div className="hash-info">
                  <label>Actual Product Hash:</label>
                  <code>{verificationResult.actual_hash}</code>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Safety Alerts Section */}
      {showAlerts && (
        <div className="alerts-section">
          <h2>Safety and Quality Alerts</h2>
          {alertProducts.length === 0 ? (
            <p className="no-alerts">No safety alerts at this time</p>
          ) : (
            <div className="alerts-list">
              {alertProducts.map((product) => (
                <div key={product.product_id} className="alert-item">
                  <div className="alert-header">
                    <h3>{product.name}</h3>
                    <span className="product-id">ID: {product.product_id}</span>
                  </div>
                  <div className="alert-details">
                    <p><strong>Manufacturer:</strong> {product.manufacturer}</p>
                    <p><strong>Batch:</strong> {product.batch_number}</p>
                  </div>
                  <div className="alert-messages">
                    {product.safety_alerts && product.safety_alerts.map((alert, idx) => (
                      <div key={idx} className={`alert-message severity-${alert.severity}`}>
                        <span className="alert-severity">{alert.severity.toUpperCase()}</span>
                        <span className="alert-description">{alert.description}</span>
                        <span className="alert-location">{alert.location}</span>
                        <span className="alert-time">{formatDate(alert.timestamp)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Product List and Details */}
      <div className="main-content">
        {/* Product List */}
        <div className="product-list-section">
          <div className="section-header">
            <h2>Registered Products ({filteredProducts.length})</h2>
            
            {/* Filters */}
            <div className="filters">
              <select 
                value={selectedCategory} 
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="filter-select"
              >
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>

              <select 
                value={selectedManufacturer} 
                onChange={(e) => setSelectedManufacturer(e.target.value)}
                className="filter-select"
              >
                <option value="">All Manufacturers</option>
                {manufacturers.map(mfr => (
                  <option key={mfr} value={mfr}>{mfr}</option>
                ))}
              </select>

              {(selectedCategory || selectedManufacturer) && (
                <button 
                  onClick={() => {
                    setSelectedCategory('');
                    setSelectedManufacturer('');
                  }}
                  className="btn-clear-filters"
                >
                  Clear Filters
                </button>
              )}
            </div>
          </div>

          <div className="product-list">
            {loading && !selectedProduct ? (
              <p className="loading-message">Loading products...</p>
            ) : filteredProducts.length === 0 ? (
              <p className="no-products">No products found. Register a new product to get started.</p>
            ) : (
              filteredProducts.map((product) => (
                <div 
                  key={product.product_id} 
                  className={`product-item ${selectedProduct === product.product_id ? 'selected' : ''}`}
                  onClick={() => handleSelectProduct(product.product_id)}
                >
                  <div className="product-item-header">
                    <h3>{product.name}</h3>
                    <span className="product-category">{product.category}</span>
                  </div>
                  <div className="product-item-info">
                    <p><strong>ID:</strong> {product.product_id}</p>
                    <p><strong>Manufacturer:</strong> {product.manufacturer}</p>
                    <p><strong>Location:</strong> {product.current_location}</p>
                    <p><strong>Events:</strong> {product.events ? product.events.length : 0}</p>
                  </div>
                  {product.safety_alerts && product.safety_alerts.length > 0 && (
                    <div className="product-alert-badge">
                      {product.safety_alerts.length} Alert(s)
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Product Details */}
        {productDetails && (
          <div className="product-details-section">
            <div className="section-header">
              <h2>Product Details</h2>
              <button 
                onClick={() => setShowEventForm(!showEventForm)}
                className="btn-add-event"
              >
                {showEventForm ? 'Cancel' : 'Add Tracking Event'}
              </button>
            </div>

            {/* Add Event Form */}
            {showEventForm && (
              <div className="event-form">
                <h3>Add Tracking Event</h3>
                <form onSubmit={handleAddEvent}>
                  <div className="form-row">
                    <div className="form-group">
                      <label>Event Type</label>
                      <select
                        value={eventForm.event_type}
                        onChange={(e) => setEventForm({...eventForm, event_type: e.target.value})}
                        required
                      >
                        <option value="transport">Transport</option>
                        <option value="inspection">Inspection</option>
                        <option value="storage">Storage</option>
                        <option value="delivery">Delivery</option>
                        <option value="quality_check">Quality Check</option>
                        <option value="quality_alert">Quality Alert</option>
                        <option value="customs">Customs Clearance</option>
                        <option value="received">Received</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label>Location</label>
                      <input
                        type="text"
                        value={eventForm.location}
                        onChange={(e) => setEventForm({...eventForm, location: e.target.value})}
                        placeholder="Current location"
                        required
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Handler / Responsible Party</label>
                    <input
                      type="text"
                      value={eventForm.handler}
                      onChange={(e) => setEventForm({...eventForm, handler: e.target.value})}
                      placeholder="Company, warehouse, or person responsible"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Description</label>
                    <textarea
                      value={eventForm.description}
                      onChange={(e) => setEventForm({...eventForm, description: e.target.value})}
                      placeholder="Event description"
                      rows="3"
                      required
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Temperature (optional)</label>
                      <input
                        type="text"
                        value={eventForm.temperature}
                        onChange={(e) => setEventForm({...eventForm, temperature: e.target.value})}
                        placeholder="e.g., 5°C"
                      />
                    </div>

                    <div className="form-group">
                      <label>Humidity (optional)</label>
                      <input
                        type="text"
                        value={eventForm.humidity}
                        onChange={(e) => setEventForm({...eventForm, humidity: e.target.value})}
                        placeholder="e.g., 60%"
                      />
                    </div>
                  </div>

                  <button type="submit" disabled={loading} className="btn-submit">
                    {loading ? 'Adding Event...' : 'Add Event'}
                  </button>
                </form>
              </div>
            )}

            {/* Product Information */}
            <div className="details-card">
              <h3>Product Information</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <label>Product ID</label>
                  <span>{productDetails.product_id}</span>
                </div>
                <div className="detail-item">
                  <label>Name</label>
                  <span>{productDetails.name}</span>
                </div>
                <div className="detail-item">
                  <label>Category</label>
                  <span>{productDetails.category}</span>
                </div>
                <div className="detail-item">
                  <label>Manufacturer</label>
                  <span>{productDetails.manufacturer}</span>
                </div>
                <div className="detail-item">
                  <label>Manufacture Date</label>
                  <span>{productDetails.manufacture_date}</span>
                </div>
                <div className="detail-item">
                  <label>Batch Number</label>
                  <span>{productDetails.batch_number}</span>
                </div>
                <div className="detail-item">
                  <label>Current Location</label>
                  <span>{productDetails.current_location}</span>
                </div>
                <div className="detail-item">
                  <label>Registration Time</label>
                  <span>{formatDate(productDetails.registration_timestamp)}</span>
                </div>
              </div>

              <div className="authentication-hash">
                <label>Authentication Hash</label>
                <div className="hash-value">
                  <code>{productDetails.product_hash}</code>
                  <button 
                    onClick={() => copyToClipboard(productDetails.product_hash, 'Authentication hash')}
                    className="btn-copy"
                  >
                    Copy
                  </button>
                </div>
                <p className="hash-description">
                  This unique hash serves as a digital fingerprint for authenticity verification
                </p>
              </div>

              {productDetails.metadata && (
                <div className="metadata-section">
                  <h4>Additional Information</h4>
                  {productDetails.metadata.quantity && (
                    <p><strong>Quantity:</strong> {productDetails.metadata.quantity}</p>
                  )}
                  {productDetails.metadata.description && (
                    <p><strong>Description:</strong> {productDetails.metadata.description}</p>
                  )}
                  {productDetails.metadata.specifications && (
                    <p><strong>Specifications:</strong> {productDetails.metadata.specifications}</p>
                  )}
                </div>
              )}
            </div>

            {/* Tracking History */}
            <div className="details-card">
              <h3>Tracking History ({productDetails.events ? productDetails.events.length : 0} Events)</h3>
              
              {!productDetails.events || productDetails.events.length === 0 ? (
                <p className="no-events">No tracking events yet. Add the first event to start tracking.</p>
              ) : (
                <div className="timeline">
                  {productDetails.events.map((event, index) => (
                    <div key={index} className={`timeline-item event-type-${event.event_type}`}>
                      <div className="timeline-marker"></div>
                      <div className="timeline-content">
                        <div className="event-header">
                          <h4>{event.event_type.replace('_', ' ').toUpperCase()}</h4>
                          <span className="event-time">{formatDate(event.timestamp)}</span>
                        </div>
                        <div className="event-details">
                          <p><strong>Location:</strong> {event.location}</p>
                          <p><strong>Handler:</strong> {event.handler}</p>
                          <p><strong>Description:</strong> {event.description}</p>
                          {event.metadata && (
                            <div className="event-metadata">
                              {event.metadata.temperature && (
                                <span className="metadata-tag">Temp: {event.metadata.temperature}</span>
                              )}
                              {event.metadata.humidity && (
                                <span className="metadata-tag">Humidity: {event.metadata.humidity}</span>
                              )}
                              {event.metadata.severity && (
                                <span className={`metadata-tag severity-${event.metadata.severity}`}>
                                  {event.metadata.severity.toUpperCase()}
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                        <div className="event-hash">
                          <small>Hash: {event.event_hash.substring(0, 16)}...</small>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Safety Alerts */}
            {productDetails.safety_alerts && productDetails.safety_alerts.length > 0 && (
              <div className="details-card alerts-card">
                <h3>Safety Alerts</h3>
                <div className="alerts-list">
                  {productDetails.safety_alerts.map((alert, index) => (
                    <div key={index} className={`alert-item severity-${alert.severity}`}>
                      <div className="alert-badge">{alert.severity.toUpperCase()}</div>
                      <div className="alert-content">
                        <p>{alert.description}</p>
                        <p className="alert-meta">
                          <span>{alert.location}</span>
                          <span>{formatDate(alert.timestamp)}</span>
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default SupplyChain;
