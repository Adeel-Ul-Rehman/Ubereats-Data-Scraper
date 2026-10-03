"""
Debug script to inspect the page structure and find rating/review elements
"""

import asyncio
from playwright.async_api import async_playwright


async def debug_page():
    """Debug function to inspect page structure"""
    
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        # Navigate to UberEats
        await page.goto('https://www.ubereats.com', wait_until='domcontentloaded', timeout=30000)
        
        print("\n" + "="*70)
        print("🔍 DEBUG MODE - Page Inspector")
        print("="*70)
        print("\n📋 Instructions:")
        print("1. Set your delivery location in the browser")
        print("2. Scroll to load restaurants")
        print("3. Press ENTER when ready to analyze the page")
        print("="*70)
        
        input("\n👉 Press ENTER when restaurants are loaded...")
        
        # Run debug JavaScript
        debug_js = """
        () => {
            const results = {
                totalCards: 0,
                cardsWithRating: 0,
                sampleCards: [],
                ratingElements: []
            };
            
            // Find all potential restaurant cards
            const cards = document.querySelectorAll('a[data-testid="store-card"], a[href*="/store/"]');
            results.totalCards = cards.length;
            
            for (let i = 0; i < Math.min(cards.length, 5); i++) {
                const card = cards[i];
                const cardInfo = {
                    hasRatingElement: false,
                    ratingValue: null,
                    reviewsValue: null,
                    name: null,
                    ariaLabel: null,
                    innerText: null
                };
                
                // Get name
                const nameEl = card.querySelector('h3, h2');
                if (nameEl) cardInfo.name = nameEl.innerText.trim();
                if (!cardInfo.name) {
                    const text = card.innerText;
                    const lines = text.split('\\n');
                    if (lines[0]) cardInfo.name = lines[0].trim();
                }
                
                // Look for rating element
                const ratingEl = card.querySelector('[aria-label*="Rating"]');
                if (ratingEl) {
                    cardInfo.hasRatingElement = true;
                    cardInfo.ariaLabel = ratingEl.getAttribute('aria-label');
                    
                    // Parse rating
                    const ratingMatch = cardInfo.ariaLabel.match(/Rating:\\s*([0-9.]+)/);
                    if (ratingMatch) cardInfo.ratingValue = ratingMatch[1];
                    
                    // Parse reviews
                    const reviewsMatch = cardInfo.ariaLabel.match(/([0-9,]+(?:\\+)?)\\s*reviews?/);
                    if (reviewsMatch) cardInfo.reviewsValue = reviewsMatch[1];
                }
                
                // Get inner text for debugging
                cardInfo.innerText = card.innerText.substring(0, 200);
                
                results.sampleCards.push(cardInfo);
            }
            
            // Find all rating elements on the page
            const allRatingElements = document.querySelectorAll('[aria-label*="Rating"]');
            for (const el of allRatingElements) {
                results.ratingElements.push(el.getAttribute('aria-label'));
            }
            
            return results;
        }
        """
        
        results = await page.evaluate(debug_js)
        
        print("\n" + "="*70)
        print("📊 PAGE ANALYSIS RESULTS")
        print("="*70)
        
        print(f"\n📈 Statistics:")
        print(f"   Total restaurant cards found: {results['totalCards']}")
        print(f"   Cards with rating element: {results['cardsWithRating']}")
        print(f"   Total rating elements on page: {len(results['ratingElements'])}")
        
        print("\n📋 Sample Cards (first 5):")
        for i, card in enumerate(results['sampleCards'], 1):
            print(f"\n   Card {i}:")
            print(f"     Name: {card['name']}")
            print(f"     Has rating element: {card['hasRatingElement']}")
            if card['ariaLabel']:
                print(f"     Aria-label: {card['ariaLabel']}")
                print(f"     Rating value: {card['ratingValue']}")
                print(f"     Reviews value: {card['reviewsValue']}")
            print(f"     Inner text preview: {card['innerText'][:100]}...")
        
        if results['ratingElements']:
            print("\n⭐ All rating elements found:")
            for label in results['ratingElements'][:10]:
                print(f"   - {label}")
        
        print("\n" + "="*70)
        print("🔧 Next Steps:")
        print("1. Check if restaurant cards have the rating element")
        print("2. Note the exact format of the aria-label")
        print("3. If no rating elements found, the page might be using a different structure")
        print("="*70)
        
        input("\n👉 Press ENTER to close browser...")
        await browser.close()


async def test_address_extraction():
    """Test address extraction on a specific restaurant page"""
    
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n" + "="*70)
        print("📍 ADDRESS EXTRACTION TEST")
        print("="*70)
        print("\n1. Navigate to any restaurant page")
        print("2. Copy the URL")
        print("3. Paste it here")
        
        url = input("\nEnter restaurant URL: ").strip()
        
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(2)
        
        # Try multiple methods to extract address
        print("\n🔍 Trying different address extraction methods...")
        
        # Method 1: JavaScript extraction
        js_method1 = """
        () => {
            const bodyText = document.body.innerText;
            const patterns = [
                /(\\d+[\\s\\-]?\\w+(?:\\s+\\w+)*\\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Place|Pl|Square|Sq|Loop|Circle|Cir|Parkway|Pkwy)[\\s,]+[A-Za-z\\s]+,\\s*[A-Z]{2}\\s+\\d{5})/i,
                /(\\d+[\\s\\-]?\\w+(?:\\s+\\w+)*\\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Place|Pl|Square|Sq|Loop|Circle|Cir|Parkway|Pkwy)[\\s,]+[A-Z]{2}\\s+\\d{5})/i
            ];
            for (const pattern of patterns) {
                const match = bodyText.match(pattern);
                if (match) return match[1].trim();
            }
            return null;
        }
        """
        
        address1 = await page.evaluate(js_method1)
        print(f"Method 1 (pattern matching): {address1 if address1 else 'Not found'}")
        
        # Method 2: Look for specific elements
        js_method2 = """
        () => {
            const selectors = [
                '[data-testid="store-address"]',
                '[class*="address"]',
                'address',
                '[class*="location"]'
            ];
            for (const selector of selectors) {
                const elem = document.querySelector(selector);
                if (elem) {
                    const text = elem.innerText.trim();
                    if (text && text.length > 10) return text;
                }
            }
            return null;
        }
        """
        
        address2 = await page.evaluate(js_method2)
        print(f"Method 2 (element selectors): {address2 if address2 else 'Not found'}")
        
        # Method 3: Look for lines with city/state/zip
        js_method3 = """
        () => {
            const lines = document.body.innerText.split('\\n');
            for (const line of lines) {
                if (line.match(/[A-Z]{2}\\s+\\d{5}/) && line.match(/\\d/)) {
                    return line.trim();
                }
            }
            return null;
        }
        """
        
        address3 = await page.evaluate(js_method3)
        print(f"Method 3 (city/state/zip line): {address3 if address3 else 'Not found'}")
        
        print("\n" + "="*70)
        input("👉 Press ENTER to close browser...")
        await browser.close()


async def main():
    print("\n" + "="*70)
    print("  🔧 UBEREATS DEBUG TOOL")
    print("="*70)
    print("\nOptions:")
    print("1. Debug page structure - Find rating/review elements")
    print("2. Test address extraction - On a specific restaurant page")
    print("3. Exit")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    if choice == '1':
        await debug_page()
    elif choice == '2':
        await test_address_extraction()
    else:
        print("Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())