"""
UberEats Scraper - Multi-Location Launcher
Scrape multiple locations and save to separate files
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uber_scraper import UberEatsScraper


def print_header():
    """Print application header"""
    print("\n" + "="*70)
    print("  🍽️  UBEREATS RESTAURANT SCRAPER")
    print("="*70)
    print("\n📋 FEATURES:")
    print("   - Each location saves to a separate CSV file")
    print("   - Resume capability - won't re-scrape existing URLs")
    print("   - Filter: Rating >= 4.0, Reviews >= 100")
    print("   - Automatically skips chain restaurants")
    print("   - Extracts FULL restaurant name and complete address")
    print("="*70)


async def scrape_location(location: str):
    """Scrape a single location"""
    print(f"\n{'='*70}")
    print(f"📍 SCRAPING LOCATION: {location.upper()}")
    print(f"{'='*70}")
    
    scraper = UberEatsScraper(location=location)
    await scraper.run()


async def main():
    """Main entry point"""
    print_header()
    
    print("\nOptions:")
    print("1. Scrape a single location")
    print("2. Scrape multiple locations (batch mode)")
    print("3. Exit")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    if choice == '1':
        location = input("\nEnter location name (e.g., California, Florida, Austin): ").strip()
        await scrape_location(location)
    
    elif choice == '2':
        print("\nEnter locations one per line. Press Enter twice when done:")
        print("Example: Austin, Texas, California, Florida, New York")
        print("-" * 50)
        locations = []
        while True:
            loc = input().strip()
            if not loc:
                break
            locations.append(loc)
        
        if not locations:
            print("No locations entered. Exiting.")
            return
        
        print(f"\n📋 Locations to scrape: {', '.join(locations)}")
        confirm = input("\nProceed? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            for i, location in enumerate(locations, 1):
                print(f"\n{'='*70}")
                print(f"Progress: {i}/{len(locations)}")
                await scrape_location(location)
                print(f"\n✅ Completed {location}")
                print("="*70)
        else:
            print("Cancelled.")
    
    else:
        print("Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()