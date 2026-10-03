"""
Comprehensive Chain Restaurant List for Filtering
Updated with complete chain list
"""

import re

CHAIN_RESTAURANTS = {
    # FAST FOOD & BURGERS
    'mcdonald', 'mcdonald\'s', 'burger king', 'wendy', 'wendy\'s', 'sonic', 
    'sonic drive-in', 'jack in the box', 'whataburger', 'in-n-out', 
    'in and out', 'white castle', 'five guys', 'shake shack', 'culver\'s',
    'checkers', 'rally\'s', 'carl\'s jr', 'hardee\'s', 'steak \'n shake',
    'freddy\'s', 'freddys', 'a&w', 'fatburger', 'wayback burgers', 
    'wayback', 'smashburger', 'habit burger', 'the habit',

    # CHICKEN
    'chick-fil-a', 'chick fil a', 'kfc', 'kentucky fried chicken', 
    'popeyes', 'popeyes louisiana kitchen', 'wingstop', 'raising cane\'s',
    'zaxby\'s', 'zaxbys', 'bojangles', 'church\'s chicken', 'churchs chicken',
    'el pollo loco', 'dave\'s hot chicken', 'jollibee', 'slim chickens',
    'buffalo wild wings', 'bww', 'bdubs', 'wingstreet', 'boston market',
    'krispy krunchy chicken',

    # PIZZA
    'domino', 'domino\'s', 'pizza hut', 'papa john\'s', 'papa johns',
    'little caesars', 'marco\'s pizza', 'marcos pizza', 'papa murphy\'s',
    'papa murphy', 'hungry howie\'s', 'round table pizza', 'pizza ranch',
    'blaze pizza', 'mod pizza', 'jet\'s pizza', 'jets pizza', 'cici\'s',
    'cici pizza', 'donatos', 'mellow mushroom', 'pizza rev', '&pizza',

    # SANDWICHES & SUBS
    'subway', 'jimmy john\'s', 'jimmy johns', 'jersey mike\'s', 'jersey mikes',
    'firehouse subs', 'quiznos', 'potbelly', 'potbelly sandwich', 'which wich',
    'schlotzsky\'s', 'schlotzskys', 'jason\'s deli', 'mcalister\'s deli',
    'capriotti\'s', 'penn station', 'charleys cheesesteaks', 'blimpie',
    'togo\'s', 'togos', 'erbert & gerbert\'s',

    # MEXICAN & LATIN
    'taco bell', 'chipotle', 'chipotle mexican grill', 'qdoba', 
    'moe\'s southwest grill', 'moes southwest grill', 'baja fresh',
    'del taco', 'rubio\'s', 'rubios', 'torchy\'s tacos', 'torchys',
    'chuys', 'on the border', 'taco cabana', 'el pollo loco', 'cafe rio',
    'taco john\'s', 'taco johns', 'fuzzy\'s taco shop', 'fuzzy tacos',

    # COFFEE, BAKERY & DESSERTS
    'starbucks', 'dunkin', 'dunkin donuts', 'caribou coffee', 'peet\'s coffee',
    'peets coffee', 'tim hortons', 'panera bread', 'einstein bros',
    'einstein brothers', 'bruegger\'s', 'brueggers', 'cinnabon',
    'krispy kreme', 'baskin robbins', 'cold stone', 'ben & jerry\'s',
    'ben and jerry\'s', 'haagen dazs', 'crumbl cookies', 'insomnia cookies',
    'auntie anne\'s', 'jamba', 'jamba juice', 'tropical smoothie cafe',
    'smoothie king', 'dutch bros coffee', 'dutch bros', '7-eleven', 'seven eleven',

    # CASUAL DINING
    'olive garden', 'applebees', 'apple bee\'s', 'chili\'s', 'chilis',
    'outback', 'outback steakhouse', 'red lobster', 'texas roadhouse',
    'ihop', 'denny\'s', 'dennys', 'waffle house', 'cheesecake factory',
    'p.f. chang\'s', 'pf changs', 'bj\'s restaurant', 'bj restaurant',
    'red robin', 'tgi fridays', 'hooters', 'miller\'s ale house', 'maggiano\'s',
    'longhorn steakhouse', 'carrabba\'s', 'carrabbas', 'bonefish grill',
    'california pizza kitchen', 'cpk', 'cracker barrel', 'cracker barrel old country store',

    # ASIAN & GLOBAL
    'panda express', 'p.f. chang\'s', 'pf changs', 'pei wei', 'benihana',
    'genghis grill', 'pick up stix', 'teriyaki madness', 'din tai fung',
    'itsu', 'wagamama', 'sarku japan', 'manchu wok', 'noodles and company',

    # HEALTH & FAST CASUAL
    'sweetgreen', 'dig', 'dig inn', 'saladworks', 'panera bread', 'cava',
    'chopt', 'true food kitchen', 'nando\'s', 'nandos', 'tropical smoothie cafe',

    # RETAIL & GROCERY (Uber Eats Partners) - SKIP THESE
    'walmart', 'target', 'cvs', 'walgreens', 'rite aid', '7-eleven', 'seven eleven',
    'kroger', 'safeway', 'publix', 'whole foods', 'trader joe\'s', 'trader joes',
    'aldi', 'costco', 'sam\'s club', 'sams club', 'dollar general', 'wawa',
    'sheetz', 'circle k', 'gnc', 'petco', 'petsmart', 'costco', 'bj\'s wholesale',

    # ADDITIONAL COMMON CHAINS
    'dairy queen', 'dq', 'sonic', 'whataburger', 'in-n-out', 'white castle',
    'five guys', 'shake shack', 'culver\'s', 'checkers', 'rally\'s',
    'carl\'s jr', 'hardee\'s', 'steak \'n shake', 'freddy\'s', 'a&w',
    'fatburger', 'wayback burgers', 'smashburger', 'qdob', 'moe\'s',
    'moes', 'baja fresh', 'del taco', 'rubio\'s', 'rubios', 'torchy\'s',
    'chuys', 'taco cabana', 'cafe rio', 'chipotle', 'panera', 'einstein',
    'bruegger', 'cinnabon', 'krispy kreme', 'baskin', 'cold stone',
    'ben & jerry', 'haagen dazs', 'crumbl', 'insomnia', 'auntie anne\'s',
    'jamba', 'tropical smoothie', 'smoothie king', 'dutch bros',
    'olive garden', 'applebees', 'chili\'s', 'outback', 'red lobster',
    'texas roadhouse', 'ihop', 'denny\'s', 'waffle house', 'cheesecake',
    'p.f. chang', 'bj\'s', 'red robin', 'tgi fridays', 'hooters',
    'miller\'s ale', 'maggiano\'s', 'longhorn', 'carrabba\'s', 'bonefish',
    'california pizza kitchen', 'panda express', 'pei wei', 'benihana',
    'genghis grill', 'pick up stix', 'teriyaki madness', 'din tai fung',
    'itsu', 'wagamama', 'sweetgreen', 'dig', 'saladworks', 'cava',
    'chopt', 'true food', 'nando\'s', 'kfc', 'popeyes', 'wingstop',
    'raising cane\'s', 'zaxby\'s', 'bojangles', 'church\'s', 'el pollo loco',
    'dave\'s hot chicken', 'jollibee', 'slim chickens', 'buffalo wild wings',
    'boston market', 'domino\'s', 'dominos', 'pizza hut', 'papa johns',
    'little caesars', 'marco\'s', 'papa murphy\'s', 'hungry howie\'s',
    'round table', 'pizza ranch', 'blaze pizza', 'mod pizza', 'jet\'s pizza',
    'cici\'s', 'donatos', 'mellow mushroom', 'subway', 'jimmy johns',
    'jersey mikes', 'firehouse subs', 'quiznos', 'potbelly', 'which wich',
    'schlotzsky\'s', 'jason\'s deli', 'mcalister\'s', 'capriotti\'s',
    'penn station', 'charleys', 'blimpie', 'taco bell', 'chipotle',
    'qdoba', 'moe\'s', 'baja fresh', 'del taco', 'rubio\'s', 'torchy\'s',
    'chuys', 'on the border', 'taco cabana', 'cafe rio'
}

