import sys
import unicodedata
from collections import defaultdict

token = {
    'BooleanLiteral': 1,
    'EOF': 2,
    'Identifier': 3,
    'Keyword': 4,
    'NullLiteral': 5,
    'NumericLiteral': 6,
    'Punctuator': 7,
    'StringLiteral': 8,
    'RegularExpression': 9,
    'Template': 10
}

TokenName = {v: k for k, v in token.items()}

FnExprTokens = ['(', '{', '[', 'in', 'typeof', 'instanceof', 'new',
                'return', 'case', 'delete', 'throw', 'void',
                # assignment operators
                '=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '>>>=',
                '&=', '|=', '^=', ',',
                # binary/unary operators
                '+', '-', '*', '/', '%', '++', '--', '<<', '>>', '>>>', '&',
                '|', '^', '!', '~', '&&', '||', '?', ':', '===', '==', '>=',
                '<=', '<', '>', '!=', '!==']

syntax = {'AssignmentExpression',
          'AssignmentPattern',
          'ArrayExpression',
          'ArrayPattern',
          'ArrowFunctionExpression',
          'BlockStatement',
          'BinaryExpression',
          'BreakStatement',
          'CallExpression',
          'CatchClause',
          'ClassBody',
          'ClassDeclaration',
          'ClassExpression',
          'ConditionalExpression',
          'ContinueStatement',
          'DoWhileStatement',
          'DebuggerStatement',
          'EmptyStatement',
          'ExportAllDeclaration',
          'ExportDefaultDeclaration',
          'ExportNamedDeclaration',
          'ExportSpecifier',
          'ExpressionStatement',
          'ForStatement',
          'ForInStatement',
          'FunctionDeclaration',
          'FunctionExpression',
          'Identifier',
          'IfStatement',
          'ImportDeclaration',
          'ImportDefaultSpecifier',
          'ImportNamespaceSpecifier',
          'ImportSpecifier',
          'Literal',
          'LabeledStatement',
          'LogicalExpression',
          'MemberExpression',
          'MethodDefinition',
          'NewExpression',
          'ObjectExpression',
          'ObjectPattern',
          'Program',
          'Property',
          'RestElement',
          'ReturnStatement',
          'SequenceExpression',
          'SpreadElement',
          'Super',
          'SwitchCase',
          'SwitchStatement',
          'TaggedTemplateExpression',
          'TemplateElement',
          'TemplateLiteral',
          'ThisExpression',
          'ThrowStatement',
          'TryStatement',
          'UnaryExpression',
          'UpdateExpression',
          'VariableDeclaration',
          'VariableDeclarator',
          'WhileStatement',
          'WithStatement'}

# Error messages should be identical to V8.
messages = {
    'UnexpectedToken': 'Unexpected token %s',
    'UnexpectedNumber': 'Unexpected number',
    'UnexpectedString': 'Unexpected string',
    'UnexpectedIdentifier': 'Unexpected identifier',
    'UnexpectedReserved': 'Unexpected reserved word',
    'UnexpectedTemplate': 'Unexpected quasi %s',
    'UnexpectedEOS': 'Unexpected end of input',
    'NewlineAfterThrow': 'Illegal newline after throw',
    'InvalidRegExp': 'Invalid regular expression',
    'UnterminatedRegExp': 'Invalid regular expression: missing /',
    'InvalidLHSInAssignment': 'Invalid left-hand side in assignment',
    'InvalidLHSInForIn': 'Invalid left-hand side in for-in',
    'MultipleDefaultsInSwitch': 'More than one default clause in switch statement',
    'NoCatchOrFinally': 'Missing catch or finally after try',
    'UnknownLabel': 'Undefined label \'%s\'',
    'Redeclaration': '%s \'%s\' has already been declared',
    'IllegalContinue': 'Illegal continue statement',
    'IllegalBreak': 'Illegal break statement',
    'IllegalReturn': 'Illegal return statement',
    'StrictModeWith': 'Strict mode code may not include a with statement',
    'StrictCatchVariable': 'Catch variable may not be eval or arguments in strict mode',
    'StrictVarName': 'Variable name may not be eval or arguments in strict mode',
    'StrictParamName': 'Parameter name eval or arguments is not allowed in strict mode',
    'StrictParamDupe': 'Strict mode function may not have duplicate parameter names',
    'StrictFunctionName': 'Function name may not be eval or arguments in strict mode',
    'StrictOctalLiteral': 'Octal literals are not allowed in strict mode.',
    'StrictDelete': 'Delete of an unqualified identifier in strict mode.',
    'StrictLHSAssignment': 'Assignment to eval or arguments is not allowed in strict mode',
    'StrictLHSPostfix': 'Postfix increment/decrement may not have eval or arguments operand in strict mode',
    'StrictLHSPrefix': 'Prefix increment/decrement may not have eval or arguments operand in strict mode',
    'StrictReservedWord': 'Use of future reserved word in strict mode',
    'TemplateOctalLiteral': 'Octal literals are not allowed in template strings.',
    'ParameterAfterRestParameter': 'Rest parameter must be last formal parameter',
    'DefaultRestParameter': 'Unexpected token =',
    'ObjectPatternAsRestParameter': 'Unexpected token {',
    'DuplicateProtoProperty': 'Duplicate __proto__ fields are not allowed in object literals',
    'ConstructorSpecialMethod': 'Class constructor may not be an accessor',
    'DuplicateConstructor': 'A class may only have one constructor',
    'StaticPrototype': 'Classes may not have static property named prototype',
    'MissingFromClause': 'Unexpected token',
    'NoAsAfterImportNamespace': 'Unexpected token',
    'InvalidModuleSpecifier': 'Unexpected token',
    'IllegalImportDeclaration': 'Unexpected token',
    'IllegalExportDeclaration': 'Unexpected token'}

