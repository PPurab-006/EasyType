import re
import sys

with open('easytype.py', 'r') as f:
    content = f.read()

# We need to replace the try/except block at the end
start_marker = "    try:\n        # Execute the code in an isolated namespace"

new_block = """    try:
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
                    code_line = transpiled_code.split('\\n')[lineno - 1]
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
"""

parts = content.split(start_marker)
if len(parts) == 2:
    new_content = parts[0] + new_block
    # Remove the `if __name__ == "__main__":` part and add it back
    if 'if __name__ == "__main__":' in new_content:
        new_content = new_content.split('if __name__ == "__main__":')[0] + 'if __name__ == "__main__":\n    main()\n'
    else:
        new_content += '\nif __name__ == "__main__":\n    main()\n'
    with open('easytype.py', 'w') as f:
        f.write(new_content)
    print("Patched successfully")
else:
    print("Could not find start_marker")
