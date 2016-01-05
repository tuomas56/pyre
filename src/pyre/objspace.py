"""
(c) Tuomas Laakkonen 2015, under the MIT license.

pyre.objspace

An implementation of the basic object-space and native Pyre types.
"""

from pyre.asteval import *
import collections
import io
from functools import partial

def pyre_truthy(expr):
    if isinstance(expr, PyreNumber) and expr.value == 0:
        return False
    return True

def pyre_call(expr, args):
    return pyre_getattr(expr, '__call__')(*args)

def pyre_getattr(expr, attr):
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
    return attr in expr.dict

def pyre_to_py_val(expr):
    if isinstance(expr, PyreNumber):
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
        obj = object()
        for name, val in expr.dict.items():
            setattr(obj, name, pyre_to_py_val(val))
        return obj

def pyre_to_pyre_val(val):
    if callable(val):
        def _wrapper(*args):
            return pyre_to_pyre_val(val(*list(map(pyre_to_py_val, args))))
        return PyrePyFunc(_wrapper)
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

class PyreEmptyFunc:

    def __init__(self, func):
        self.dict = {}
        self.dict['__call__'] = func

class PyrePyFunc:

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

class PyreModule(PyreObject):
    pass


class PyreBuffer(PyreObject):
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
        return PyreString(self.value * int(times.value))

    def split(self, sep):
        return PyreList([PyreString(x) for x in self.value.split(sep.value)])

    def num(self):
        return PyreNumber(float(self.value))

    def len(self):
        return PyreNumber(len(self.value))

    def __str__(self):
        return str(self.value)

    def encode(self):
        return PyreBytes(self.value.encode())

class PyreList(PyreObject):

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
        self.dict['__iter__'] = PyrePyFunc(lambda: self.values)
        self.dict['index'] = PyrePyFunc(self.index)
        self.dict['take'] = PyrePyFunc(self.take)
        self.dict['drop'] = PyrePyFunc(self.drop)

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
