import ast, sys
files = ["src/config.py", "src/whatsapp_bot_gui.py"]
ok = True
for f in files:
    try:
        ast.parse(open(f, encoding="utf-8").read())
        print(f"OK  {f}")
    except SyntaxError as e:
        print(f"ERR {f}: {e}")
        ok = False
sys.exit(0 if ok else 1)
