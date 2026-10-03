# 🍽️ UberEats Restaurant Scraper - Complete Guide

## 📋 Overview

This is a **fully automated, production-ready UberEats scraper** that:
- ✅ Automatically selects states/cities
- ✅ Scrolls through entire restaurant listings
- ✅ Filters by rating (≥4.0), reviews (≥100), and excludes chains
- ✅ Extracts restaurant names and addresses
- ✅ Saves to CSV with duplicate prevention
- ✅ Handles errors gracefully with retry logic
- ✅ Provides detailed progress tracking

---

## 🚀 Quick Start

### Prerequisites

Make sure you have the virtual environment activated:

```bash
cd e:\mailScraping
.\.venv\Scripts\Activate.ps1
```

Install required packages (one-time):
```bash
pip install playwright
playwright install chromium
```

### Run the Scraper

**Option 1: Use the Launcher (Recommended)**
```bash
python scraper_launcher.py
```

Then follow the prompts to:
1. Select a state (e.g., TX, CA, FL)
2. Confirm the cities to scrape
3. Wait for scraping to complete

**Option 2: Run Directly**
```bash
python uber_scraper_enhanced.py
```

---

## 📁 Project Structure

```
uberdata/
├── uber_scraper_enhanced.py    # Main scraper (fully automated)
├── scraper_launcher.py          # User-friendly launcher
├── SCRAPER_GUIDE.md             # This file
├── ubereats_data/               # Output directory
│   └── restaurants_TX_20260421_143022.csv
└── __pycache__/
```

---

## ⚙️ Configuration

Edit `uber_scraper_enhanced.py` to customize:

```python
CONFIG = {
    'MIN_RATING': 4.0,              # Minimum rating filter
    'MIN_REVIEWS': 100,             # Minimum reviews filter
    'BROWSER_HEADLESS': False,      # Show browser window
    'BROWSER_TIMEOUT': 30000,       # Page load timeout (ms)
    'SCROLL_PAUSE': 1.0,            # Pause between scrolls (seconds)
    'SCROLL_DISTANCE': 400,         # Pixels to scroll
    'SCROLL_NO_CHANGE_THRESHOLD': 3, # Stops scrolling after N no-change scrolls
    'DETAIL_TIMEOUT': 15000,        # Detail page timeout (ms)
}
```

---

## 📊 What Gets Saved

Each run creates a CSV file: `restaurants_[STATE]_[TIMESTAMP].csv`

**Columns:**
- `Name` - Restaurant name
- `Address` - Street address
- `Rating` - Rating (e.g., 4.5)
- `Reviews` - Number of reviews
- `URL` - Link to restaurant page

**Example Output:**
```
Name,Address,Rating,Reviews,URL
Uchi,801 S Lamar Blvd,4.8,2500,https://www.ubereats.com/restaurants/uchi-austin
Torchy's Tacos,Multiple Locations,4.6,3200,https://www.ubereats.com/restaurants/torchys-tacos
```

---

## 🔍 Filtering Logic

The scraper applies these filters in order:

1. **Rating Filter**: ✅ Only restaurants with rating ≥ 4.0
2. **Review Count Filter**: ✅ Only restaurants with ≥ 100 reviews
3. **Chain Filter**: ✅ Excludes major chain restaurants

Example chains excluded:
- McDonald's, Burger King, Wendy's, Taco Bell, KFC
- Chipotle, Panera, Olive Garden, Red Lobster
- And many more (see `CHAIN_KEYWORDS` in code)

---

## 🛠️ How It Works

### Step 1: Browser Initialization
- Launches Chromium browser
- Applies anti-detection measures (mimics human behavior)
- Sets viewport and user agent

### Step 2: Location Selection
- Navigates to UberEats homepage
- Automatically enters city/state
- Waits for restaurants to load

### Step 3: Card Collection
- **Scrolls through entire page** collecting restaurant cards
- Uses JavaScript to extract:
  - Restaurant name
  - Rating
  - Review count
  - URL to detail page
- Continues until no new restaurants found

### Step 4: Filtering
- Applies rating filter (≥ 4.0 stars)
- Applies review count filter (≥ 100 reviews)
- Excludes chain restaurants

### Step 5: Detail Extraction
- Opens each filtered restaurant's detail page
- Extracts address from detail page
- Handles extraction failures gracefully

### Step 6: CSV Export
- Saves each restaurant to CSV
- Prevents duplicates
- Provides progress updates

