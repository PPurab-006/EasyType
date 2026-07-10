import re

with open('easytype.py', 'r') as f:
    content = f.read()

content = content.replace(
    r"line = re.sub(r'\blist\b\s+(.*)', r'[\1]', line)",
    r"line = re.sub(r'\blist\b\s+([a-zA-Z0-9_\.\s,]+?)(?=\s*($|[^a-zA-Z0-9_\.\s,]))', r'[\1]', line)"
)

with open('easytype.py', 'w') as f:
    f.write(content)
