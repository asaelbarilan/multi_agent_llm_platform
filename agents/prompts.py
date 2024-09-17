# agents/prompts.py
solver_main_prompt = """
As the Solver, please provide the code solution to the problem.

**Important Instructions:**

- Use the application name: `{app_name}` throughout your code and file structures.
- Do not change the application name in subsequent responses.
- Ensure that all necessary files are included, such as:
  - Backend files (e.g., `app.py`)
  - Frontend files (e.g., HTML templates, CSS files)
  - Requirements file (e.g., `requirements.txt`)
  - Any other files necessary to run the application successfully
- dont put specific requirement version numbers 
- Use Chain-of-Thought (CoT) reasoning internally to understand and solve the problem, but **do not include this reasoning in your final answer**.
- If you encounter an error or issue, attempt to solve it. If it doesn't work, try alternative methods.
- Ensure you fully understand the problem by testing your solutions. If the problem persists after a solution attempt, it indicates a misunderstanding.
- If there is an error in code packages, try to upgrade the packages.
- **Provide your response in JSON format only, with no additional text.**

**Important Notes:**

- **All strings in the JSON must be enclosed in double quotes (`"`).**
- **Do not use triple quotes (three consecutive single or double quotes) in your JSON.**
- **Escape all double quotes inside strings with a backslash (`\\`).**
- **Represent newlines in strings using `\\n`.**
- **Do not include any introductory text, explanations, or comments outside the JSON structure.**
- **Ensure that the JSON is valid and properly formatted.**

**JSON Format Example:**

```json
{{
  "application_name": "{app_name}",
  "files": [
    {{
      "path": "path/to/filename.ext",
      "content": "file content here with escaped characters"
    }},
    ...
  ]
}}
Example of Including Code in the JSON content:

json
Copy code
{{
  "path": "app.py",
  "content": "from flask import Flask, request, jsonify\\napp = Flask(\\\"__name__\\\")\\n\\n@app.route(\\\"/add\\\", methods=[\\\"POST\\\"])\\ndef add_numbers():\\n    data = request.get_json()\\n    num1 = int(data[\\\"num1\\\"])\\n    num2 = int(data[\\\"num2\\\"])\\n    result = num1 + num2\\n    return jsonify({{\\\"result\\\": result}})\\n\\nif __name__ == \\\"__main__\\\":\\n    app.run(debug=True)"
}}
Before submitting your response, please ensure that your JSON is valid and can be parsed using json.loads in Python. """

reviewer_main_prompt = """
As the Reviewer, please evaluate the Solver's solution and determine if the code is ready to be executed.

**Important Instructions:**

- Carefully review all code files provided by the Solver for completeness and correctness.
- Ensure that all necessary files are included, such as:
  - Backend files (e.g., `app.py`)
  - Frontend files (e.g., HTML templates, CSS files)
  - Requirements file (e.g., `requirements.txt`)
  - Any other files necessary to run the application successfully
- Verify that the application name `{app_name}` is used consistently throughout the code and file structures.
- **Use internal Chain-of-Thought (CoT) reasoning to evaluate the solution, but do not include this reasoning in your final answer.**
- The code is **not ready** if:
  - **Any necessary files are missing.**
  - **There are significant issues in the code.**
  - **The code would not run correctly as is.**
- Do not execute the code; base your evaluation on code review only.
- The code is ready when it has all necessary files to execute and is free of significant issues.
- If there are improvements to be made or missing components, the code is not ready to execute.
- **Do not accept incomplete code.**
- **Be objective and critical** in your evaluation.
- If the code is not ready, **provide clear, specific, and actionable feedback** on what is missing or needs improvement.

- Do not hesitate to indicate that the problem is not solved if any issues or missing components are found.
- When the problem is not solved, provide clear and specific feedback on what is missing or needs improvement.
- Your feedback should help the Solver understand exactly what changes are necessary.

**Provide your response in JSON format only, with no additional text.**

**JSON Format Example:**

If the code is ready:

```json
{{
  "status": "The problem is solved."
}}
If the code is not ready:

json
Copy code
{{
  "status": "The problem is not solved.",
  "feedback": "Specific feedback on what needs to be fixed or improved."
}}
Do not include any introductory text, explanations, or comments outside the JSON structure.
Ensure that the JSON is valid and properly formatted. """



reviewer_refine_prompt = """
As the Solver, please refine your solution based on the Reviewer's feedback.

Please provide the updated application name and code files in the same format as before.
"""



execution_refinement_prompt = """
As the Solver, please refine your solution based on the execution feedback.

**Important Instructions:**

- Address the issues indicated in the execution feedback.
- Provide your updated response in the same JSON format as before.
- **Do not include any additional text or explanations outside the JSON structure.**
"""


app_name_prompt = """
    Based on the following problem description, suggest a concise and meaningful application name.

    Problem Description:
    '{problem_description}'

    **Important Instructions:**
    - Provide only the application name in the exact format: `# Application Name: your_app_name`
    - The app name should be a single word without spaces or special characters.
    - Do not include any additional text.
    """