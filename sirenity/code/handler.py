import ast
import contextlib
import os
from io import StringIO

ALLOWED_MODULES = ["math"]


class CodeHandler:
    """A class used to handle code submissions from users"""

    def __init__(self, code: str) -> None:
        self.code = code

    def safe_run(self):
        """Safetly runs python code"""
        tree = ast.parse(self.code)
        safe_nodes = self.get_safe_nodes()
        for node in tree.body:
            node_name = type(node).__name__
            if node_name == "Import":
                for module in node.names:
                    if module.name not in ALLOWED_MODULES:
                        raise ValueError(f"unsafe module, contains {module.name}")
            elif node_name not in safe_nodes:
                raise ValueError(f"unsafe expression, contains {node_name}")

        fout = StringIO()
        with contextlib.redirect_stdout(fout):
            exec(self.code)

        return fout.getvalue()

    def get_safe_nodes(self) -> list:
        """Get all nodes types allowed from allowed_nodes.txt"""
        filename = "allowed_nodes.txt"
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
        with open(file_path, "r") as file:
            allowed_nodes = file.readlines()
        return allowed_nodes
