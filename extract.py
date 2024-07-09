import ast
import astor


def is_valid_python(code_string):
    """
    # Example usage
    valid_code = \"""
    def hello_world():
        print("Hello, World!")
    \"""

    invalid_code = \"""
    def hello_world()
        print("Hello, World!")
    \"""

    print(f"Valid code: {is_valid_python(valid_code)}")
    print(f"Invalid code: {is_valid_python(invalid_code)}")
    > Valid code: True
    > Invalid code: False
    """
    try:
        ast.parse(code_string)
        return True
    except SyntaxError:
        return False


def extract_function_names(code_string):
    """
    Example usage
    code = \"""
    def hello_world():
        print("Hello, World!")

    def add(a, b):
        return a + b

    class MyClass:
        def method(self):
            pass

    lambda x: x * 2  # This won't be included as it's not a named function
    \"""

    function_names = extract_function_names(code)
    print(function_names)
    > ['hello_world', 'add', 'method']
    """
    try:
        tree = ast.parse(code_string)
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    except SyntaxError:
        return "Error: Invalid Python code"



def extract_function_by_name(code_string, function_name):
    """
    # Example usage
    code = \"""
    def hello_world():
        print("Hello, World!")

    def add(a, b):
        return a + b

    class MyClass:
        def method(self):
            pass

    def complex_function(x, y):
        result = 0
        for i in range(x):
            for j in range(y):
                result += i * j
        return result
    \"""

    # Extract a specific function
    function_name = "complex_function"
    extracted_function = extract_function_by_name(code, function_name)
    print(extracted_function) # it's a string
    > def complex_function(x, y):
        result = 0
        for i in range(x):
            for j in range(y):
                result += i * j
        return result
    """
    try:
        tree = ast.parse(code_string)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return astor.to_source(node)
        return f"Function '{function_name}' not found in the code."
    except SyntaxError:
        return "Error: Invalid Python code"


def extract_imports(code_string):
    """
    # Example usage
    code = \"""
    import os
    import sys
    from datetime import datetime
    from math import pi, sqrt
    import numpy as np
    from .local_module import local_function
    from ..parent_module import parent_function

    def hello_1():
        print("hello 1")

    import blah
    \"""

    imports = extract_imports(code)
    print("\n".join(imports))
    import os
    import sys
    from datetime import datetime
    from math import pi
    from math import sqrt
    import numpy
    from .local_module import local_function
    from ..parent_module import parent_function
    import blah
    """
    try:
        tree = ast.parse(code_string)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ""
                for alias in node.names:
                    if node.level > 0:
                        module = "." * node.level + module
                    imports.append(f"from {module} import {alias.name}")
        
        return imports
    except SyntaxError:
        return ["Error: Invalid Python code"]

