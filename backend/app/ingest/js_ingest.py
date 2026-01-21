from tree_sitter import Parser, Language
import tree_sitter_javascript as ts_js

JS_LANGUAGE = Language(ts_js.language())

parser = Parser(JS_LANGUAGE)    

def node_text(code, node):
    return code[node.start_byte:node.end_byte].decode("utf-8")

def extract_import (root, code):
    imports = []

    def walk(node):
        if node.type == "import_statement":
            for c in node.children:
                if c.type == "string":
                    imports.append(node_text(code, c).strip("'\'"))
        for child in node.children:
            walk(child)
    
    walk(root)

    return imports

def extract_classes(file_path):
    with open(file_path, "rb") as f:
        code = f.read()
    
    tree = parser.parse(code)
    root = tree.root_node

    imports  = extract_import(root, code)
    calls = extract_call(root, code)

    print(imports)

def extract_call(node, code):
    calls = set()

    def walk(n):
        print(n)
        if n.type == "call_expression":
            fn = n.child_by_field_name("function")
            if fn:
                calls.add(node_text(code, fn))
        for c in n.children:
            walk(c)
    walk(node)

    return list(calls)

def extract_function(node, code):
    function_chunk = []
    imports = extract_import(node, code)

    def walk(n):
        if n.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            function_name = node_text(n, name_node)
            
            function_chunk.append({
                "type": "function",
                "name": function_name,
                "file_path": "file path",
                "language": "javascript",
                "import": imports,
                "parametre": "parametre",
                "code": node_text(node, code)
            })

        for f in node.children:
            walk(f)
    
    walk(node)
    return function_chunk

def mutates_state(node, code):
    mutated = set()

    def walk(n):
        if n.type == "assignment_expression":
            left = n.child_by_field_name("left")
            if left and left.type == "member_expression":
                if "this." in node_text(code, left):
                    mutated.add(node_text(code, left))
        for c in n.children:
            walk(c)
    walk(node)
    return mutated

def extract_methode(class_node, code):
    methods = []

    for child in class_node.children:
        if child.type == "class_body":
            for member in child.children:
                if member.type == "method_definition":
                    name_node = member.child_by_field_name("name")
                    name = node_text(code, name_node)

                    params_node = member.child_by_field_name("parameters")
                    params = []
                    if params_node:
                        for p in params_node.children:
                            if p.type == "identifier":
                                params.append(node_text(code, p))

                    methods.append({
                        "name": name,
                        "params": params,
                        "calls": extract_call(member, code),
                        "mutatesState": bool(mutates_state(member)),
                        "mutations": mutates_state(member),
                        "code": node_text(code, member)
                    })
    
    return methods


def extract_classes(node, code):
    class_chunk = []

    imports = extract_import(node, code)

    def walk(n):
        if n.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            class_name = node_text(n, name_node)
            methods = extract_methode(n, code)

            class_chunk.append({
                "type": "class",
                "name": class_name,
                "file_path": "file path",
                "language": "javascript",
                "import": imports,
                "constructor": "constructor",
                "methode": methods,
                "code": node_text(node, code)
            })
    
        for c in node.children:
            walk(c)
    walk(node)
    return class_chunk
    
