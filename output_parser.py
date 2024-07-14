import re
import ast

from langchain.schema import BaseOutputParser


class PythonCodeExtractorParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        pattern = r"```python\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        if not matches:
            raise ValueError("No Python code block found in the output.")

        code_block = matches[0]

        # Validate the Python code
        try:
            ast.parse(code_block)
        except SyntaxError as e:
            raise ValueError(f"Extracted code is not valid Python: {e}")

        return code_block

    @property
    def _type(self) -> str:
        return "python_code"


class BugLocatorOutputParser(BaseOutputParser):
    def parse(self, text: str):
        lines = text.strip().split("\n")
        result = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result
