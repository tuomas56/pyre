from pyre.objspace import pyre_to_pyre_val, pyre_to_py_val, PyreModule, PyreString
from functools import partial

def pyimport(name):
    name = pyre_to_py_val(name)
    pymod = __import__(name)
    for part in name.split(".")[1:]:
        pymod = getattr(pymod, part)
    names = [name for name in dir(pymod) if not name.startswith('__')]
    mod = PyreModule()
    for name, value in zip(names, map(partial(getattr, pymod), names)):
        mod._setattr(PyreString(name), pyre_to_pyre_val(value))
    return mod

__all__ = ['pyimport']