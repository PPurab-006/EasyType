import sys
import re

def transpile_line(line):
    # Skip empty lines
    if not line.strip():
        return line

    # Extract comments
    comments = []
    def repl_comment(m):
        comments.append(m.group(1))
        return ""

    line = re.sub(r'\*(.*?)\*', repl_comment, line)

    # Extract strings
    strings = []
    def repl_string(m):
        strings.append(m.group(0))
        return f"__STRING_{len(strings)-1}__"

    line = re.sub(r'"[^"]*"', repl_string, line)

    # Process EasyType syntax

    # 1. Type (print)
    line = re.sub(r'^(\s*)type\b\s*(.*)$', r'\1print(\2)', line)

    # 2. Control Flow & Loops
    line = re.sub(r'^(\s*)if\b\s+(.*)$', r'\1if \2:', line)
    line = re.sub(r'^(\s*)what-if\b\s+(.*)$', r'\1elif \2:', line)
    line = re.sub(r'^(\s*)else\b\s*$', r'\1else:', line)
    line = re.sub(r'^(\s*)repeat\b\s+(.*?)\s+times\b\s*$', r'\1for _ in range(\2):', line)
    line = re.sub(r'^(\s*)repeat\b\s+while\b\s+(.*)$', r'\1while \2:', line)

    # 3. Equals
    if re.match(r'^\s*(if|elif|while)\b', line):
        line = re.sub(r'\bequals\b', '==', line)
    else:
        line = re.sub(r'\bequals\b', '=', line)

    # 4. Lists
    line = re.sub(r'\blist\b\s+(.*)', r'[\1]', line)

    def repl_insert(m):
        indent = m.group(1)
        val = m.group(2)
        pos = m.group(3)
        var = m.group(4)
        if pos.isdigit():
            pos_str = str(int(pos) - 1)
        else:
            pos_str = f"{pos} - 1"
        return f"{indent}{var}.insert({pos_str}, {val})"
    line = re.sub(r'^(\s*)insert\b\s+(.*?)\s+at\s+position\b\s+(.*?)\s+in\b\s+([a-zA-Z0-9_]+)', repl_insert, line)

    def repl_remove(m):
        indent = m.group(1)
        pos = m.group(2)
        var = m.group(3)
        if pos.isdigit():
            pos_str = str(int(pos) - 1)
        else:
            pos_str = f"{pos} - 1"
        return f"{indent}{var}.pop({pos_str})"
    line = re.sub(r'^(\s*)remove\b\s+position\b\s+(.*?)\s+from\b\s+([a-zA-Z0-9_]+)', repl_remove, line)

    def repl_position(m):
        pos = m.group(1)
        var = m.group(2)
        if pos.isdigit():
            pos_str = str(int(pos) - 1)
        else:
            pos_str = f"{pos} - 1"
        return f"{var}[{pos_str}]"
    line = re.sub(r'\bposition\b\s+(.*?)\s+in\b\s+([a-zA-Z0-9_]+)', repl_position, line)

    line = re.sub(r'\bsize\b\s+of\b\s+([a-zA-Z0-9_]+)', r'len(\1)', line)

    # 5. User Input
    line = re.sub(r'\bask\b\s+number\b\s+([a-zA-Z0-9_]+|__STRING_\d+__)', r'int(input(\1))', line)
    line = re.sub(r'\bask\b\s+decimal\b\s+([a-zA-Z0-9_]+|__STRING_\d+__)', r'float(input(\1))', line)
    line = re.sub(r'\bask\b\s+([a-zA-Z0-9_]+|__STRING_\d+__)', r'input(\1)', line)

    # 6. Math & Logic
    line = re.sub(r'\bplus\b', '+', line)
    line = re.sub(r'\bminus\b', '-', line)
    line = re.sub(r'\btimes\b', '*', line)
    line = re.sub(r'\bdivided-by\b', '/', line)
    line = re.sub(r'\bpower\b', '**', line)
    line = re.sub(r'\bremainder of\b', '%', line)
    line = re.sub(r'\bpercent of\b', '* 0.01 *', line)
    line = re.sub(r'\bmore-than\b', '>', line)
    line = re.sub(r'\bless-than\b', '<', line)

    # Restore strings
    for i in range(len(strings)):
        line = line.replace(f"__STRING_{i}__", strings[i])

    # Append comments
    if comments:
        comment_str = " ".join(comments)
        line = f"{line} #{comment_str}"

    return line

def transpile(code):
    return "\n".join(transpile_line(line) for line in code.split("\n"))

def main():
    if len(sys.argv) < 2:
        print("Usage: python easytype.py <file.esy> [--debug]")
        sys.exit(1)

    filename = sys.argv[1]
    debug = "--debug" in sys.argv

    try:
        with open(filename, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    transpiled_code = transpile(code)

    if debug:
        print("--- Transpiled Python Code ---")
        print(transpiled_code)
        print("------------------------------")

    try:
        # Execute the code in an isolated namespace
        exec(transpiled_code, {})
    except SyntaxError as e:
        print(f"Oops! EasyType encountered a Syntax Error:")
        print(f"Line {e.lineno}: {e.msg}")
        if not debug:
            print("Tip: Run with --debug to see the translated Python code.")
    except Exception as e:
        print(f"Oops! EasyType encountered an Error while running your code:")
        print(f"{type(e).__name__}: {e}")
        if not debug:
            print("Tip: Run with --debug to see the translated Python code.")

if __name__ == "__main__":
    main()
