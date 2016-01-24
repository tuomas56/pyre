##The Module System

Modules in Pyre are, like in Python, simply code file. 
When the `import` function is called, the module is simply
read from disk and `eval`ed. The value this returns is then
returned by the call to `import`. Usually, a module will consist
of a module expression, with the body being a block.

A module expression looks like this:

```ruby
module (names) body
```

Where *body* is an expression that is executed when the module is `eval`ed. And *names* is a comma seperated list of identifiers.
Typically this is a block. When a module is loaded, body is executed and then
a module object is created. All the variables in *names* are then set
as attributes of the module object. This allows module to work like this:

*lib.pyr*
```ruby
module (double, triple) do
	let double = def n
		n.mul 2

	let triple = def n
		n.mul 3
end
```

*ipyre*
```ruby
>>> let lib = import("lib")
...
>>> lib.double 2
...
4.0
>>> lib.triple 6
...
18.0
```

##The Extension System

The extension system allows modules to be written in Python. 
This differs from Pyre's Python interop library in a very
important way: extension modules are responsible for their *own*
conversion between Pyre values and Python ones.

In order to make an extension, you simply create a python module
on the `PYTHONPATH` which supplies an `__all__` attribute, containing
a list of values to import into Pyre. These values will be injected in directly
so the module is responsible for outputting Pyre objects, such as those found in
`pyre.objspace`.

In order to load an extension module, use the function `loadex` in the same
way as the `import` function.