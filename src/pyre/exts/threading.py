from pyre.objspace import pyre_to_pyre_val, pyre_to_py_val, PyreModule, PyreString
from functools import partial
import threading

def run(func, args):
	func, args = map(pyre_to_py_val, (func, args))
	threading.Thread(target=func, args=args, daemon=True).start()

__all__ = ['run']