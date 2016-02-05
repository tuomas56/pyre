"""
(c) Tuomas Laakkonen 2015, under the MIT license.

pyre.objspace

An implementation of the basic object-space and native Pyre types.
"""

from pyre.asteval import *
from pyre.util import *
import collections
import io
from functools import partial

from pyre.objspace import *
from pyre.asteval import *

def pyre_truthy(expr):
    """Evaluate the truthiness of a value. Everything except 0 (and thus False) is True."""
    if isinstance(expr, PyreNumber) and expr.value == 0:
        return False
    return True

def pyre_call(expr, args):
    """Implements the call operator via the __call__ special method.
       This is expected to return a *Python* callable."""
    return pyre_getattr(expr, '__call__')(*args)

def pyre_getattr(expr, attr):
    """Implements the dot operator. It first attempts to find the __getallattr__ method,
       Which is called to find any attribute. Then, it checks the object's dictionary
       and then if the attribute is not found their, it calls the __getattr__ method."""
    if pyre_hasattr(expr, '__getallattr__'):
        return pyre_call(expr.dict['__getallattr__'], attr)
    elif pyre_hasattr(expr, attr):
        return expr.dict[attr]
    elif pyre_hasattr(expr, '__getattr__'):
        return pyre_call(expr.dict['__getattr__'], attr)
    else:
        raise AttributeError(
            'object "%s" has no attribute "%s"!' % (expr, attr))

def pyre_hasattr(expr, attr):
    """Checks if an attribute exists in an objects dictionary."""
    return attr in expr.dict

class _empty: pass

def pyre_to_py_val(expr):
    """Convert a Pyre value to a Python one. Has direct conversion for some types
       It then falls back to constructing a object."""
    if expr == PyreNumber(1):
        return True
    elif expr == PyreNumber(0):
        return False
    elif expr is Pyre_NONE:
        return None
    elif isinstance(expr, PyreNumber):
        if int(expr.value) == expr.value:
            return int(expr.value)
        else:
            return expr.value
    elif isinstance(expr, PyreString):
        return expr.value.encode().decode("unicode_escape")
    elif isinstance(expr, PyreBytes):
        return expr.value.decode("unicode_escape").encode()
    elif isinstance(expr, (PyreList)):
        return tuple(pyre_to_py_val(x) for x in expr.values)
    elif isinstance(expr, (PyrePyFunc)):
        return expr.dict['__call__']
    elif isinstance(expr, PyreBuffer):
        return expr.value
    elif isinstance(expr, PyreObject):
        obj = _empty()
        for name, val in expr.dict.items():
            setattr(obj, name, pyre_to_py_val(val))
        return obj

def pyre_to_pyre_val(val):
    """Convert a Python value to a Python one. Has direct conversion for some types
       It then falls back to constructing a PyreObject."""
    if callable(val):
        def _wrapper(*args, **kwargs):
            return pyre_to_pyre_val(val(*list(map(pyre_to_py_val, args)), **kwargs))
        return PyrePyFunc(_wrapper)
    elif val is True:
        return Pyre_TRUE
    elif val is False:
        return Pyre_FALSE
    elif val is None:
        return Pyre_NONE
    elif isinstance(val, str):
        return PyreString(val)
    elif isinstance(val, bytes):
        return PyreBytes(val)
    elif isinstance(val, (int, float)):
        return PyreNumber(float(val))
    elif isinstance(val, io.IOBase):
        return PyreBuffer(val)
    elif isinstance(val, collections.Iterable):
        return PyreList([pyre_to_pyre_val(v) for v in val])
    else:
        obj = PyreObject()
        names = [name for name in dir(val) if not name.startswith('__')]
        for name, val in zip(names, map(partial(getattr, val), names)):
            obj._setattr(PyreString(name), pyre_to_pyre_val(val))
        return obj

def pyre_iter_from_py_iter(ite):
    obj = PyreObject()
    obj.dict['__iter__'] = PyrePyFunc(lambda: PyrePyFunc(ite.__next__))
    return obj
        
class MappingDict(dict):
    """A dictionary that *lazily* maps all values by a function.
       TODO: This probably exists somewhere in the stdlib."""
    def __init__(self, func, vals):
        super().__init__()
        self.func = func
        self.update(vals)
        
    def __getitem__(self, key):
        return self.func(super().__getitem__(key))

class PyreEmptyFunc:
    """A Pyre function that is *not* a PyreObject (to prevent infinite recursive data structures.)"""
    def __init__(self, func):
        self.dict = {}
        self.dict['__call__'] = func

