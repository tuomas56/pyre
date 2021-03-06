from pyre.runtime import global_state, builtin_func
from pyre.objspace import PyreList, PyreNumber

@builtin_func(global_state, 'list')
def _list(state, *args):
    return PyreList(list(args))

@builtin_func(global_state, 'sum')
def _sum(state, list):
    return PyreNumber(sum([x.value for x in list.values]))

@builtin_func(global_state, 'range')
def _range(state, *args):
	return PyreList([PyreNumber(x) for x in range(*[int(arg.value) for arg in args])])