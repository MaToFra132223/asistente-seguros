from bs4 import BeautifulSoup
import re

def analyze():
    print("Analyzing debug_failure.html...")
    try:
        with open('debug_failure.html', 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        print("debug_failure.html not found.")
        return

    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Find Main Panel
    main = soup.find('div', id='main')
    if not main:
        print("ALERT: div[id='main'] NOT found.")
        # Try finding by role/aria
        main = soup.find('div', role='region', attrs={'aria-label': 'Conversation'})
        if not main:
             main = soup.find('div', role='region', attrs={'aria-label': 'Conversación'})
    
    if main:
        print(f"FOUND Main Panel: {main.name} (Classes: {main.get('class')})")
        
        # 2. Find Messages inside Main
        # Look for rows
        rows = main.find_all('div', role='row')
        print(f"Found {len(rows)} rows in Main Panel.")
        
        for i, row in enumerate(rows[-3:]): # Check last 3
            print(f"--- Row {i} ---")
            print(f"Classes: {row.get('class')}")
            print(f"Text: {row.get_text()[:100]}...")
            
            # Check for message-in/out classes
            if 'message-in' in str(row):
                print("  -> Contains 'message-in'")
            else:
                print("  -> DOES NOT contain 'message-in'")
                
            # Print parent classes to see identifying containers
            parent = row.parent
            if parent:
                print(f"  Parent Classes: {parent.get('class')}")
                
    else:
        print("CRITICAL: No Main Panel found in dump.")
        # Print all regions
        regions = soup.find_all('div', role='region')
        print(f"Found {len(regions)} regions:")
        for r in regions:
            print(f"  - Label: {r.get('aria-label')}, Classes: {r.get('class')}")

if __name__ == "__main__":
    analyze()
