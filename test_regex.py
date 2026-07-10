import re

line = 'print(__STRING_0__, list 1, 2, 3)'
# Old regex
print("Old:", re.sub(r'\blist\b\s+(.*)', r'[\1]', line))

# New regex
print("New:", re.sub(r'\blist\b\s+([a-zA-Z0-9_,\s]+)', r'[\1]', line))
