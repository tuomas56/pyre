from pyre.runtime import global_state, builtin_func
from pyre.objspace import pyre_to_pyre_val, pyre_to_py_val, PyreModule, PyreString, PyrePyFunc
from functools import partial

@builtin_func(global_state, 'loadex')
def loadex(state, name):
    name = pyre_to_py_val(name)
    pymod = __import__(name)
    for part in name.split(".")[1:]:
        pymod = getattr(pymod, part)
    names = [name for name in pymod.__all__ if not name.startswith('__')]
    mod = PyreModule()
    for name, value in zip(names, map(partial(getattr, pymod), names)):
        if callable(value):
            mod._setattr(PyreString(name), PyrePyFunc(value))
        else:
            mod._setattr(PyreString(name), value)
    return mod

