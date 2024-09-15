import asyncio
import subprocess
import sys
import os
import re
import hashlib

class ProblemSolvingAgent:
    def __init__(self, name):
        self.name = name

    async def process_message(self, message):
        response = await self.query_ollama(message)
        return response.strip()

    async def query_ollama(self, prompt):
        if sys.platform == "win32":
            # Windows-specific workaround
            result = subprocess.run(
                ["ollama", "run", "llama3"],
                input=prompt.encode('utf-8'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.stdout.decode('utf-8')
        else:
            # Other platforms
            process = await asyncio.create_subprocess_exec(
                "ollama", "run", "llama3",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate(input=prompt.encode('utf-8'))
            return stdout.decode('utf-8')

class Environment:
    def __init__(self):
        self.agents = []
        self.conversation = []
        self.solved = False
        self.app_name = "default_app_name"

    def add_agent(self, agent):
        self.agents.append(agent)

    def initiate_conversation(self, prompt):
        self.conversation.append(f"Initial Prompt: {prompt}")
        self.problem_description = prompt

    def create_image_tag(self, app_name):
        # Generate a simple image tag from the app name
        sanitized_name = re.sub(r'\W+', '_', app_name).lower()
        image_tag = f"generated_app_{sanitized_name[:30]}"  # Limit length if necessary
        return image_tag

    async def run_conversation(self):
        iteration_count = 0
        max_iterations = 5  # Adjust as needed

        # Create a unique folder for this conversation
        folder_name = create_unique_folder(self.problem_description)

        while not self.solved and iteration_count < max_iterations:
            iteration_count += 1
            print(f"\n--- Iteration {iteration_count} ---")

            # Agent 1 (Solver) provides an initial solution
            agent1 = self.agents[0]
            conversation_history = "\n".join(self.conversation)

            triple_backtick = "```"

            solver_prompt = f"""{conversation_history}
As the Solver, please provide the code solution to the problem.

**Important Instructions:**

- Provide an application name in the format `# Application Name: your_app_name`.
- Use this name consistently in your code and file structures if applicable.
- Provide each code file separately.
- For each file, start with exactly `# File: path/to/filename.ext` or `**File: path/to/filename.ext**` (without any additional text).
- Follow the filename with the code in a code block.
- Include all necessary files, including JS files, CSS files, templates, etc.
- Ensure that the `requirements.txt` file includes both `flask==2.0.3` and `werkzeug==2.0.3` to avoid compatibility issues.
- Do not include any additional text, explanations, or instructions.
- **Do not provide any text outside of the specified format.**

**Example Format:**

# Application Name: simple_calculator_app

# File: app.py
{triple_backtick}python
# Your code here
{triple_backtick}

# File: templates/index.html
{triple_backtick}html
<!-- Your HTML code here -->
{triple_backtick}

# File: requirements.txt
{triple_backtick}text
flask==2.0.3
werkzeug==2.0.3
{triple_backtick}

Please provide only the application name and code files in this exact format.
"""

            response1 = await agent1.process_message(solver_prompt)
            print(f"{agent1.name} response:\n{response1}")
            self.conversation.append(f"{agent1.name}: {response1}")

            # Save the generated code and get the app name
            files, app_name = parse_files_from_response(response1)
            if app_name:
                self.app_name = app_name  # Store the app name
            else:
                print("Application name not found in the response. Using default name.")
            self.save_code_to_files(files, folder_name)

            # Execute the code in Docker
            execution_feedback = self.build_and_run_docker_container(folder_name, 'app.py')
            print(f"Execution Feedback:\n{execution_feedback}")

            # Provide execution feedback to the agents
            self.conversation.append(f"Execution Feedback:\n{execution_feedback}")

            # Agent 2 (Reviewer) reviews and evaluates the solution
            agent2 = self.agents[1]

            review_prompt = f"""{conversation_history}
{agent1.name}: {response1}
Execution Feedback:
{execution_feedback}
As the Reviewer, please evaluate the Solver's solution based on the execution results and determine if the problem is solved.

**Important Instructions:**

- If there are any errors in the execution feedback, consider the problem not solved.
- Provide specific feedback on what needs to be fixed.
- Do not declare the problem solved if there are any errors or issues in the execution.

Please provide your response in the following format:

- Start with "The problem is solved." or "The problem is not solved."
- If not solved, provide specific feedback.
"""

            response2 = await agent2.process_message(review_prompt)
            print(f"{agent2.name} response:\n{response2}")
            self.conversation.append(f"{agent2.name}: {response2}")

            # Check if the Reviewer agrees that the problem is solved
            if self.check_if_solved(response2) and "Errors:" not in execution_feedback:
                print("Both agents agree that the problem is solved.")
                self.solved = True
                return

            # Solver refines the solution based on the Reviewer's feedback

            refine_prompt = f"""{conversation_history}
{agent2.name}: {response2}
As the Solver, please refine your solution based on the Reviewer's feedback.

Please provide the updated application name and code files in the same format as before.
"""

            response1 = await agent1.process_message(refine_prompt)
            print(f"{agent1.name} refined response:\n{response1}")
            self.conversation.append(f"{agent1.name}: {response1}")

            # Save the refined code and get the app name
            files, app_name = parse_files_from_response(response1)
            if app_name:
                self.app_name = app_name  # Update the app name if changed
            else:
                print("Application name not found in the refined response. Using existing name.")
            self.save_code_to_files(files, folder_name)

            # Execute the refined code
            execution_feedback = self.build_and_run_docker_container(folder_name, 'app.py')
            print(f"Execution Feedback:\n{execution_feedback}")

            # Provide execution feedback to the agents
            self.conversation.append(f"Execution Feedback:\n{execution_feedback}")

            # Update the conversation history for the next iteration
            self.conversation.append(f"{agent1.name}: {response1}")
            self.conversation.append(f"{agent2.name}: {response2}")

        if not self.solved:
            print("Conversation ended without a verified solution.")

    def save_code_to_files(self, files, folder_name):
        if files:
            for file_path, code in files.items():
                full_path = os.path.join(folder_name, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(code)
        else:
            print("No code files to save from the agent's response.")

    def build_and_run_docker_container(self, folder_name, code_filename):
        # Ensure Dockerfile exists
        self.create_dockerfile(folder_name, code_filename)

        # Build the Docker image
        image_tag = self.create_image_tag(self.app_name)
        build_command = ['docker', 'build', '-t', image_tag, folder_name]
        try:
            subprocess.run(build_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            error_message = f"Docker build failed: {e.stderr.decode()}"
            print(error_message)
            return error_message

        # Run the Docker container with safety options
        run_command = [
            'docker', 'run', '--rm',
            '-p', '5001:5000',  # Changed host port to 5001 to avoid conflicts
            '--memory', '256m', '--cpus', '1.0',
            image_tag
        ]
        try:
            result = subprocess.run(run_command, capture_output=True, text=True, timeout=60)  # Increased timeout
            execution_output = f"Output:\n{result.stdout}\nErrors:\n{result.stderr}"
            return execution_output
        except subprocess.TimeoutExpired:
            return "Execution timed out."
        except subprocess.CalledProcessError as e:
            return f"Execution failed: {e.stderr}"

    def create_dockerfile(self, folder_name, code_filename):
        dockerfile_content = f"""
FROM python:3.9-slim

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

CMD ["python", "{code_filename}"]
"""
        dockerfile_path = os.path.join(folder_name, 'Dockerfile')
        with open(dockerfile_path, 'w') as dockerfile:
            dockerfile.write(dockerfile_content)

    def check_if_solved(self, response):
        # Check if the Reviewer agrees that the problem is solved
        if response.lower().startswith("the problem is solved"):
            return True
        return False

def parse_files_from_response(response):
    files = {}
    app_name = None  # Default name is None

    # Extract application name if provided in '# Application Name: name' or '**Application Name:** name'
    app_name_match = re.search(r'# Application Name:\s*(\S+)', response)
    if app_name_match:
        app_name = app_name_match.group(1).strip()
    else:
        app_name_match = re.search(r'\*\*Application Name:\s*(\S+)\*\*', response)
        if app_name_match:
            app_name = app_name_match.group(1).strip()

    # Pattern to match the expected file format with '# File: filename'
    pattern1 = r'# File: (.*?)\n```(?:.*?)\n(.*?)```'
    matches1 = re.finditer(pattern1, response, re.DOTALL)

    for match in matches1:
        file_path = match.group(1).strip()
        code = match.group(2)

        # Sanitize the file path
        file_path = file_path.replace('\n', '').replace('\r', '').strip()

        # Validate the file path (allow forward slashes)
        if any(c in file_path for c in r'<>:"\\|?*'):
            print(f"Invalid characters found in file path: {file_path}. Skipping this file.")
            continue

        files[file_path] = code

    # If no files found, try to match filenames in bold '**File: filename**'
    if not files:
        pattern2 = r'\*\*File:\s*(.*?)\*\*\n```(?:.*?)\n(.*?)```'
        matches2 = re.finditer(pattern2, response, re.DOTALL)

        for match in matches2:
            file_path = match.group(1).strip()
            code = match.group(2)

            # Sanitize the file path
            file_path = file_path.replace('\n', '').replace('\r', '').strip()

            # Validate the file path (allow forward slashes)
            if any(c in file_path for c in r'<>:"\\|?*'):
                print(f"Invalid characters found in file path: {file_path}. Skipping this file.")
                continue

            files[file_path] = code

    if not files:
        print("No valid code files found in the agent's response.")

    return files, app_name

def create_unique_folder(prompt):
    # Create a hash of the prompt
    folder_name = hashlib.md5(prompt.encode('utf-8')).hexdigest()
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def initialize_agents():
    agent1 = ProblemSolvingAgent("Solver")
    agent2 = ProblemSolvingAgent("Reviewer")
    return [agent1, agent2]

async def orchestrate_problem_solving(agents, prompt):
    env = Environment()
    for agent in agents:
        env.add_agent(agent)

    env.initiate_conversation(prompt)
    await env.run_conversation()

# Usage example
if __name__ == "__main__":
    agents = initialize_agents()
    prompt = "Create a simple calculator web app using Flask that adds two numbers provided by the user."

    async def main():
        await orchestrate_problem_solving(agents, prompt)

    asyncio.run(main())
