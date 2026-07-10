import traceback

namespace = {'scores': [10, 20]}
try:
    exec("scores.pop(5)", namespace)
except Exception as e:
    tb = e.__traceback__
    while tb.tb_next:
        tb = tb.tb_next
    print("Lineno:", tb.tb_lineno)
    print("Exception:", type(e))
    print("Args:", e.args)
    # Get the source line
    code_lines = "scores.pop(5)".split('\n')
    print("Code:", code_lines[tb.tb_lineno - 1])
