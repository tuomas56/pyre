from pyre.objspace import pyre_to_pyre_val, pyre_to_py_val, PyreModule, PyreString
from functools import partial

def pyimport(name):
    name = pyre_to_py_val(name)
    pymod = __import__(name)
    for part in name.split(".")[1:]:
        pymod = getattr(pymod, part)
    names = pymod.__all__ if hasattr(pymod, '__all__') else [name for name in dir(pymod) if not name.startswith('__')]
    mod = PyreModule()
    for name, value in zip(names, map(partial(getattr, pymod), names)):
        mod._setattr(PyreString(name), pyre_to_pyre_val(value))
    return mod

def pyeval(string):
    string = pyre_to_py_val(string)
    return pyre_to_pyre_val(eval(string))

def pyexec(string):
    string = pyre_to_py_val(string)
    exec(string)
    
    
def apply_kw(func, ad):
    func, adict = pyre_to_py_val(func), {pyre_to_py_val(name): pyre_to_py_val(value) 
                for name, value in zip(ad.dict['keys'].values, ad.dict['values'].values)}
    return pyre_to_pyre_val(func(**adict))

__all__ = ['pyimport', 'pyexec', 'pyeval', 'apply_kw']