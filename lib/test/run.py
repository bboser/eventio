import sys

sys.path.append('test')

import tests

for t in dir(tests):
    if not t.startswith('test_'): continue
    try:
        print("-----------", t)
        getattr(tests, t)()
    except Exception as e:
        print("test failed:", e)
