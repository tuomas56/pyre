##Python Interop

In order to enable Python interop in Pyre, simply
load the `pyre.exts.pyinterop` extension. This module
provides three functions: `pyimport`, `pyeval` and `pyexec`.

`pyimport` does exactly what you would think, importing a python module.
It converts the Python module into a Pyre module object.

`pyeval`, evaluates a Python expression and converts it back into
a Pyre value. `pyexec` evaluates a Python statement and returns
None. Bear in mind that this is run *in the context of the interpreter,*
and so use of `pyeval` and `pyexec` is generally considered unsafe.

An example of `pyimport`:

*ipyre*
```ruby
>>> let pyi = loadex("pyre.exts.pyinterop")
...
>>> let random = pyi.pyimport("random")
...
>>> random.random!
...
0.4567892049201930
```