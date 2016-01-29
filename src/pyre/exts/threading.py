from pyre.objspace import pyre_to_py_val, pyre_to_pyre_val
import threading

def run(func, args):
    func, args = pyre_to_py_val(func), pyre_to_py_val(args)
    threading.Thread(target=func, args=args, daemon=True).run()

__all__ = ['run']