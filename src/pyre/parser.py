"""
(c) Tuomas Laakkonen 2015, under the MIT license.

pyre.parser

A parser for Pyre. Utilizes funcparserlib for functional, monadic parsing.
"""


from funcparserlib.parser import *
from funcparserlib.lexer import make_tokenizer
import re

fwd = forward_decl
eof = finished


def spec(name, regex, flags=None):
    return (name, (regex, flags)) if flags else (name, (regex,))


def tok(type, value=None):
    if value is None:
        return some(lambda t: t.type == type)
    else:
        return some(lambda t: t.type == type and t.value == value)

token_specs = [
    spec(
        'comment',
        r'#.*$',
        re.MULTILINE & re.DOTALL),
    spec(
        'keyword',
        r'(if)|(do)|(else)|(end)|(while)|(def)|(let)|'
        r'(try)|(except)|(break)|(return)'),
    spec(
        'floatn',
        r'[0-9]+\.[0-9]+'),
    spec(
        'intn',
        r'[0-9]+'),
    spec(
        'ident',
        r'[A-Za-z_\$][A-Za-z_0-9\$]*'),
    spec(
        'string',
        r'"[^"]*?"'),
    spec(
        'dot',
        r'\.'),
    spec(
        'comma',
        r','),
    spec(
        'bang',
        r'!'),
    spec(
        'eq',
        r'='),
    spec(
        'lrb',
        r'\('),
    spec(
        'rrb',
        r'\)'),
    spec(
        'ws',
        r'\s+'),
    spec(
        'nl',
        r'\r|\n|\r\n')]


token_types = [spec[0] for spec in token_specs]

ignore_tokens = [
    'ws',
    'nl',
    'comment'
]

tokenizer = make_tokenizer(token_specs)


def tokenize(s):
    return list(filter(lambda x: x.type not in ignore_tokens, tokenizer(s)))


def print_tokens(t):
    print('\n'.join(map(repr, t)))

for type in token_types:
    globals()[type] = tok(type)


def keyword(t):
    return tok('keyword', t)


class AstNode:

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        values = ', '.join('%s=%r' % (x, getattr(self, x))
                           for x in dir(self) if not x.startswith('_'))
        return '%s(%s)' % (self.__class__.__name__, values)


class Number(AstNode):
    pass


class String(AstNode):

    def __str__(self):
        return '"%s"' % self.value


class Name(AstNode):
    pass


class Call(AstNode):

    def __init__(self, value, args):
        self.value = value
        self.args = args

    def __str__(self):
        return '%s(%s)' % (self.value, ', '.join(map(str, self.args)))


class Attr(AstNode):

    def __init__(self, value, name):
        self.value, self.name = value, name

    def __str__(self):
        return '%s.%s' % (self.value, self.name)


class Block(AstNode):

    def __str__(self):
        return 'do\n %s\nend' % ('\n '.join(map(str, self.value)))


class IfExpr(AstNode):

    def __init__(self, cond, body, elsebody):
        self.cond, self.body, self.elsebody = cond, body, elsebody

    def __str__(self):
        return "if %s %s else %s" % (self.cond, self.body, self.elsebody)


class VarExpr(AstNode):

    def __init__(self, var, value):
        self.var, self.value = var.value, value

    def __str__(self):
        return 'var %s = %s' % (self.var, self.value)


class WhileExpr(AstNode):

    def __init__(self, cond, body):
        self.cond, self.body = cond, body

    def __str__(self):
        return 'while %s %s' % (self.cond, self.body)


class DefExpr(AstNode):

    def __init__(self, args, body):
        self.args, self.body = args, body

    def __str__(self):
        return 'def (%s) %s' % (', '.join(self.args), self.body)


class TryExpr(AstNode):

    def __init__(self, body, exceptbody):
        self.body, self.exceptbody = body, exceptbody

    def __str__(self):
        return 'try %s except %s' % (self.body, self.exceptbody)


class BreakExpr(AstNode):

    def __init__(self):
        pass

    def __str__(self):
        return 'break'


class ReturnExpr(AstNode):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'return %s' % self.value


def parse_args(t):
    return [t[0]] + t[1]


def parse_stem(t):
    if t.type == 'intn' or t.type == 'floatn':
        return Number(float(t.value))
    elif t.type == 'string':
        return String(t.value[1:-1])
    elif t.type == 'ident':
        return Name(t.value)


def parse_call(t):
    stem, args = t
    if hasattr(stem, 'type'):
        stem = parse_stem(stem)
    if len(args) == 0:
        return stem
    else:
        for argset in args:
            if hasattr(argset, 'type') and argset.type == 'bang':
                stem = Call(stem, [])
            elif isinstance(argset, tuple):
                stem = Attr(stem, argset[1].value)
            else:
                stem = Call(stem, argset)
        return stem


def parse_def(t):
    args, body = t

    return DefExpr(args, body)


def parse_defargs(t):
    return [t[0].value] + [x.value for x in t[1]]

expr = fwd()

args = expr + many(skip(comma) + expr) >> parse_args

literal = string | floatn | intn

brackets = skip(lrb) + expr + skip(rrb)

call_ = (skip(lrb) + args + skip(rrb)) | bang
attr_ = dot + ident
call = (literal | ident | brackets) + many(call_ | attr_) >> parse_call

block = skip(keyword('do')) + many(expr) + skip(keyword('end')) >> Block

ifexpr = skip(keyword('if')) + expr + expr + \
    maybe(skip(keyword('else')) + expr) >> (lambda t: IfExpr(*t))

varexpr = skip(keyword('let')) + ident + skip(eq) + \
    expr >> (lambda t: VarExpr(*t))

whileexpr = skip(keyword('while')) + expr + expr >> (lambda t: WhileExpr(*t))

defargs = ident + many(skip(comma) + ident) >> parse_defargs
defexpr = skip(keyword('def')) + skip(lrb) + \
    maybe(defargs) + skip(rrb) + expr >> parse_def

tryexpr = skip(keyword('try')) + expr + \
    skip(keyword('except')) + expr >> (lambda t: TryExpr(*t))

breakexpr = skip(keyword('break')) >> (lambda t: BreakExpr())

returnexpr = skip(keyword('return')) + expr >> (lambda t: ReturnExpr(t))

expr.define((breakexpr | returnexpr | call | brackets | block |
             ifexpr | varexpr | whileexpr | defexpr | tryexpr))

toplevel = expr + skip(eof)


def parse(s):
    return toplevel.parse(tokenize(s))
