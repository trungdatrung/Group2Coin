# Group2Coin - Blockchain + Travel Booking Platform

Group2Coin is a full-stack educational blockchain application with an integrated travel & tour booking system.

**Stack:**
- Backend: Python 3 + Flask REST API
- Frontend: React 18 with Axios
- Blockchain: SHA-256 hashing, RSA-2048 signatures, proof-of-work mining
- Travel System: In-memory tour/booking/review management

---

## Quick Start (Development)

**Requirements:**
- Python 3.8+
- Node.js 16+ / npm

### 1. Start Backend

```bash
cd backend
python3 -m venv venv        # create if needed
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Backend runs on `http://localhost:5000` with API at `/api` and `/travel`.

### 2. Start Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000` and calls `http://localhost:5000` for APIs.

## Build (Production)

```bash
npm --prefix frontend run build
# Serve frontend/build/ with a static server
```

---

## API Reference

### Blockchain Endpoints (`/api`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/blockchain` | Full chain, difficulty, mining reward, pending transactions |
| GET | `/blockchain/pending` | Pending transactions |
| GET | `/blockchain/validate` | Chain validity status |
| POST | `/wallet/create` | Create new wallet (returns address, keys) |
| GET | `/wallet/<addr>/balance` | Get wallet balance |
| GET | `/wallet/<addr>/transactions` | Get wallet's transactions |
| POST | `/transaction/create` | Create & sign transaction |
| POST | `/mine` | Mine pending transactions (body: `{miner_address}`) |

### Travel Endpoints (`/travel`)

#### Admin Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/tour/create` | Create new tour |
| PUT | `/admin/tour/<id>/update` | Update tour details |
| GET | `/admin/tours/<addr>` | Get all tours by admin |
| GET | `/admin/bookings/<addr>` | Get all bookings for admin's tours |
| GET | `/admin/stats/<addr>` | Get admin stats (revenue, bookings, etc.) |

#### User Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tours` | List all available tours |
| GET | `/tours/<id>` | Get tour details |
| POST | `/booking/create` | Create booking for tour |
| POST | `/booking/<id>/confirm` | Confirm booking (after payment) |
| POST | `/booking/<id>/cancel` | Cancel pending booking |
| GET | `/user/bookings/<addr>` | Get user's bookings |

#### Review Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/review/add` | Submit review for completed tour |
| GET | `/reviews/<tour_id>` | Get all reviews for tour |

---

## Features

### Blockchain Features
- ✅ Wallet creation (RSA-2048 key pairs)
- ✅ Transaction creation & digital signatures
- ✅ Proof-of-work mining (difficulty 4)
- ✅ Full chain validation
- ✅ Real-time blockchain viewer
- ✅ Transaction history & balance tracking

### Travel & Booking Features
- ✅ Admin tour creation with pricing, dates, itinerary
- ✅ User tour browsing with search/filtering
- ✅ Booking creation with participant validation
- ✅ Booking management (view, cancel, confirm)
- ✅ Rating & review system (1-5 stars)
- ✅ Admin dashboard with stats (revenue, bookings, tours)
- ✅ Responsive UI for mobile/desktop

### Frontend Components

**Blockchain:**
- Dashboard - Real-time stats
- Wallet - Create/import/manage wallets
- Transactions - Send coins
- Mining - Mine blocks
- BlockchainViewer - Explore full chain

**Travel:**
- TourListing - Browse tours with detail modal
- BookingForm - Create bookings with validation
- MyBookings - View user's bookings (pending/confirmed/completed)
- TourManagement - Admin panel (create tours, view bookings, stats)
- Reviews - Rate and review completed tours

---

## Recent Changes & Fixes

**Travel System Integration (Latest)**
- Added TourManagement admin component with stats dashboard
- Created MyBookings user view with booking status filtering
- Implemented Review system with star ratings and comments
- Wired BookingForm to TourListing detail modal
- All components integrated with backend travel API endpoints

**Blockchain Fixes**
- `/api/blockchain` now includes `pending_transactions` array
- BlockchainViewer guards against missing data (defensive coding)
- Dashboard refresh button now shows loading state & disable while fetching

**Repository Hygiene**
- Added `.gitignore` for venv, `__pycache__`, node_modules, build artifacts
- Updated README with practical quick-start guide
- Cleaned up git tracking (removed build/cache files)

---

## Architecture Notes

