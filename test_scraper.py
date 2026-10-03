"""
UberEats Scraper - Diagnostic Test
Verify all dependencies and setup are correct before running full scraper
"""

import asyncio
import sys
import os


async def test_imports():
    """Test if all required modules can be imported"""
    print("1️⃣  Testing imports...")
    try:
        from playwright.async_api import async_playwright
        print("   ✅ playwright - OK")
        return True
    except ImportError as e:
        print(f"   ❌ playwright - FAILED: {e}")
        print("      Run: pip install playwright")
        return False


async def test_playwright_install():
    """Test if Chromium browser is installed"""
    print("\n2️⃣  Testing Playwright browser installation...")
    try:
        from playwright.async_api import async_playwright
        pw = await async_playwright().start()
        browser = await pw.chromium.launch()
        await browser.close()
        await pw.stop()
        print("   ✅ Chromium browser - OK")
        return True
    except Exception as e:
        print(f"   ❌ Chromium browser - FAILED: {e}")
        print("      Run: playwright install chromium")
        return False


async def test_ubereats_navigation():
    """Test navigating to UberEats"""
    print("\n3️⃣  Testing UberEats navigation...")
    try:
        from playwright.async_api import async_playwright
        
        print("   🔄 Starting browser...")
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("   🔄 Navigating to https://www.ubereats.com...")
        await page.goto("https://www.ubereats.com", wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(2)
        
        title = await page.title()
        print(f"   ✅ Page loaded: {title[:50]}...")
        
        # Close
        await context.close()
        await browser.close()
        await pw.stop()
        
        return True
    
    except Exception as e:
        print(f"   ❌ Navigation - FAILED: {e}")
        return False


async def test_restaurant_detection():
    """Test if scraper can detect restaurants on page"""
    print("\n4️⃣  Testing restaurant detection...")
    print("   ℹ️  This requires you to manually set a location")
    print("   📋 Steps:")
    print("      1. When browser opens, select a city (e.g., Austin, TX)")
    print("      2. Wait for restaurants to load")
    print("      3. Press ENTER here when restaurants are visible\n")
    
    try:
        from playwright.async_api import async_playwright
        
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://www.ubereats.com", wait_until='domcontentloaded', timeout=30000)
        
        input("Press ENTER when restaurants are visible on page: ")
        
        # Try to count restaurants
        count = await page.evaluate("""
            () => document.querySelectorAll('a[href*="/restaurants/"]').length
        """)
        
        print(f"\n   ✅ Found {count} restaurant elements\n")
        
        # Close
        await context.close()
        await browser.close()
        await pw.stop()
        
        return count > 0
    
    except Exception as e:
        print(f"   ❌ Restaurant detection - FAILED: {e}")
        return False


async def test_card_extraction():
    """Test card extraction logic"""
    print("\n5️⃣  Testing card extraction...")
    
    try:
        from playwright.async_api import async_playwright
        
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("   📍 Navigating to UberEats...")
        await page.goto("https://www.ubereats.com", wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(2)
        
        print("   👁️  Please set location and wait for restaurants to load...")
        input("   Press ENTER when ready: ")
        
        # Scroll a bit
        print("   📜 Scrolling...")
        await page.evaluate('window.scrollBy(0, 500)')
        await asyncio.sleep(2)
        
        # Try extraction
        print("   🔍 Extracting cards...")
        cards = await page.evaluate("""
            () => {
                const cards = [];
                const seen = new Set();
                
                document.querySelectorAll('a[href*="/restaurants/"]').forEach(link => {
                    try {
                        let container = link.closest('div[class*="RestaurantCard"], article') || link;
                        let text = container.innerText || '';
                        
                        let ratingMatch = text.match(/([0-9]\\.[0-9]{1,2})/);
                        let reviewMatch = text.match(/\\((\\d+)\\+?\\)/);
                        
                        if (ratingMatch && reviewMatch) {
                            let lines = text.split('\\n').filter(l => l.trim());
                            let name = lines[0]?.trim();
                            
                            if (name && !seen.has(name)) {
                                cards.push({
                                    name,
                                    rating: parseFloat(ratingMatch[1]),
                                    reviews: parseInt(reviewMatch[1])
                                });
                                seen.add(name);
                            }
                        }
                    } catch(e) {}
                });
                
                return cards;
            }
        """)
        
        print(f"   ✅ Extracted {len(cards)} cards")
        
        if cards:
            print("\n   📋 Sample cards:")
            for card in cards[:3]:
                print(f"      - {card['name']} ({card['rating']}⭐, {card['reviews']}+ reviews)")
        
        # Close
        await context.close()
        await browser.close()
        await pw.stop()
        
        return len(cards) > 0
    
    except Exception as e:
        print(f"   ❌ Card extraction - FAILED: {e}")
        return False


async def test_csv_output():
    """Test CSV writing"""
    print("\n6️⃣  Testing CSV output...")
    try:
        import csv
        import os
        
        test_file = 'ubereats_data/test_output.csv'
        os.makedirs('ubereats_data', exist_ok=True)
        
        # Write test data
        with open(test_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Address', 'Rating', 'Reviews', 'URL'])
            writer.writerow(['Test Restaurant', '123 Main St', 4.5, 100, 'https://example.com'])
        
        # Read back
        with open(test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"   ✅ CSV output - OK ({len(lines)} lines)")
        
        # Cleanup
        os.remove(test_file)
        
        return True
    
    except Exception as e:
        print(f"   ❌ CSV output - FAILED: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  🔧 UBEREATS SCRAPER - DIAGNOSTIC TEST")
    print("="*70 + "\n")
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", await test_imports()))
    
    # Test 2: Playwright
    results.append(("Playwright", await test_playwright_install()))
    
    # Test 3: Navigation
    results.append(("Navigation", await test_ubereats_navigation()))
    
    # Test 4: Detection
    try:
        results.append(("Detection", await test_restaurant_detection()))
    except KeyboardInterrupt:
        results.append(("Detection", None))
    
    # Test 5: Extraction
    try:
        results.append(("Extraction", await test_card_extraction()))
    except KeyboardInterrupt:
        results.append(("Extraction", None))
    
    # Test 6: CSV
    results.append(("CSV Output", await test_csv_output()))
    
    # Summary
    print("\n" + "="*70)
    print("  📊 TEST SUMMARY")
    print("="*70 + "\n")
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)
    
    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIP"
        print(f"  {status:12} - {test_name}")
    
    print()
    print(f"  Passed:  {passed}")
    print(f"  Failed:  {failed}")
    print(f"  Skipped: {skipped}")
    
    print("\n" + "="*70 + "\n")
    
    if failed == 0:
        print("✅ All tests passed! You're ready to use the scraper.\n")
        print("   Run: python scraper_launcher.py\n")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.\n")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