PRECEDENCE = {'||': 1,
              '&&': 2,
              '|': 3,
              '^': 4,
              '&': 5,
              '==': 6,
              '!=': 6,
              '===': 6,
              '!==': 6,
              '<': 7,
              '>': 7,
              '<=': 7,
              '>=': 7,
              'instanceof': 7,
              'in': 7,
              '<<': 8,
              '>>': 8,
              '>>>': 8,
              '+': 9,
              '-': 9,
              '*': 11,
              '/': 11,
              '%': 11}


class Token: pass


class Syntax: pass


class Messages: pass


class PlaceHolders:
    ArrowParameterPlaceHolder = 'ArrowParameterPlaceHolder'


for k, v in list(token.items()):
    setattr(Token, k, v)

for e in syntax:
    setattr(Syntax, e, e)

for k, v in list(messages.items()):
    setattr(Messages, k, v)

# http://stackoverflow.com/questions/14245893/efficiently-list-all-characters-in-a-given-unicode-category
BOM = '\uFEFF'
ZWJ = '\u200D'
ZWNJ = '\u200C'
TAB = '\u0009'
VT = '\u000B'
FF = '\u000C'
SP = '\u0020'
NBSP = '\u00A0'
LF = '\u000A'
CR = '\u000D'
LS = '\u2028'
PS = '\u2029'

U_CATEGORIES = defaultdict(list)
for c in map(chr, list(range(sys.maxunicode + 1))):
    U_CATEGORIES[unicodedata.category(c)].append(c)
UNICODE_LETTER = set(U_CATEGORIES['Lu'] + U_CATEGORIES['Ll'] +
                     U_CATEGORIES['Lt'] + U_CATEGORIES['Lm'] +
                     U_CATEGORIES['Lo'] + U_CATEGORIES['Nl'])
UNICODE_COMBINING_MARK = set(U_CATEGORIES['Mn'] + U_CATEGORIES['Mc'])
UNICODE_DIGIT = set(U_CATEGORIES['Nd'])
UNICODE_CONNECTOR_PUNCTUATION = set(U_CATEGORIES['Pc'])
IDENTIFIER_START = UNICODE_LETTER.union({'$', '_'})  # and some fucking unicode escape sequence
IDENTIFIER_PART = IDENTIFIER_START.union(UNICODE_COMBINING_MARK).union(UNICODE_DIGIT).union(
    UNICODE_CONNECTOR_PUNCTUATION).union({ZWJ, ZWNJ})


def isIdentifierStart(ch):
    return (ch if isinstance(ch, str) else chr(ch)) in IDENTIFIER_START


def isIdentifierPart(ch):
    return (ch if isinstance(ch, str) else chr(ch)) in IDENTIFIER_PART


def isWhiteSpace(ch):
    return (ord(ch) if isinstance(ch, str) else ch) in {0x20, 0x09, 0x0B, 0x0C, 0xA0, 0x1680,
                                                        0x180E, 0x2000, 0x2001, 0x2002, 0x2003,
                                                        0x2004, 0x2005, 0x2006, 0x2007, 0x2008,
                                                        0x2009, 0x200A, 0x202F, 0x205F, 0x3000,
                                                        0xFEFF}


def isLineTerminator(ch):
    return (ord(ch) if isinstance(ch, str) else ch) in {0x0A, 0x0D, 0x2028, 0x2029}


OCTAL = {'0', '1', '2', '3', '4', '5', '6', '7'}
DEC = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
HEX = set('0123456789abcdefABCDEF')
HEX_CONV = {'0123456789abcdef'[n]: n for n in range(16)}
for i, e in enumerate('ABCDEF', 10):
    HEX_CONV[e] = i


def isDecimalDigit(ch):
    return (ch if isinstance(ch, str) else chr(ch)) in DEC


def isHexDigit(ch):
    return (ch if isinstance(ch, str) else chr(ch)) in HEX


def isOctalDigit(ch):
    return (ch if isinstance(ch, str) else chr(ch)) in OCTAL


def isFutureReservedWord(w):
    return w in {'enum', 'export', 'import', 'super'}


def isStrictModeReservedWord(w):
    return w in {'implements', 'interface', 'package', 'private', 'protected', 'public', 'static', 'yield', 'let'}


def isRestrictedWord(w):
    return w in {'eval', 'arguments'}


def isKeyword(w):
    # 'const' is specialized as Keyword in V8.
    # 'yield' and 'let' are for compatibility with SpiderMonkey and ES.next.
    # Some others are from future reserved words.
    return w in {'if', 'in', 'do', 'var', 'for', 'new', 'try', 'let', 'this', 'else', 'case',
                 'void', 'with', 'enum', 'while', 'break', 'catch', 'throw', 'const', 'yield',
                 'class', 'super', 'return', 'typeof', 'delete', 'switch', 'export', 'import',
                 'default', 'finally', 'extends', 'function', 'continue', 'debugger', 'instanceof'}


class JsSyntaxError(Exception): pass


if __name__ == '__main__':
    assert isLineTerminator('\n')
    assert isLineTerminator(0x0A)
    assert isIdentifierStart('$')
    assert isIdentifierStart(100)
    assert isWhiteSpace(' ')
