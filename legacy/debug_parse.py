from urllib.parse import urlparse, parse_qs
import re

url = 'https://www.wowhead.com/pt/item=12345&bonus=6789'
print('URL:', url)

# Testar parse_qs
parsed = urlparse(url)
print('Parsed query:', parsed.query)
query = parse_qs(parsed.query)
print('Parsed dict:', query)
print('Bonus value:', query.get('bonus'))

# Testar regex
match = re.search(r'item=(\d+)', url)
print('Item ID match:', match.group(1) if match else 'None')

# Testar bonus extraction
if 'bonus' in query:
    values = query['bonus']
    print('Bonus values:', values)
    for value in values:
        print('Value:', value, 'Type:', type(value))
        # Split
        ids = re.split(r'[:,]', value)
        print('Split IDs:', ids)
