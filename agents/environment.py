# agents/environment.py

import asyncio
import os
import re
import subprocess
from .utils import parse_files_from_response, create_unique_folder
from .prompts import *

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

        while not self.solved and iteration_count < max_iterations:
            iteration_count += 1
            print(f"\n--- Iteration {iteration_count} ---")
            yield f"\n--- Iteration {iteration_count} ---"

            # Agent 1 (Solver) provides an initial solution
            agent1 = self.agents[0]
            conversation_history = "\n".join(self.conversation)

            triple_backtick = "```"

            solver_prompt = f"""{conversation_history}
    {solver_main_prompt}
    {code_example}
    """

            response1 = await agent1.process_message(solver_prompt)
            print(f"{agent1.name} response:\n{response1}")
            self.conversation.append(f"{agent1.name}: {response1}")
            yield f"{agent1.name}: {response1}"

            # Save the generated code and get the app name
            files, app_name = parse_files_from_response(response1)

            # Create a unique folder for this conversation
            folder_name = create_unique_folder(app_name)

            if app_name:
                self.app_name = app_name  # Store the app name
            else:
                print("Application name not found in the response. Using default name.")
            self.save_code_to_files(files, folder_name)

            # Execute the code in Docker
            execution_feedback = self.build_and_run_docker_container(folder_name, 'app.py')
            print(f"Execution Feedback:\n{execution_feedback}")
            yield f"Execution Feedback:\n{execution_feedback}"

            # Provide execution feedback to the agents
            self.conversation.append(f"Execution Feedback:\n{execution_feedback}")

            # Agent 2 (Reviewer) reviews and evaluates the solution
            agent2 = self.agents[1]

            review_prompt = f"""{conversation_history}
    {agent1.name}: {response1}
    Execution Feedback:
    {execution_feedback}
    {reviewer_main_prompt}
    """

            response2 = await agent2.process_message(review_prompt)
            print(f"{agent2.name} response:\n{response2}")
            self.conversation.append(f"{agent2.name}: {response2}")
            yield f"{agent2.name}: {response2}"

            # Check if the Reviewer agrees that the problem is solved and no execution errors
            if self.check_if_solved(response2) and "Errors:" not in execution_feedback:
                print("Both agents agree that the problem is solved.")
                self.solved = True
                yield "Both agents agree that the problem is solved."
                return

            # Solver refines the solution based on the Reviewer's feedback

            refine_prompt = f"""{conversation_history}
    {agent2.name}: {response2}
   {reviewer_refine_prompt}
    """

            response1 = await agent1.process_message(refine_prompt)
            print(f"{agent1.name} refined response:\n{response1}")
            self.conversation.append(f"{agent1.name}: {response1}")
            yield f"{agent1.name} refined response:\n{response1}"

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
            yield f"Execution Feedback:\n{execution_feedback}"

            # Provide execution feedback to the agents
            self.conversation.append(f"Execution Feedback:\n{execution_feedback}")

            # Update the conversation history for the next iteration
            self.conversation.append(f"{agent1.name}: {response1}")
            self.conversation.append(f"{agent2.name}: {response2}")

        if not self.solved:
            print("Conversation ended without a verified solution.")
            yield "Conversation ended without a verified solution."

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