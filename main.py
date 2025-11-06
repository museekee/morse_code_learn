try:
    import PySide6
except ImportError:
    import importlib

    import pip

    print("PySide6 is not installed. Installing...")
    pip.main(["install", "PySide6"])
    PySide6 = importlib.import_module("PySide6")
