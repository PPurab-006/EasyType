import re

line = 'type "Here is a list:", list 10, 20, 30'
# We have a transpiler line processing order:
# 1. replace strings with __STRING_X__
# line becomes: type __STRING_0__, list 10, 20, 30
# 2. replace type with print
# line becomes: print(__STRING_0__, list 10, 20, 30)
# 3. lists
# line should become: print(__STRING_0__, [10, 20, 30])