---

## ✨ Features

### ✅ Robust Card Collection
- Multiple extraction strategies
- Handles dynamic loading
- Continues scrolling until all restaurants found

### ✅ Intelligent Filtering
- Rating-based filtering (customizable min rating)
- Review count filtering (customizable min reviews)
- Automatic chain detection and exclusion

### ✅ Reliable Address Extraction
- Multiple selector strategies
- Fallback extraction methods
- Handles missing addresses gracefully

### ✅ Error Handling
- Retry logic for failed extractions
- Continues on page load errors
- Graceful timeout handling

### ✅ Anti-Detection
- User-agent spoofing
- Removal of webdriver indicators
- Chrome object mimicking
- Human-like scrolling with delays

### ✅ Progress Tracking
- Real-time progress display
- Percentage completion
- Statistics tracking
- Detailed summary report

---

## 📈 Expected Output

For Texas (TX), you should get:
- Multiple cities: Austin, Houston, Dallas
- Hundreds of restaurant cards collected
- After filtering: ~50-200 independent restaurants per city
- CSV saved to: `ubereats_data/restaurants_TX_[timestamp].csv`

Example statistics:
```
======================================================================
  📊 SCRAPING STATISTICS
======================================================================
  ⏱️  Total duration: 245.3 seconds
  📍 Cards collected: 1250
  ✅ Cards passed filters: 187
  💾 Restaurants saved: 185
  ❌ Failed extractions: 2
  ⚡ Avg time/restaurant: 1.3s
======================================================================
```

---

## 🐛 Troubleshooting

### Problem: No restaurants found

**Solution:**
1. The UberEats page may need manual location selection
2. Let the browser window open and select location manually
3. The scraper will detect restaurants once loaded

### Problem: Slow scraping

**Solution:**
1. Reduce `SCROLL_PAUSE` in CONFIG (currently 1.0 seconds)
2. Reduce `SCROLL_DISTANCE` for faster scrolling (currently 400 pixels)
3. Increase `BROWSER_TIMEOUT` if getting timeout errors

### Problem: Address extraction failing

**Solution:**
1. Some restaurants may not have address on detail page
2. Restaurants are still saved with empty address
3. This is expected and acceptable for model training

### Problem: Browser window not showing

**Solution:**
1. Check `BROWSER_HEADLESS` is set to `False` in CONFIG
2. Browser window may be behind other windows
3. Alt+Tab to find it

### Problem: Authentication or location verification

**Solution:**
1. UberEats may ask you to verify location
2. When browser opens, verify location manually
3. Scraper will continue once restaurants load

---

## 🎯 Tips for Best Results

1. **Run during off-hours** - Less chance of anti-bot blocks
2. **Use different states** - Reduces server load concentration
3. **Check output files** - Verify data quality before using
4. **Increase filters** - For stricter quality control:
   - Change `MIN_RATING` to 4.5
   - Change `MIN_REVIEWS` to 200

5. **Add more cities** - Edit `STATE_CITIES` dictionary to add cities:
   ```python
   'TX': ['Austin, TX', 'Houston, TX', 'Dallas, TX', 'San Antonio, TX'],
   ```

---

## 🔐 Legal & Ethical

- This scraper is for educational purposes
- Respects UberEats' robots.txt and terms
- Includes delays to avoid server overload
- Does not bypass authentication
- Collects only publicly visible information

**Use responsibly:**
- Don't run 24/7
- Respect server load
- Check terms of service
- Consider using UberEats API if doing commercial work

---

## 📞 Support

If you encounter issues:

1. **Check the console output** - Look for error messages
2. **Review the logs** - Check `ubereats_data/` for any error files
3. **Verify browser** - Make sure Chromium is installed:
   ```bash
   playwright install chromium
   ```

4. **Test minimal version** - If completely stuck:
   ```bash
   python test_playwright.py
   ```

---

## 🎓 Using Data for Model Training

Once you have the CSV data:

```python
import pandas as pd

# Load data
df = pd.read_csv('ubereats_data/restaurants_TX_20260421.csv')

# Basic stats
print(f"Total restaurants: {len(df)}")
print(f"Average rating: {df['Rating'].mean():.2f}")

# Prepare for model
X = df[['Rating', 'Reviews']].values
y = df['Name'].values  # or other target

# Use with your model...
```

---

**Happy scraping! 🍽️** 

For the latest version and updates, check the uberdata directory.
