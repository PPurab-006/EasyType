import traceback

def test():
    try:
        exec("print(undeclared_var)", {})
    except NameError as e:
        print(f"NameError: {e}")
        # how to get line number?
        tb = e.__traceback__
        # get the last frame
        while tb.tb_next:
            tb = tb.tb_next
        print(f"Line number: {tb.tb_lineno}")
        print(repr(e))
test()
