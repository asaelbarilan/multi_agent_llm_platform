

code_example=""""

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


solver_main_prompt=""""
As the Solver, please provide the code solution to the problem.

**Important Instructions:**

- Use Chain-of-Thought (CoT) reasoning to understand and solve the problem.
- If you encounter an error or issue, attempt to solve it. If it doesn't work, try alternative methods.
- Ensure you fully understand the problem by testing your solutions. If the problem persists after a solution attempt, it indicates a misunderstanding.
- Provide an application name in the format `# Application Name: your_app_name`.
- Use this name consistently in your code and file structures.
- Provide each code file separately.
- For each file, start with exactly `# File: path/to/filename.ext` or `**File: path/to/filename.ext**` (without any additional text).
- Follow the filename with the code in a code block.
- Include all necessary files, including JS files, CSS files, templates, etc.
- Do not include any additional text, explanations, or instructions.
- **Do not provide any text outside of the specified format.**
"""


reviewer_main_prompt="""As the Reviewer, please evaluate the Solver's solution based on the execution results and determine if the problem is solved.

**Important Instructions:**

- If there are any errors in the execution feedback, consider the problem not solved.
- Provide specific feedback on what needs to be fixed.
- Do not declare the problem solved if there are any errors or issues in the execution.

Please provide your response in the following format:

- Start with "The problem is solved." or "The problem is not solved."
- If not solved, provide specific feedback. """


reviewer_refine_prompt=""" As the Solver, please refine your solution based on the Reviewer's feedback.

    Please provide the updated application name and code files in the same format as before."""