### Travel System Design
- **Manager Pattern**: `TravelManager` handles all tour/booking/review state (in-memory)
- **Models**: `Tour`, `Booking`, `Review` classes with `to_dict()` serialization
- **API Structure**: Admin routes under `/admin/*`, user routes under `/tours`, `/booking/*`, `/user/*`
- **Status Flow**: Booking → pending → confirmed (after payment) → completed

### Blockchain Design
- **In-Memory Storage**: Wallets and blockchain stored in Flask memory (ephemeral)
- **UTXO Model**: Balance calculated by summing all transactions
- **Difficulty Adjustment**: Current difficulty = 4 (leading zeros in hash)
- **Proof-of-Work**: Requires finding valid nonce that hashes to target

### Payment Integration (Todo)
- Currently bookings are created but payment confirmation uses placeholder fields
- Future: Integrate blockchain transactions for payment confirmation
- Design: When booking → confirm, validate G2C payment tx hash on backend

---

## Testing

Run backend smoke test:

```bash
python3 backend/test_setup.py
```

Tests:
- Blockchain initialization
- Transaction creation & signing
- Block mining
- Chain validation

---

## Development TODOs

- [ ] Persist wallets to file/database (currently ephemeral)
- [ ] Wire booking confirmation to blockchain transactions (payment validation)
- [ ] Add authentication/authorization layer for admin routes
- [ ] Unit tests for blockchain functions
- [ ] E2E test for booking → payment → review flow
- [ ] Tour search/filter on frontend
- [ ] Notification system for booking updates
- [ ] Refund handling for cancelled bookings

---

## Directory Structure

```
backend/
├── api/                    # Blockchain API routes
│   ├── routes.py
│   └── __init__.py
├── blockchain/
│   ├── block.py
│   ├── blockchain.py
│   ├── transaction.py
│   └── __init__.py
├── travel/                 # Travel/booking system
│   ├── manager.py         # Data models & business logic
│   ├── routes.py          # API endpoints
│   └── __init__.py
├── wallet/
│   ├── wallet.py
│   └── __init__.py
├── utils/
│   ├── crypto.py
│   └── __init__.py
├── main.py                # Flask app factory
├── requirements.txt
└── test_setup.py

frontend/
├── src/
│   ├── components/
│   │   ├── App.jsx                 # Main app with routing
│   │   ├── Header.jsx              # Navigation
│   │   ├── Dashboard.jsx           # Blockchain overview
│   │   ├── Wallet.jsx
│   │   ├── Transactions.jsx
│   │   ├── Mining.jsx
│   │   ├── BlockchainViewer.jsx
│   │   ├── TourListing.jsx         # Browse tours
│   │   ├── BookingForm.jsx         # Create booking
│   │   ├── MyBookings.jsx          # User's bookings
│   │   ├── TourManagement.jsx      # Admin panel
│   │   ├── Reviews.jsx             # Rating/reviews
│   │   └── *.css                   # Component styles
│   ├── services/
│   │   ├── api.js                  # Blockchain API client
│   │   └── travel.js               # Travel API client
│   ├── App.css
│   ├── index.js
│   └── index.css
├── public/
├── build/                  # Production build (npm run build)
└── package.json
```

---

## How to Use

### For Users

1. **Create Wallet**: Go to Wallet tab, click "Create Wallet", save your keys
2. **Mine Coins** (Optional): Go to Mining, click "Mine" to earn 50 G2C per block
3. **Browse Tours**: Go to "Tours" tab, click any tour to see details
4. **Book Tour**: Click "Book Now" in tour detail, fill participant count and requests
5. **View Bookings**: Go to "My Bookings" to see status and manage reservations
6. **Leave Review**: After tour completes, click "Leave a Review" and rate it

### For Admins

1. Go to "Admin Panel" tab
2. Create tours with title, description, location, pricing, dates
3. View all your tours, bookings, and revenue stats
4. Monitor booking confirmations

---

## Security Notes

- **Private Keys**: Never share or commit to git. Downloaded wallet files are local-only
- **In-Memory Storage**: Data is lost on server restart (dev only, add DB for production)
- **Signatures**: All transactions must be signed with private key
- **Wallet Addresses**: Derived from public key hash (SHA-256)

---

## License

Educational use only. Add LICENSE file before sharing publicly.

---

## Support

For questions or issues, see the code comments and API routes for implementation details.
