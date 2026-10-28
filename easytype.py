import sys
import re
import ast
import io

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
    line = re.sub(r'\blist\b\s+([a-zA-Z0-9_\.\s,]+?)(?=\s*($|[^a-zA-Z0-9_\.\s,]))', r'[\1]', line)

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
    except Exception as e:
        import traceback
        if isinstance(e, SyntaxError):
            lineno = e.lineno
            print(f"Oops! Line {lineno}: Something in this line didn't translate cleanly. Run with --debug to see what EasyType turned it into, and check the line above for typos in EasyType keywords.")
        else:
            tb = e.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
            lineno = tb.tb_lineno

            if isinstance(e, NameError):
                match = re.search(r"name '(.+)' is not defined", str(e))
                name = match.group(1) if match else "something"
                print(f"Oops! Line {lineno}: I don't know what '{name}' is. Did you forget to create it first with '{name} equals ...', or is it a typo?")
            elif isinstance(e, TypeError):
                print(f"Oops! Line {lineno}: You tried to combine a number and a word. I can only do math with numbers — check if one of your values should be 'ask number' instead of 'ask'.")
            elif isinstance(e, IndexError):
                # Try to extract the actual length from the current frame's locals if possible
                actual_length = "fewer"
                frame = tb.tb_frame
                # Find which list caused the IndexError. We could try to parse the code line or look at locals.
                # A simple way: look at the local variables in the frame and find the list that was accessed.
                # Since we don't know which list, we can just say "the list".
                # To get actual length, we need to know the list name.
                import token
                import tokenize
                import io
                code_line = ""
                try:
                    code_line = transpiled_code.split('\n')[lineno - 1]
                    # Attempt to find list names in the code line
                    import ast
                    for node in ast.walk(ast.parse(code_line.strip())):
                        if isinstance(node, ast.Name) and isinstance(frame.f_locals.get(node.id), list):
                            actual_length = len(frame.f_locals[node.id])
                            break
                        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                            if isinstance(frame.f_locals.get(node.value.id), list):
                                actual_length = len(frame.f_locals[node.value.id])
                                break
                except Exception:
                    pass

                print(f"Oops! Line {lineno}: You asked for a position that doesn't exist in the list. Remember, EasyType lists start counting at position 1, and this list only has {actual_length} item(s).")
            elif isinstance(e, ZeroDivisionError):
                print(f"Oops! Line {lineno}: You tried to divide by zero, which isn't allowed — even computers can't do that math!")
            else:
                print(f"Oops! EasyType encountered an Error while running your code:")
                print(f"Line {lineno}: {type(e).__name__}: {e}")
                if not debug:
                    print("Tip: Run with --debug to see the translated Python code.")

if __name__ == "__main__":
    main()
