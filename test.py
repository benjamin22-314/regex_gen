import pytest
from langchain_openai import ChatOpenAI
from llm_calls import llm_find_bug
from function_code_with_unit_tests import FunctionCodeWithUnitTests
from run_tests import FindFirstFailingUnitTestFunctionMessage


@pytest.fixture
def llm():
    return ChatOpenAI(temperature=0, model="gpt-4")


def test_llm_find_bug_add_function_incorrect_function(llm, ):
    query = "Add two numbers"
    function_code = ["def add(a, b):\n    return a - b"]
    unit_tests = {"test_add": ["def test_add():\n    assert add(2, 3) == 5"]}
    unit_test_imports = "import unittest"
    function_code_with_unit_tests = FunctionCodeWithUnitTests(function_code, unit_tests, unit_test_imports)
    failing_test_message = FindFirstFailingUnitTestFunctionMessage(
        False,
        "test_add",
        "AssertionError: assert -1 == 5"
    )

    result = llm_find_bug(
        llm,
        query,
        function_code_with_unit_tests,
        failing_test_message
    )
    assert result["Likely Bug Location"] == "Function"


def test_llm_find_bug_add_function_incorrect_unit_test(llm, ):
    query = "Add two numbers"
    function_code = ["def add(a, b):\n    return a + b"]
    unit_tests = {"test_add": ["def test_add():\n    assert add(2, 4) == 5"]}
    unit_test_imports = "import unittest"
    function_code_with_unit_tests = FunctionCodeWithUnitTests(function_code, unit_tests, unit_test_imports)
    failing_test_message = FindFirstFailingUnitTestFunctionMessage(
        False,
        "test_add",
        "AssertionError: assert 6 == 5"
    )

    result = llm_find_bug(
        llm,
        query,
        function_code_with_unit_tests,
        failing_test_message
    )
    assert result["Likely Bug Location"] == "Unit Test"