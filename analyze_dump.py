import re

try:
    with open('debug_failure.html', 'r', encoding='utf-8') as f:
        html = f.read()

    print("--- Searching for context around 'Pablo' ---")
    matches = re.finditer(r'Pablo', html, re.IGNORECASE)
    
    count = 0
    for match in matches:
        print(f"Match {count+1}: Pablo")
        # Print surrounding context (prev 200 chars, next 800 chars to find badge)
        start = max(0, match.start() - 200)
        end = min(len(html), match.end() + 800)
        snippet = html[start:end]
        # Replace non-ascii for safe printing
        safe_snippet = snippet.encode('ascii', 'replace').decode('ascii')
        print(f"Context:\n{safe_snippet}")
        print("-" * 20)
        count += 1
        if count >= 3: break # Only need first few occurances

except Exception as e:
    print(f"Error: {e}")