def is_chain(restaurant_name: str) -> bool:
    """
    Check if restaurant is a known chain.
    
    Args:
        restaurant_name: Name of restaurant to check
        
    Returns:
        True if restaurant is a chain, False otherwise
    """
    if not restaurant_name:
        return False
    
    name_lower = restaurant_name.lower().strip()
    
    # Remove common suffixes like (South Lamar), (Downtown), etc.
    name_clean = re.sub(r'\s*\([^)]*\)', '', name_lower).strip()
    
    # Check for exact or partial matches
    for chain in CHAIN_RESTAURANTS:
        # Check both original name and cleaned name
        if chain in name_lower or chain in name_clean:
            return True
    
    # Additional check for common chain patterns
    # e.g., "McDonald's" vs "McDonald's (South Lamar)"
    first_word = name_lower.split()[0] if name_lower.split() else ""
    if first_word in CHAIN_RESTAURANTS:
        return True
    
    return False


def get_chain_name(restaurant_name: str) -> str:
    """
    Get the matching chain name if restaurant is a chain
    
    Args:
        restaurant_name: Name of restaurant to check
        
    Returns:
        Chain name if found, empty string otherwise
    """
    if not restaurant_name:
        return ""
    
    name_lower = restaurant_name.lower().strip()
    name_clean = re.sub(r'\s*\([^)]*\)', '', name_lower).strip()
    
    for chain in CHAIN_RESTAURANTS:
        if chain in name_lower or chain in name_clean:
            return chain
    
    first_word = name_lower.split()[0] if name_lower.split() else ""
    if first_word in CHAIN_RESTAURANTS:
        return first_word
    
    return ""


if __name__ == "__main__":
    # Test the function
    test_names = [
        "McDonald's", "Burger King", "Wendy's", "Phil's Icehouse", 
        "7-Eleven", "Chipotle Mexican Grill", "Local Pizza Place"
    ]
    
    print("Testing chain detection:")
    for name in test_names:
        is_chain_result = is_chain(name)
        chain_name = get_chain_name(name)
        print(f"  {name}: Chain={is_chain_result}, Matched='{chain_name}'")