class PyrePyFunc:
    """A Pyre fuction that is (for most purposes) a PyreObject."""
    def __init__(self, func):
        self.func = func
        self.dict = {}
        self.dict['__call__'] = func
        self.dict['setattr'] = PyreEmptyFunc(self._setattr)
        self.dict['getattr'] = PyreEmptyFunc(self._getattr)
        self.dict['equals'] = PyreEmptyFunc(self.equals)
        self.dict['apply'] = PyreEmptyFunc(self.apply)
        self.dict['str'] = PyreEmptyFunc(self.str)
        self.dict['dir'] = PyreEmptyFunc(self.dir)
        self.dict['partial'] = PyreEmptyFunc(self.partial)
        self.eq_vars = ['func']

    def partial(self, *args):
        return PyrePyFunc(partial(self.func, *args))

    def dir(self):
        return pyre_to_pyre_val(self.dict.keys())

    def str(self):
        return PyreString(str(self))

    def equals(self, other):
        for var in self.eq_vars:
            if not hasattr(
                other,
                var) or getattr(
                self,
                var) != getattr(
                other,
                    var):
                return Pyre_FALSE
        if len(self.eq_vars) == 0:
            if not self.dict == other.dict:
                return Pyre_FALSE
        return Pyre_TRUE

    def apply(self, func):
        return pyre_call(func, [self])

    def _setattr(self, name, value):
        self.dict[name.value] = value

    def _getattr(self, name):
        return self.dict[name.value]


class PyreObject:

    """Pyre's base object."""
    def __init__(self):
        self.dict = {}
        self.dict['setattr'] = PyrePyFunc(self._setattr)
        self.dict['getattr'] = PyrePyFunc(self._getattr)
        self.dict['equals'] = PyrePyFunc(self.equals)
        self.dict['apply'] = PyrePyFunc(self.apply)
        self.dict['str'] = PyrePyFunc(self.str)
        self.dict['dir'] = PyrePyFunc(self.dir)
        self.eq_vars = []

    def dir(self):
        return pyre_to_pyre_val(self.dict.keys())

    def str(self):
        return PyreString(str(self))

    def equals(self, other):
        for var in self.eq_vars:
            if not hasattr(
                other,
                var) or getattr(
                self,
                var) != getattr(
                other,
                    var):
                return Pyre_FALSE
        if len(self.eq_vars) == 0:
            if not self.dict == other.dict:
                return Pyre_FALSE
        return Pyre_TRUE

    def apply(self, func):
        return pyre_call(func, [self])

    def _setattr(self, name, value):
        self.dict[name.value] = value

    def _getattr(self, name):
        return self.dict[name.value]
       
Pyre_NONE = PyreObject()

class PyreModule(PyreObject):
    """An object to represent a module in Pyre."""
    pass


class PyreBuffer(PyreObject):
    """A Pyre object that represents any Python object that has read, write and close methods."""
    def __init__(self, value):
        super().__init__()
        self.eq_vars.append('value')
        self.value = value
        self.dict['read'] = PyrePyFunc(self.read)
        self.dict['readline'] = PyrePyFunc(self.readline)
        self.dict['write'] = PyrePyFunc(self.write)
        self.dict['close'] = PyrePyFunc(self.close)

    def read(self, n):
        return PyreString(self.value.read(int(n.value)))

    def readline(self):
        return PyreString(self.value.readline())

    def write(self, bytes):
        self.value.write(bytes.value)
        return bytes

    def close(self):
        self.value.close()

class PyreBytes(PyreObject):
    """A Pyre object that represents a Python bytes object."""
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.eq_vars.append('value')
        self.dict['len'] = PyrePyFunc(self.len)
        self.dict['concat'] = PyrePyFunc(self.concat)
        self.dict['rep'] = PyrePyFunc(self.rep)
        self.dict['list'] = PyrePyFunc(self.list)
        self.dict['decode'] = PyrePyFunc(self.decode)

    def list(self):
        return PyreList([PyreBytes(x) for x in self.value])

    def concat(self, other):
        return PyreBytes(self.value + other.value)

    def rep(self, times):
        return PyreBytes(self.value * int(times.value))

    def len(self):
        return PyreNumber(len(self.value))

    def decode(self):
        return PyreString(self.value.decode())

    def __str__(self):
        return str(self.value)

class PyreString(PyreObject):
    """A Pyre object that represents a Python unicode string object."""
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.eq_vars.append('value')
        self.dict['len'] = PyrePyFunc(self.len)
        self.dict['num'] = PyrePyFunc(self.num)
        self.dict['split'] = PyrePyFunc(self.split)
        self.dict['concat'] = PyrePyFunc(self.concat)
        self.dict['rep'] = PyrePyFunc(self.rep)
        self.dict['list'] = PyrePyFunc(self.list)
        self.dict['encode'] = PyrePyFunc(self.encode)

    def list(self):
        return PyreList([PyreString(x) for x in self.value])

    def concat(self, other):
        return PyreString(self.value + other.value)

    def rep(self, times):
        return PyreString(pyre_to_py_val(self) * int(times.value))

    def split(self, sep):
        return PyreList([PyreString(x) for x in pyre_to_py_val(self).split(pyre_to_py_val(sep))])

    def num(self):
        return PyreNumber(float(self.value))

    def len(self):
        return PyreNumber(len(self.value))

    def __str__(self):
        return str(self.value)

    def encode(self):
        return PyreBytes(self.value.encode())

