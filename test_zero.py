import traceback

try:
    exec("1 / 0", {})
except Exception as e:
    tb = e.__traceback__
    while tb.tb_next:
        tb = tb.tb_next
    print("Lineno:", tb.tb_lineno)
    print("Exception:", type(e))
    print("Args:", e.args)
