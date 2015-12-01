import codecs
import json
import os

from pyjsparser.pyjsparser import PyJsParser, Node, WrappingNode, node_to_dict


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def create_coverage_log(lines):
    return PyJsParser().parse_to_program("console.log({lines});".format(lines=lines))


def add_coverage_code(node):
    if not node.body:
        return
    if isinstance(node.body, list):
        lines = [x.token['lineNumber'] for x in node.body]
        node.body = [create_coverage_log(lines)] + node.body
        for child in node.body[1:]:
            add_coverage_code(child)
    elif node.type == 'FunctionDeclaration':
        add_coverage_code(node.body)

with codecs.open(os.path.join(BASE_DIR, 'pyjscoverage/static/angular.js'), "r", "utf-8") as f:
    program = PyJsParser().parse_to_program(f.read())

add_coverage_code(program)

output = node_to_dict(program)

with codecs.open(os.path.join(BASE_DIR, 'pyjscoverage/static/output.js'), 'w', "utf-8") as f:
    f.write("xxx = {json}".format(json=json.dumps(output, indent=2, separators=(',', ': '))))