class PyreList(PyreObject):
    """A a Pyre object that represents a mutable Python list."""
    def __init__(self, values):
        super().__init__()
        self.values = values
        self.eq_vars.append('values')
        self.dict['get'] = PyrePyFunc(self.get)
        self.dict['set'] = PyrePyFunc(self.set)
        self.dict['append'] = PyrePyFunc(self.append)
        self.dict['pop'] = PyrePyFunc(self.pop)
        self.dict['join'] = PyrePyFunc(self.join)
        self.dict['map'] = PyrePyFunc(self.map)
        self.dict['len'] = PyrePyFunc(self.len)
        self.dict['filter'] = PyrePyFunc(self.filter)
        self.dict['reverse'] = PyrePyFunc(self.reverse)
        self.dict['__iter__'] = PyrePyFunc(self.iter)
        self.dict['index'] = PyrePyFunc(self.index)
        self.dict['take'] = PyrePyFunc(self.take)
        self.dict['drop'] = PyrePyFunc(self.drop)
        self.dict['enumerate'] = PyrePyFunc(self.enumerate)
        
    def enumerate(self):
        return pyre_iter_from_py_iter(self._enumerate())
        
    def _enumerate(self):
        for i, value in enumerate(self.values):
            yield PyreList([PyreNumber(i), value])

    def iter(self):
        i = -1
        def _next():
            nonlocal i
            i += 1
            if i >= len(self.values):
                raise Exception("stopiter")
            return self.values[i]
        return PyrePyFunc(_next)

    def take(self, num):
        return PyreList(self.values[:int(num.value)])

    def drop(self, num):
        return PyreList(self.values[int(num.value):])

    def index(self, value):
        for i, val in enumerate(self.values):
            if pyre_truthy(val.equals(value)):
               return PyreNumber(i)
        raise IndexError("'%s' not in list!" % value)

    def reverse(self):
        return PyreList(self.values[::-1])

    def append(self, object):
        self.values.append(object)
        return object

    def join(self, sep):
        return PyreString(sep.value.join(map(str, self.values)))

    def pop(self):
        return self.values.pop()

    def get(self, index):
        return self.values[int(index.value)]

    def set(self, index, value):
        self.values[int(index.value)] = value

    def len(self):
        return PyreNumber(len(self.values))

    def map(self, func):
        return PyreList([pyre_call(func, [x]) for x in self.values])

    def filter(self, func):
        return PyreList(
            [x for x in self.values if pyre_truthy(pyre_call(func, [x]))])

    def __str__(self):
        return "[%s]" % (', '.join(map(str, self.values)))

class PyreNumber(PyreObject):
    """A Pyre object that represents a Python integer or floating point."""
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.eq_vars.append('value')
        self.dict['add'] = PyrePyFunc(self.add)
        self.dict['sub'] = PyrePyFunc(self.sub)
        self.dict['mul'] = PyrePyFunc(self.mul)
        self.dict['div'] = PyrePyFunc(self.div)
        self.dict['pow'] = PyrePyFunc(self.pow)
        self.dict['mod'] = PyrePyFunc(self.mod)
        self.dict['gt'] = PyrePyFunc(self.gt)
        self.dict['lt'] = PyrePyFunc(self.lt)
        self.dict['or'] = PyrePyFunc(self.lor)
        self.dict['and'] = PyrePyFunc(self.land)
        self.dict['not'] = PyrePyFunc(self.lnot)
        self.dict['int'] = PyrePyFunc(self.int)
        self.dict['bxor'] = PyrePyFunc(self.bxor)
        self.dict['rshift'] = PyrePyFunc(self.rshift)
        self.dict['lshift'] = PyrePyFunc(self.lshift)

    def rshift(self, other):
        return PyreNumber(self.value >> other.value)

    def lshift(self, other):
        return PyreNumber(self.value << other.value)

    def bxor(self, other):
        return PyreNumber(self.value ^ other.value)

    def mod(self, other):
        return PyreNumber(self.value % other.value)

    def int(self):
        return PyreNumber(int(self.value))

    def lor(self, other):
        if pyre_truthy(self) or pyre_truthy(other):
            return Pyre_TRUE
        else:
            return Pyre_FALSE

    def land(self, other):
        if pyre_truthy(self) and pyre_truthy(other):
            return Pyre_TRUE
        else:
            return Pyre_FALSE

    def lnot(self):
        if pyre_truthy(self):
            return Pyre_FALSE
        else:
            return Pyre_TRUE

    def __str__(self):
        return str(self.value)

    def add(self, other):
        return PyreNumber(self.value + other.value)

    def sub(self, other):
        return PyreNumber(self.value - other.value)

    def mul(self, other):
        return PyreNumber(self.value * other.value)

    def div(self, other):
        return PyreNumber(self.value / other.value)

    def pow(self, other):
        return PyreNumber(self.value ** other.value)

    def gt(self, other):
        if self.value > other.value:
            return Pyre_TRUE
        else:
            return Pyre_FALSE

    def lt(self, other):
        if self.value < other.value:
            return Pyre_TRUE
        else:
            return Pyre_FALSE

Pyre_TRUE = PyreNumber(1)
Pyre_FALSE = PyreNumber(0)