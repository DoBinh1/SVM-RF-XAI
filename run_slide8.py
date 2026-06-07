import sys, os

SCRIPT = r"d:\[Lab] HUST\nhà máy\generate_figures.py"
os.chdir(r"d:\[Lab] HUST\nhà máy")
sys.path.insert(0, r"d:\[Lab] HUST\nhà máy")

with open(SCRIPT, encoding="utf-8") as f:
    src = f.read()

# Inject __file__ so os.path.abspath(__file__) works inside exec
ns = {"__file__": SCRIPT}
exec(compile(src, SCRIPT, "exec"), ns)
ns["plot_slide8"]()

