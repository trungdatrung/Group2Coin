# Travel System Debugging & Testing Guide

## What Was Fixed

### 1. **Component Navigation Issue** ✅
**Problem**: Clicking "Tours" button showed dashboard instead of tours
**Solution**: 
- Added ErrorBoundary component to catch rendering errors
- Added unique `key` props to each view so React properly unmounts/remounts components
- Fixed Dashboard interval cleanup to prevent memory leaks
- Dashboard no longer interferes with other component states

### 2. **Error Handling** ✅
**Problem**: Silent failures, no error messages visible to user
**Solution**:
- Created ErrorBoundary.jsx that displays errors in a user-friendly way
- Wrapped all travel components (TourListing, MyBookings, TourManagement) with error boundary
- Added console logging for debugging

### 3. **API Debugging** ✅
**Problem**: Couldn't see if API calls were working
**Solution**:
- Added axios interceptors to travel.js service
- All API calls now logged to browser console
- Can see exact request/response data

---

## How to Test

### Step 1: Start Both Servers

**Terminal 1 - Backend:**
```bash
cd /home/gnurt/Documents/Group2Coin/backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd /home/gnurt/Documents/Group2Coin/frontend
npm start
```

### Step 2: Open Browser Console
Press `F12` to open Developer Tools → Console tab
(Keep this open while testing - you'll see API logs here)

### Step 3: Test Tours Tab

1. Click the "Tours" button in navbar
2. **Expected**: Should show "No tours available yet" with a Refresh button
3. **If error**: Check ErrorBoundary message and console logs
4. **Console should show**: 
   ```
   Travel API Response: /tours {total: 0, tours: []}
   ```

### Step 4: Create a Test Tour

**Option A: Using curl (from terminal 3)**
```bash
curl -X POST http://localhost:5000/travel/admin/tour/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Tour",
    "description": "A test tour description",
    "location": "Test Location",
    "price": 100,
    "start_date": "2025-06-01",
    "end_date": "2025-06-05",
    "max_participants": 10,
    "admin_address": "admin123",
    "duration_days": 5,
    "itinerary": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]
  }'
```

**Option B: Using Admin Panel (from UI)**
1. Create a wallet first (go to Wallet tab, click "Create Wallet")
2. Go to "Admin Panel" tab
3. Fill in tour creation form and submit

### Step 5: Verify Tour Appears

1. Go back to "Tours" tab
2. Click the Refresh button (or manually refresh page)
3. **Expected**: Tour card should appear showing title, location, price
4. **Console**: Should see API response with tour data

### Step 6: Test Tour Detail

1. Click on a tour card
2. **Expected**: Modal opens showing full tour details
3. **Check**: Title, description, itinerary, dates, price per person, availability

### Step 7: Test Other Travel Features

**MyBookings:**
1. Create wallet first
2. Go to "My Bookings" tab
3. Should show "No bookings yet" initially
4. Try to book a tour from Tours tab

**Admin Panel:**
1. Create wallet first
2. Go to "Admin Panel" tab
3. Should show stats dashboard
4. Create tours and see them listed

---

## Troubleshooting

### Issue: Tours tab shows blank/nothing
**Solution**:
1. Open console (F12)
2. Look for red errors
3. Look for Travel API Response logs
4. Check if backend is running: `curl http://localhost:5000/travel/tours`

### Issue: Error message in ErrorBoundary
**Solution**:
1. Read the error message carefully
2. Check browser console for full error stack
3. Check backend logs for API errors
4. Try reloading page (Ctrl+F5)

### Issue: API calls show as failed in console
**Solution**:
1. Verify backend is running on port 5000
2. Check if travel routes are registered: `curl http://localhost:5000/travel/tours`
3. Check CORS headers: `curl -I http://localhost:5000/travel/tours`

### Issue: Wallet won't load in MyBookings/Admin Panel
**Solution**:
1. Go to Wallet tab first
2. Click "Create Wallet" or import existing wallet
3. Wallet address should appear
4. Then navigate to MyBookings/Admin Panel

---

## Console Logs You Should See

### Successful Tour List:
```
Travel API Response: /tours {total: 2, tours: [{tour_id: "...", title: "Paris City Tour", ...}]}
Tours API Response: /tours tours [Object, Object]
```

### Successful Tour Detail:
```
Travel API Response: /tours/tour-id-here {tour: {...}, reviews: [], average_rating: 0, review_count: 0}
```

### If Something's Wrong:
```
Travel API Error: /tours GET http://localhost:5000/travel/tours 404 Not Found
```

---

## Quick Status Check Commands

```bash
# Test travel API is working
curl http://localhost:5000/travel/tours

# Test blockchain API (should NOT affect travel)
curl http://localhost:5000/api/blockchain

# Test CORS headers are set
curl -I http://localhost:5000/travel/tours

# Check backend is running
ps aux | grep "python main.py"
```

---

## If Travel System Still Not Working

1. **Rebuild frontend**: `cd frontend && npm run build`
2. **Restart both servers**: Kill and restart backend + frontend
3. **Clear browser cache**: Ctrl+Shift+Del in browser
4. **Check git latest changes**: `git log --oneline | head -5`
5. **Check for errors in console** and report them

---

**Files Changed in This Fix:**
- `frontend/src/components/App.jsx` - Added ErrorBoundary, unique keys
- `frontend/src/components/ErrorBoundary.jsx` - New error boundary component
- `frontend/src/components/ErrorBoundary.css` - Error boundary styling
- `frontend/src/components/Dashboard.jsx` - Fixed interval cleanup
- `frontend/src/components/TourListing.jsx` - Improved empty states
- `frontend/src/services/travel.js` - Added API logging interceptors

