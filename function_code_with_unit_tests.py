from typing import List, Dict


class FunctionCodeWithUnitTests:
    def __init__(
        self,
        function_code: List[str],
        unit_tests: Dict[str, List[str]],
        unit_test_imports: str,
    ):
        self.function_code = function_code
        self.unit_tests = unit_tests
        self.unit_test_imports = unit_test_imports

    def replace_function_code(self, new_function_code: str) -> None:
        self.function_code.append(new_function_code)

    def replace_unit_test(self, unit_test_name: str, new_unit_test_code: str) -> None:
        self.unit_tests[unit_test_name].append(new_unit_test_code)

    def get_function_code(self) -> str:
        return self.function_code[-1]

    def get_unit_test_code(self, unit_test_name: str) -> str:
        return self.unit_tests[unit_test_name][-1]

    def delete_unit_test_code(self, unit_test_name: str) -> None:
        del self.unit_tests[unit_test_name]
    
    def delete_function_changes(self) -> None:
        self.function_code = self.function_code[:-1]
