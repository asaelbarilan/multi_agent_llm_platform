# agents/prompts.py

code_example = """
**Example Format:**

# Application Name: simple_calculator_app

# File: app.py
{triple_backtick}
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num1 = float(request.form['num1'])
        num2 = float(request.form['num2'])
        result = num1 + num2
        return render_template('result.html', result=result)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
{triple_backtick}

# File: templates/index.html
{triple_backtick}
<!DOCTYPE html>
<html>
<head>
  <title>Simple Calculator</title>
</head>
<body>
  <h1>Simple Calculator</h1>
  <form action="/" method="post">
    Number 1: <input type="number" name="num1"><br>
    Number 2: <input type="number" name="num2"><br>
    <input type="submit" value="Calculate">
  </form>
</body>
</html>
{triple_backtick}

# File: templates/result.html
{triple_backtick}
<!DOCTYPE html>
<html>
<head>
  <title>Calculator Result</title>
</head>
<body>
  <h1>Result: {{ result }}</h1>
</body>
</html>
{triple_backtick}

# File: requirements.txt
{triple_backtick}
flask==2.0.3
werkzeug==2.0.3
{triple_backtick}

Please provide only the application name and code files in this exact format.
"""

solver_main_prompt = """
As the Solver, please provide the code solution to the problem.

**Important Instructions:**

- Use the application name: `{app_name}` throughout your code and file structures.
- Do not change the application name in subsequent responses.
- Use this name consistently in your code and file structures.
- Use Chain-of-Thought (CoT) reasoning to understand and solve the problem.
- If you encounter an error or issue, attempt to solve it. If it doesn't work, try alternative methods.
- Ensure you fully understand the problem by testing your solutions. If the problem persists after a solution attempt, it indicates a misunderstanding.
- If there is an error in code packages try to upgrade the packages
- Provide each code file separately.
- For each file, start with exactly `# File: path/to/filename.ext` or `**File: path/to/filename.ext**` (without any additional text).
- Follow the filename with the code in a code block.
- **Do not specify exact version numbers in `requirements.txt` unless it's critical.**
- Include all necessary files, including JS files, CSS files, templates, etc.
- Do not include any additional text, explanations, or instructions.
- **Do not provide any text outside of the specified format.**
"""

reviewer_main_prompt = """
As the Reviewer, please evaluate the Solver's solution and determine if the code is ready to be executed.

**Important Instructions:**

- Carefully review all code files for completeness and correctness.
- Ensure that all necessary files are included.
- Do not execute the code; base your evaluation on code review only.
- If there are big improvements to make the code is not ready to execute.
- the code is ready when it has all necessary files to execute, it has to have requirement file, front-end back-end files etc.
- If the code is ready, respond with "The problem is solved."
- If not, provide specific feedback on any issues, improvements, or best practices.
"""

reviewer_refine_prompt = """
As the Solver, please refine your solution based on the Reviewer's feedback.

Please provide the updated application name and code files in the same format as before.
"""

execution_refinement_prompt = """
As the Solver, please refine your solution based on the execution feedback.

Please provide the updated application name and code files in the same format as before.
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