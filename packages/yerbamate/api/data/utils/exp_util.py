import ast

def get_relative_imports(file):
    with open(file, 'r') as f:
        tree = ast.parse(f.read())
    relative_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level > 0:
                relative_imports.append(node.module)
    return relative_imports

