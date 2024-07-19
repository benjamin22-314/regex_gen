from typing import Dict

import langchain_openai
from langchain_core.prompts import ChatPromptTemplate

from output_parser import (
    PythonCodeExtractorParser,
    BugLocatorOutputParser,
)

from function_code_with_unit_tests import (
    FunctionCodeWithUnitTests,
)

from run_tests import (
    FindFirstFailingUnitTestFunctionMessage,
)


def llm_generate_unit_tests(
    llm: langchain_openai.chat_models.base.ChatOpenAI, query: str
) -> str:
    """
    Generate unit tests for a hypothetical function that does what is described in `query`.
    """

    unit_test_system_prompt_string = """
    You are a specialized assistant designed to create thorough unit tests for functions involving regular expressions (regex). \
    Your task is to generate comprehensive, self-contained unit tests based on a natural language \
    description of the function's intended behavior.

    Instructions:
    1. Carefully analyze the given description.
    2. Create diverse unit tests that cover all aspects of the function's expected behavior, including:
    - Basic functionality
    - Edge cases
    - Corner cases
    - Boundary conditions
    - Invalid inputs
    - Empty inputs
    - Large inputs
    - Special characters
    - Unicode characters (if applicable)
    - Case sensitivity (if applicable)
    - Multiline inputs (if applicable)
    - Non-matching scenarios
    3. If you need to use a unit test framework, use pytest.
    4. Write individual test functions, not a test class.
    5. Use descriptive test names that clearly indicate the specific scenario being tested.
    6. Include detailed assertions that thoroughly check expected outcomes.
    7. Each assert statement should have a message with the expected output and the observed output.
    8. Do not test input longer than 1000 characters.
    9. For regex functions, consider testing:
    - Pattern matching accuracy
    - Capturing groups
    - Non-capturing groups
    - Lookahead and lookbehind assertions
    - Greedy vs. non-greedy quantifiers
    - Character classes and negated character classes
    - Anchors (start, end, word boundaries)
    - Flags (e.g., re.IGNORECASE, re.MULTILINE, re.DOTALL)
    - Escape sequences
    10. Do not write the actual function implementation or code to run the tests.
    11. Write the name of the function you are testing as a comment at the top of the code block (do not write a place holder function).
    12. Generate at least 10-15 diverse tests to ensure comprehensive coverage.

    Provide your response as a Python code block containing only the unit tests. \
    Ensure that the tests are varied and cover a wide range of scenarios to thoroughly validate the regex function.

    Example input: "Create tests for a function that extracts all valid email addresses from a given text."

    Your task is to generate appropriate unit tests based on similar natural language descriptions, \
    focusing on comprehensive testing of regex functionality.
    """

    unit_test_prompt = ChatPromptTemplate.from_messages(
        [("system", unit_test_system_prompt_string), ("user", "{input}")]
    )

    unit_test_chain = unit_test_prompt | llm | PythonCodeExtractorParser()
    unit_test_code_as_string = unit_test_chain.invoke({"input": query})
    return unit_test_code_as_string


def llm_generate_function_from_unit_tests(
    llm: langchain_openai.chat_models.base.ChatOpenAI,
    unit_test_code_as_string: str,
    query:  str
) -> str:
    """
    Generate a function that will pass the given unit tests.
    """

    function_writer_system_prompt_string = """
    You are a Python code generation assistant. Your task is to create a Python function that satisfies all the provided pytest unit tests. Follow these guidelines:

    1. Consider the function description and the unit tests carefully to understand the function's required behavior.
    2. Write a single Python function that passes all the provided tests.
    3. Use type hints for parameters and return values.
    4. Include a clear and concise docstring explaining the function's purpose and parameters.
    5. Follow Python best practices and PEP 8 style guidelines.
    6. Do not include comments within the function body.
    7. Ensure the function handles all edge cases and scenarios covered in the tests.
    8. If the tests imply the use of regular expressions, import the 're' module and use it appropriately.
    9. Provide only the function definition and its implementation, nothing else.

    Your response should be a Python code block containing only the requested function.
    """
    function_writer_prompt = ChatPromptTemplate.from_messages(
        [("system", function_writer_system_prompt_string), ("user", "{input}")]
    )
    function_writer_chain = function_writer_prompt | llm | PythonCodeExtractorParser()
    target_function_code_as_string = function_writer_chain.invoke(
        {"input": "Function description: " + query + "\n" + unit_test_code_as_string}
    )
    return target_function_code_as_string


