"""
UberEats Restaurant Scraper - Manual Mode
Filters: Rating >= 4.0, Reviews >= 100
Skips chain restaurants
Saves: Restaurant Name and Address to CSV
"""

import asyncio
import csv
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set

from playwright.async_api import async_playwright, Page

# Import chain detection
from chains_list import is_chain


class UberEatsScraper:
    """Main scraper class for UberEats restaurant data"""
    
    def __init__(self, output_dir: str = "ubereats_data", location: str = None):
        self.output_dir = output_dir
        self.location = location
        self.scraped_urls: Set[str] = set()
        self.results: List[Dict] = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Set filename based on location
        if location:
            safe_location = re.sub(r'[^a-zA-Z0-9]', '_', location.lower())
            self.csv_file = os.path.join(output_dir, f"restaurants_{safe_location}.csv")
        else:
            self.csv_file = os.path.join(output_dir, "restaurants.csv")
        
        # Load already scraped data if exists
        self.load_existing_data()
    
    def load_existing_data(self):
        """Load previously scraped data to resume from where left off"""
        if os.path.exists(self.csv_file):
            try:
                with open(self.csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'url' in row and row['url']:
                            self.scraped_urls.add(row['url'])
                        self.results.append(row)
                print(f"📂 Loaded {len(self.results)} previously scraped restaurants from {os.path.basename(self.csv_file)}")
            except Exception as e:
                print(f"⚠️ Could not load existing data: {e}")
        else:
            print(f"📁 New file will be created: {os.path.basename(self.csv_file)}")
    
    def save_to_csv(self):
        """Save scraped data to CSV file"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['restaurant_name', 'address', 'rating', 'reviews', 'url', 'scraped_at', 'location'])
            writer.writeheader()
            for row in self.results:
                writer.writerow(row)
        
        print(f"💾 Saved {len(self.results)} restaurants to {self.csv_file}")
    
    def parse_rating_from_aria(self, aria_label: str) -> Tuple[Optional[float], Optional[int]]:
        """Parse rating and reviews from aria-label like 'Rating: 4.7 stars. 34 reviews'"""
        rating = None
        reviews = None
        
        rating_match = re.search(r'Rating:\s*([0-9.]+)', aria_label)
        if rating_match:
            rating = float(rating_match.group(1))
        
        reviews_match = re.search(r'([0-9,]+(?:\+)?)\s*reviews?', aria_label)
        if reviews_match:
            rev_str = reviews_match.group(1).replace(',', '')
            if rev_str.endswith('+'):
                rev_str = rev_str[:-1]
            reviews = int(rev_str)
        
        return rating, reviews
    
    def meets_filters(self, rating: Optional[float], reviews: Optional[int]) -> bool:
        """Check if restaurant meets minimum requirements"""
        if rating is None or reviews is None:
            return False
        return rating >= 4.0 and reviews >= 100
    
    async def extract_restaurant_cards_with_js(self, page: Page) -> List[Dict]:
        """
        Extract all restaurant cards using JavaScript evaluation
        """
        js_code = """
        () => {
            const restaurants = [];
            const seen = new Set();
            
            const cards = document.querySelectorAll('a[data-testid="store-card"]');
            
            for (const card of cards) {
                try {
                    let url = card.getAttribute('href');
                    if (!url) continue;
                    if (url.startsWith('/')) {
                        url = 'https://www.ubereats.com' + url;
                    }
                    const baseUrl = url.split('?')[0];
                    
                    if (seen.has(baseUrl)) continue;
                    
                    // Get restaurant name - try to get full name
                    let name = '';
                    const nameElement = card.querySelector('h3');
                    if (nameElement) {
                        name = nameElement.innerText.trim();
                    }
                    if (!name) {
                        const text = card.innerText;
                        const lines = text.split('\\n');
                        if (lines[0] && lines[0].length > 0 && lines[0].length < 100) {
                            name = lines[0].trim();
                        }
                    }
                    
                    if (!name || name.length < 2) continue;
                    
                    // Find rating for filtering (only used for filtering, not for final data)
                    let rating = null;
                    let reviews = null;
                    
                    const parent = card.closest('div[class*="store"], div[class*="restaurant"], li');
                    if (parent) {
                        const ratingElement = parent.querySelector('[aria-label*="Rating:"]');
                        if (ratingElement) {
                            const ariaLabel = ratingElement.getAttribute('aria-label');
                            const ratingMatch = ariaLabel.match(/Rating:\\s*([0-9.]+)/);
                            const reviewsMatch = ariaLabel.match(/([0-9,]+(?:\\+)?)\\s*reviews?/);
                            if (ratingMatch) rating = parseFloat(ratingMatch[1]);
                            if (reviewsMatch) {
                                let revStr = reviewsMatch[1].replace(/,/g, '');
                                if (revStr.endsWith('+')) revStr = revStr.slice(0, -1);
                                reviews = parseInt(revStr);
                            }
                        }
                    }
                    
                    if (rating !== null && reviews !== null) {
                        seen.add(baseUrl);
                        restaurants.push({
                            name: name,
                            url: baseUrl,
                            homepage_rating: rating,
                            homepage_reviews: reviews
                        });
                    }
                } catch(e) {
                    console.error(e);
                }
            }
            
            return restaurants;
        }
        """
        
        try:
            restaurants = await page.evaluate(js_code)
            return restaurants
        except Exception as e:
            print(f"❌ JavaScript evaluation failed: {e}")
            return []
    
    async def scrape_restaurant_details(self, page: Page, restaurant: Dict) -> Optional[Dict]:
        """
        Open restaurant detail page and scrape FULL name, address, rating, and reviews
        """
        try:
            url = restaurant['url']
            
            print(f"  📖 Opening: {restaurant['name'][:50]}...")
            
            # Navigate to restaurant page
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(2)
            
            # Extract FULL restaurant name from detail page
            js_name = """
            () => {
                // Try multiple methods to get the full restaurant name
                
                // Method 1: Look for h1 tag (usually the full name)
                const h1 = document.querySelector('h1');
                if (h1 && h1.innerText.trim().length > 0) {
                    return h1.innerText.trim();
                }
                
                // Method 2: Look for title element
                const title = document.querySelector('title');
                if (title) {
                    let titleText = title.innerText;
                    // Remove common suffixes like " - Menu & Prices - City Delivery | Uber Eats"
                    titleText = titleText.replace(/\\s*[-|]\\s*Menu.*$/i, '');
                    titleText = titleText.replace(/\\s*[-|]\\s*Prices.*$/i, '');
                    titleText = titleText.replace(/\\s*[-|]\\s*Delivery.*$/i, '');
                    if (titleText.length > 0) return titleText.trim();
                }
                
                // Method 3: Look for store name in structured data
                const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of scripts) {
                    try {
                        const data = JSON.parse(script.innerText);
                        if (data.name) return data.name;
                        if (data.brand && data.brand.name) return data.brand.name;
                    } catch(e) {}
                }
                
                // Method 4: Look for elements with store name classes
                const nameSelectors = [
                    '[data-testid="store-name"]',
                    '[class*="store-name"]',
                    '[class*="restaurant-name"]',
                    '[class*="store-title"]'
                ];
                for (const selector of nameSelectors) {
                    const elem = document.querySelector(selector);
                    if (elem && elem.innerText.trim().length > 0) {
                        return elem.innerText.trim();
                    }
                }
                
                return null;
            }
            """
            
            full_name = await page.evaluate(js_name)
            
            # Extract rating and reviews from detail page
            js_rating_reviews = """
            () => {
                // Look for rating element on detail page
                const ratingElement = document.querySelector('[aria-label*="Rating:"]');
                if (ratingElement) {
                    const ariaLabel = ratingElement.getAttribute('aria-label');
                    const ratingMatch = ariaLabel.match(/Rating:\\s*([0-9.]+)/);
                    const reviewsMatch = ariaLabel.match(/([0-9,]+(?:\\+)?)\\s*reviews?/);
                    
                    let rating = null;
                    let reviews = null;
                    
                    if (ratingMatch) rating = parseFloat(ratingMatch[1]);
                    if (reviewsMatch) {
                        let revStr = reviewsMatch[1].replace(/,/g, '');
                        if (revStr.endsWith('+')) revStr = revStr.slice(0, -1);
                        reviews = parseInt(revStr);
                    }
                    
                    return { rating, reviews };
                }
                return { rating: null, reviews: null };
            }
            """
            
            rating_reviews = await page.evaluate(js_rating_reviews)
            
            # Extract FULL address from detail page
            js_address = """
            () => {
                // Try multiple methods to get complete address
                
                // Method 1: Look for address in structured data
                const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of scripts) {
                    try {
                        const data = JSON.parse(script.innerText);
                        if (data.address) {
                            if (typeof data.address === 'string') return data.address;
                            if (data.address.streetAddress) {
                                let addr = data.address.streetAddress;
                                if (data.address.addressLocality) addr += ', ' + data.address.addressLocality;
                                if (data.address.addressRegion) addr += ', ' + data.address.addressRegion;
                                if (data.address.postalCode) addr += ' ' + data.address.postalCode;
                                return addr;
                            }
                        }
                    } catch(e) {}
                }
                
                // Method 2: Look for specific address elements
                const selectors = [
                    '[data-testid="store-address"]',
                    '[class*="store-address"]',
                    '[class*="location-address"]',
                    'address',
                    '[class*="address"]',
                    '[class*="location"]'
                ];
                
                for (const selector of selectors) {
                    const elem = document.querySelector(selector);
                    if (elem) {
                        const text = elem.innerText.trim();
                        if (text && text.length > 10 && /\\d/.test(text)) {
                            return text;
                        }
                    }
                }
                
                // Method 3: Comprehensive pattern matching for US addresses
                const bodyText = document.body.innerText;
                
                // More comprehensive address patterns
                const patterns = [
                    // Full address with street, city, state, zip
                    /(\\d+[\\s\\-]?\\w+(?:\\s+\\w+)*\\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Place|Pl|Square|Sq|Loop|Circle|Cir|Parkway|Pkwy)[\\s,]+[A-Za-z\\s]+,\\s*[A-Z]{2}\\s+\\d{5}(?:-\\d{4})?)/i,
                    // Address with city and state
                    /(\\d+[\\s\\-]?\\w+(?:\\s+\\w+)*\\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Place|Pl|Square|Sq|Loop|Circle|Cir|Parkway|Pkwy)[\\s,]+[A-Za-z\\s]+,\\s*[A-Z]{2})/i,
                    // Simple street address with zip
                    /(\\d+[\\s\\-]?\\w+(?:\\s+\\w+)*\\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Place|Pl|Square|Sq|Loop|Circle|Cir|Parkway|Pkwy)[\\s,]+[A-Z]{2}\\s+\\d{5})/i
                ];
                
                for (const pattern of patterns) {
                    const match = bodyText.match(pattern);
                    if (match) {
                        return match[1].trim();
                    }
                }
                
                // Method 4: Look for lines containing city, state, zip
                const lines = bodyText.split('\\n');
                for (const line of lines) {
                    // Look for pattern like "City, ST 12345"
                    if (line.match(/[A-Za-z\\s]+,\\s*[A-Z]{2}\\s+\\d{5}/)) {
                        // Try to get the preceding line for street address
                        const lineIndex = lines.indexOf(line);
                        if (lineIndex > 0) {
                            const prevLine = lines[lineIndex - 1].trim();
                            if (prevLine.match(/\\d/)) {
                                return prevLine + ', ' + line.trim();
                            }
                        }
                        return line.trim();
                    }
                }
                
                return "Address not found";
            }
            """
            
            address = await page.evaluate(js_address)
            
            # Clean up address
            if address and len(address) > 300:
                address = address[:300]
            
            # Use full_name from detail page if found, otherwise use homepage name
            final_name = full_name if full_name else restaurant['name']
            
            result = {
                'restaurant_name': final_name,
                'address': address,
                'rating': rating_reviews.get('rating') if rating_reviews.get('rating') else restaurant.get('homepage_rating'),
                'reviews': rating_reviews.get('reviews') if rating_reviews.get('reviews') else restaurant.get('homepage_reviews'),
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'location': self.location if self.location else 'unknown'
            }
            
            print(f"  ✅ Scraped: {final_name[:50]}...")
            print(f"     Rating: ⭐{result['rating']} ({result['reviews']}+ reviews)")
            print(f"     Address: {address[:80]}...")
            return result
            
        except Exception as e:
            print(f"  ❌ Failed to scrape {restaurant.get('name', 'Unknown')}: {e}")
            return None
    
    async def run(self):
        """Main scraping workflow - Manual mode"""
        print("\n" + "="*70)
        print("  🍽️ UBEREATS SCRAPER - MANUAL MODE")
        print("="*70)
        
        # Ask for location name
        if not self.location:
            self.location = input("\n📍 Enter location name (e.g., California, Florida, Austin): ").strip()
            if self.location:
                safe_location = re.sub(r'[^a-zA-Z0-9]', '_', self.location.lower())
                self.csv_file = os.path.join(self.output_dir, f"restaurants_{safe_location}.csv")
                self.load_existing_data()
        
        print("\n📋 INSTRUCTIONS:")
        print("1. Browser window will open NOW")
        print(f"2. MANUALLY set your delivery location to: {self.location}")
        print("3. MANUALLY scroll down and click 'Show More' until ALL restaurants are loaded")
        print("4. Once all restaurants are visible, come back to terminal and press ENTER")
        print("5. The script will automatically filter and scrape qualifying restaurants")
        print("\n⚠️ Filter: Rating >= 4.0 AND Reviews >= 100")
        print("⚠️ Chain restaurants will be skipped")
        print(f"📁 Data will be saved to: {self.csv_file}")
        print("="*70)
        
        async with async_playwright() as pw:
            print("\n🌐 Opening browser...")
            browser = await pw.chromium.launch(headless=False, args=['--blink-settings=imagesEnabled=false'])
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            await page.goto('https://www.ubereats.com', wait_until='domcontentloaded', timeout=30000)
            
            print("\n✅ Browser ready! Please complete your setup in the browser window.")
            print(f"   - Set your delivery location to: {self.location}")
            print("   - Scroll and click 'Show More' until ALL restaurants are loaded")
            print("\n👉 Press ENTER in THIS terminal when ALL restaurants are loaded...")
            
            input()
            
            try:
                print("\n🔍 Scanning for restaurants...")
                restaurants = await self.extract_restaurant_cards_with_js(page)
                
                print(f"\n📊 Found {len(restaurants)} restaurants with valid rating/review data")
                
                if not restaurants:
                    print("\n⚠️ No restaurants with rating data found!")
                    return
                
                # Filter out chains and apply rating/review filter
                qualifying = []
                skipped_chains = []
                failed_filters = []
                
                for r in restaurants:
                    if is_chain(r['name']):
                        skipped_chains.append(r['name'])
                        continue
                    
                    if self.meets_filters(r['homepage_rating'], r['homepage_reviews']):
                        qualifying.append(r)
                        print(f"  ✅ PASS: {r['name']} (⭐{r['homepage_rating']}, {r['homepage_reviews']}+ reviews)")
                    else:
                        failed_filters.append(r)
                        print(f"  ❌ FAIL: {r['name']} (⭐{r['homepage_rating']}, {r['homepage_reviews']}+ reviews)")
                
                print(f"\n📊 Summary for {self.location}:")
                print(f"   Total restaurants with data: {len(restaurants)}")
                print(f"   Skipped chains: {len(skipped_chains)}")
                print(f"   Failed filters: {len(failed_filters)}")
                print(f"   ✅ QUALIFYING: {len(qualifying)}")
                
                if not qualifying:
                    print("\n⚠️ No qualifying restaurants found!")
                    choice = input("\nDo you want to scrape all non-chain restaurants anyway? (yes/no): ").strip().lower()
                    if choice != 'yes':
                        print("Exiting...")
                        return
                    qualifying = [r for r in restaurants if not is_chain(r['name'])]
                    print(f"   Will scrape {len(qualifying)} non-chain restaurants")
                
                if qualifying:
                    print("\n📝 Starting to scrape restaurant details...")
                    print("   (This may take a few minutes)\n")
                    
                    for i, restaurant in enumerate(qualifying, 1):
                        print(f"\n[{i}/{len(qualifying)}] Processing...")
                        
                        if restaurant['url'] in self.scraped_urls:
                            print(f"  ⏭️ Already scraped: {restaurant['name']}")
                            continue
                        
                        new_page = await context.new_page()
                        try:
                            result = await self.scrape_restaurant_details(new_page, restaurant)
                            if result:
                                self.results.append(result)
                                self.scraped_urls.add(restaurant['url'])
                                self.save_to_csv()
                        except Exception as e:
                            print(f"  ⚠️ Error: {e}")
                        finally:
                            await new_page.close()
                        
                        await asyncio.sleep(1.5)
                
                print("\n" + "="*70)
                print(f"✅ SCRAPING COMPLETE for {self.location}!")
                print(f"   Total restaurants scraped: {len(self.results)}")
                print(f"   Data saved to: {self.csv_file}")
                print("="*70)
                
            except Exception as e:
                print(f"\n❌ Error during scraping: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                print("\n🔒 Browser will stay open until you press ENTER...")
                input("👉 Press ENTER to close browser...")
                await browser.close()
    
    async def test_scrape_one(self):
        """Test scraping a single restaurant (for debugging)"""
        print("\n" + "="*70)
        print("  🔧 TEST MODE - Single Restaurant Scraper")
        print("="*70)
        
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=False, args=['--blink-settings=imagesEnabled=false'])
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.goto('https://www.ubereats.com', wait_until='domcontentloaded', timeout=30000)
            
            print("\n✅ Browser ready!")
            print("Please navigate to a restaurant page manually")
            print("Then come back and press ENTER to scrape it")
            
            input("\n👉 Press ENTER when you're on a restaurant page...")
            
            current_url = page.url
            print(f"\n📍 Current URL: {current_url}")
            
            # Test full name extraction
            full_name = await page.evaluate("""
                () => {
                    const h1 = document.querySelector('h1');
                    if (h1) return h1.innerText;
                    const title = document.querySelector('title');
                    if (title) return title.innerText;
                    return "Unknown";
                }
            """)
            print(f"📝 Full restaurant name: {full_name}")
            
            # Test rating extraction
            rating_data = await page.evaluate("""
                () => {
                    const ratingElement = document.querySelector('[aria-label*="Rating:"]');
                    if (ratingElement) {
                        return ratingElement.getAttribute('aria-label');
                    }
                    return null;
                }
            """)
            print(f"⭐ Rating data: {rating_data}")
            
            # Test address extraction
            js_address = """
            () => {
                const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of scripts) {
                    try {
                        const data = JSON.parse(script.innerText);
                        if (data.address) {
                            if (typeof data.address === 'string') return data.address;
                            if (data.address.streetAddress) {
                                let addr = data.address.streetAddress;
                                if (data.address.addressLocality) addr += ', ' + data.address.addressLocality;
                                if (data.address.addressRegion) addr += ', ' + data.address.addressRegion;
                                if (data.address.postalCode) addr += ' ' + data.address.postalCode;
                                return addr;
                            }
                        }
                    } catch(e) {}
                }
                
                const bodyText = document.body.innerText;
                const patterns = [
                    /(\\d+[\\s\\-]?\\w+(?:\\s+\\w+)*\\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Place|Pl|Square|Sq|Loop|Circle|Cir|Parkway|Pkwy)[\\s,]+[A-Za-z\\s]+,\\s*[A-Z]{2}\\s+\\d{5})/i,
                ];
                for (const pattern of patterns) {
                    const match = bodyText.match(pattern);
                    if (match) return match[1].trim();
                }
                return "Address not found";
            }
            """
            
            address = await page.evaluate(js_address)
            print(f"📍 Address: {address}")
            
            input("\n👉 Press ENTER to close browser...")
            await browser.close()


async def main():
    """Entry point"""
    print("\n" + "="*70)
    print("  🍽️ UBEREATS SCRAPER")
    print("="*70)
    print("\nOptions:")
    print("1. Full scrape (manual mode)")
    print("2. Test single restaurant")
    print("3. Exit")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    if choice == '1':
        scraper = UberEatsScraper()
        await scraper.run()
    elif choice == '2':
        scraper = UberEatsScraper()
        await scraper.test_scrape_one()
    else:
        print("Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())