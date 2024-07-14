from langchain_experimental.tools import PythonREPLTool
from function_code_with_unit_tests import FunctionCodeWithUnitTests


class FindFirstFailingUnitTestFunctionMessage:
    def __init__(self, all_tests_pass: bool, unit_test_name: str, output: str):
        self.all_tests_pass = all_tests_pass
        self.unit_test_name = unit_test_name
        self.output = output

    def print_message_details(self):
        print("all_tests_pass: " + str(self.all_tests_pass))
        print("unit_test_name: " + self.unit_test_name)
        print("output: " + self.output)


def find_first_failing_unit_test(
    function_code_with_unit_tests: FunctionCodeWithUnitTests,
) -> FindFirstFailingUnitTestFunctionMessage:

    python_repl = PythonREPLTool()

    for unit_test_name in function_code_with_unit_tests.unit_tests:
        # Example code to execute
        code_to_run = f"""

{function_code_with_unit_tests.unit_test_imports}

{function_code_with_unit_tests.get_function_code()}

{function_code_with_unit_tests.get_unit_test_code(unit_test_name=unit_test_name)}

try:
    {unit_test_name}()
    message = "test passed"
except AssertionError as e:
    message = "Assertion failed: " + str(e)
except Exception as e:
    message = "Error: " + str(e)

print(message)
        """

        # Execute the code
        # print(code_to_run)
        output = python_repl.run(code_to_run)[:-1]
        if not output.endswith("test passed"):
            return FindFirstFailingUnitTestFunctionMessage(
                all_tests_pass=False,
                unit_test_name=unit_test_name,
                output=output,
            )

    return FindFirstFailingUnitTestFunctionMessage(
        all_tests_pass=True,
        unit_test_name="Na",
        output="All tests pass",
    )