def function_and_unit_test_for_bug_finder_template(
    function_code_with_unit_tests: FunctionCodeWithUnitTests,
    first_failing_unit_test_message: FindFirstFailingUnitTestFunctionMessage,
) -> str:
    template = f"""
{function_code_with_unit_tests.get_function_code()}

{function_code_with_unit_tests.unit_test_imports}

{function_code_with_unit_tests.get_unit_test_code(
        unit_test_name=first_failing_unit_test_message.unit_test_name
    )}
    """
    return template


def llm_find_bug(
    llm: langchain_openai.chat_models.base.ChatOpenAI,
    query: str,
    function_code_with_unit_tests: FunctionCodeWithUnitTests,
    first_failing_unit_test_message: FindFirstFailingUnitTestFunctionMessage,
) -> Dict[str, str]:
    """
    Determine if the bug is in the function or the unit test.

    returns dict with bug location and explanation e.g.
    {
        "Likely Bug Location": "Unit Test",
        "Explanation": "The unit test should be adding the two numbers instead of multiplying them."
    }
    """

    bug_finder_prompt_string = f"""
    You are an expert code reviewer and debugger. Given a function and its unit test, 
    your task is to analyze both and determine which one is more likely to contain a bug.

    Your response should be in the following format:
    Likely Bug Location: [Function/Unit Test]
    Explanation: [Your detailed explanation of what went wrong, and how to fix it]

    Please do not return any text after your explanation.
    """

    bug_finder_prompt = ChatPromptTemplate.from_messages(
        [("system", bug_finder_prompt_string), ("user", "{input}")]
    )

    bug_finder_chain = bug_finder_prompt | llm | BugLocatorOutputParser()
    bug_finder_dict = bug_finder_chain.invoke(
        {
            "input": "Function description: " + query + "\n\n" + function_and_unit_test_for_bug_finder_template(
                function_code_with_unit_tests=function_code_with_unit_tests,
                first_failing_unit_test_message=first_failing_unit_test_message,
            )
        }
    )
    return bug_finder_dict


def llm_fix_bug(
    llm: langchain_openai.chat_models.base.ChatOpenAI,
    query: str,
    bug_report_dict: Dict[str, str],
    function_code_with_unit_tests: FunctionCodeWithUnitTests,
    first_failing_unit_test_message: FindFirstFailingUnitTestFunctionMessage,
) -> str:
    """
    """
    
    code_fixer_system_prompt_string = f"""
    You are a Python code generation assistant.
    You will be given a function (including a description of the function) and a unit test.

    There is a bug in the {bug_report_dict['Likely Bug Location']}.

    Instructions;
    1. Consider carefully the function and unit test to determine what went wrong.
    2. Please fix the bug by rewriting the {bug_report_dict['Likely Bug Location']} and only the {bug_report_dict['Likely Bug Location']}.
    3. Do not write any code to run the unit test or function.

    Your response should be a single Python code block containing only the requested code.
    """

    code_fixer_prompt = ChatPromptTemplate.from_messages(
        [("system", code_fixer_system_prompt_string), ("user", "{input}")]
    )

    input = (
        "Function description: "
        + query
        + "\n"
        + bug_report_dict["Explanation"]
        + "\n\nCode\n"
        + function_and_unit_test_for_bug_finder_template(
            function_code_with_unit_tests=function_code_with_unit_tests,
            first_failing_unit_test_message=first_failing_unit_test_message,
        )
    )

    code_fixer_chain = code_fixer_prompt | llm | PythonCodeExtractorParser()
    updated_code_as_string = code_fixer_chain.invoke({"input": input})
    return updated_code_as_string
