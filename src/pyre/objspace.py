"""
(c) Tuomas Laakkonen 2015, under the MIT license.

pyre.objspace

An implementation of the basic object-space and native Pyre types.
"""

from pyre.asteval import *


class PyrePyFunc:

    def __init__(self, func):
        self.dict = {}
        self.dict['__call__'] = func


class PyreObject:

    def __init__(self):
        self.dict = {}
        self.dict['setattr'] = PyrePyFunc(self._setattr)
        self.dict['getattr'] = PyrePyFunc(self._getattr)
        self.dict['equals'] = PyrePyFunc(self.equals)
        self.dict['apply'] = PyrePyFunc(self.apply)
        self.dict['str'] = PyrePyFunc(self.str)
        self.eq_vars = []

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


class PyreString(PyreObject):

    def __init__(self, value):
        super().__init__()
        self.value = value
        self.eq_vars.append('value')
        self.dict['len'] = PyrePyFunc(self.len)
        self.dict['num'] = PyrePyFunc(self.num)

    def num(self):
        return PyreNumber(float(self.value))

    def len(self):
        return PyreNumber(len(self.value))

    def __str__(self):
        return str(self.value)


class PyreList(PyreObject):

    def __init__(self, values):
        super().__init__()
        self.values = values
        self.eq_vars.append('values')
        self.dict['get'] = PyrePyFunc(self.get)
        self.dict['set'] = PyrePyFunc(self.set)
        self.dict['map'] = PyrePyFunc(self.map)
        self.dict['len'] = PyrePyFunc(self.len)
        self.dict['filter'] = PyrePyFunc(self.filter)

    def get(self, index):
        return self.values[int(index.value)]

    def set(self, index, value):
        self.values[int(index.value)] = value

    def len(self):
        return PyreNumber(len(self.value))

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
        self.dict['gt'] = PyrePyFunc(self.gt)
        self.dict['lt'] = PyrePyFunc(self.lt)
        self.dict['or'] = PyrePyFunc(self.lor)
        self.dict['and'] = PyrePyFunc(self.land)
        self.dict['not'] = PyrePyFunc(self.lnot)
        self.dict['int'] = PyrePyFunc(self.int)

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
