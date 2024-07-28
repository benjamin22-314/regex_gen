from langchain_experimental.tools import PythonREPLTool
from function_code_with_unit_tests import FunctionCodeWithUnitTests


class FindFirstFailingUnitTestFunctionMessage:
    def __init__(self, test_pass_status: bool, unit_test_name: str, output: str):
        self.test_pass_status = test_pass_status
        self.unit_test_name = unit_test_name
        self.output = output

    def print_message_details(self):
        print("\ntest_pass_status: " + str(self.test_pass_status))
        print("unit_test_name: " + self.unit_test_name)
        print("output: " + self.output + "\n")

    def message_details(self) -> str:
        return "unit test " + self.unit_test_name + " failed. " + self.output

def find_first_failing_unit_test(
    function_code_with_unit_tests: FunctionCodeWithUnitTests,
) -> FindFirstFailingUnitTestFunctionMessage:

    for i, unit_test_name in enumerate(function_code_with_unit_tests.unit_tests):
        # Example code to execute
        message = run_unit_test(
            function_code_with_unit_tests=function_code_with_unit_tests,
            unit_test_name=unit_test_name,
        )
        if message.test_pass_status == False:
            return message
        print(f"unit test {unit_test_name}() is currently passing. {i+1}/{len(function_code_with_unit_tests.unit_tests)} tests pass.")
    return message


def run_unit_test(
    function_code_with_unit_tests: FunctionCodeWithUnitTests, unit_test_name: str
) -> FindFirstFailingUnitTestFunctionMessage:
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
    output = PythonREPLTool().run(code_to_run)[:-1]
    if not output.endswith("test passed"):
        return FindFirstFailingUnitTestFunctionMessage(
            test_pass_status=False,
            unit_test_name=unit_test_name,
            output=output,
        )
    return FindFirstFailingUnitTestFunctionMessage(
        test_pass_status=True,
        unit_test_name="Na",
        output="The test passes",
    )
