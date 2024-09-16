# agents/environment.py

import asyncio
import os
import re
import subprocess
from .utils import parse_files_from_response, create_unique_folder,extract_application_name
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
        sanitized_name = re.sub(r'\W+', '_', app_name).lower()
        image_tag = f"generated_app_{sanitized_name[:30]}"  # Limit length if necessary
        return image_tag

    async def run_conversation(self):
        # Main method orchestrating the conversation
        async for message in self.collaboration_phase():
            yield message
        if self.solved:
            async for message in self.execution_phase():
                yield message
        else:
            print("Conversation ended without Reviewer agreeing that the code is ready.")
            yield "Conversation ended without Reviewer agreeing that the code is ready."

    async def set_application_name(self):
        agent1 = self.agents[0]
        app_name_prompt_full=app_name_prompt.format(problem_description=self.problem_description)

        response = await agent1.process_message( app_name_prompt_full )
        print(f"{agent1.name} app name response:\n{response}")

        # Extract the app name from the response
        app_name = extract_application_name(response)
        if app_name:
            self.app_name = app_name
            print(f"Application name set to: {self.app_name}")
            self.conversation.append(f"{agent1.name} App Name: {self.app_name}")
        else:
            print("Failed to extract application name from the response. Using default name.")
            self.app_name = "default_app_name"


    async def collaboration_phase(self):
        # Set the application name once before starting the iterations
        await self.set_application_name()

        iteration_count = 0
        max_iterations = 5  # Adjust as needed

        while not self.solved and iteration_count < max_iterations:
            iteration_count += 1
            print(f"\n--- Collaboration Iteration {iteration_count} ---")
            yield f"\n--- Collaboration Iteration {iteration_count} ---"

            conversation_history = "\n".join(self.conversation)

            # Solver provides solution
            response1 = await self.solver_provide_solution(conversation_history)
            yield f"{self.agents[0].name}: {response1}"

            # Save code to files
            folder_name = self.save_code(response1)

            # Reviewer evaluates solution
            response2 = await self.reviewer_evaluate_solution(conversation_history, response1)
            yield f"{self.agents[1].name}: {response2}"

            # Check if code is ready
            if self.check_if_ready(response2):
                print("Reviewer agrees that the code is ready to execute.")
                yield "Reviewer agrees that the code is ready to execute."
                self.solved = True
                self.folder_name = folder_name  # Save folder name for execution phase
                break  # Proceed to execution phase

            # Solver refines solution
            response1 = await self.solver_refine_solution(conversation_history, response2)
            yield f"{self.agents[0].name} refined response:\n{response1}"

            # Save refined code to files
            self.save_code(response1, folder_name)

            # Update conversation history
            self.conversation.append(f"{self.agents[0].name}: {response1}")
            self.conversation.append(f"{self.agents[1].name}: {response2}")

        if not self.solved:
            print("Collaboration phase ended without Reviewer agreeing that the code is ready.")
            yield "Collaboration phase ended without Reviewer agreeing that the code is ready."

    async def execution_phase(self):
        iteration_count = 0
        max_iterations = 5  # Adjust as needed
        execution_feedback = await self.execute_code(self.folder_name)

        # Provide execution feedback to the agents
        self.conversation.append(f"Execution Feedback:\n{execution_feedback}")
        yield f"Execution Feedback:\n{execution_feedback}"

        if "Errors:" in execution_feedback or "Error" in execution_feedback:
            # Allow agents to refine the solution based on execution feedback
            while iteration_count < max_iterations:
                iteration_count += 1
                print(f"\n--- Execution Refinement Iteration {iteration_count} ---")
                yield f"\n--- Execution Refinement Iteration {iteration_count} ---"

                conversation_history = "\n".join(self.conversation)

                # Solver refines solution based on execution feedback
                response1 = await self.solver_refine_execution(conversation_history, execution_feedback)
                yield f"{self.agents[0].name} refined response:\n{response1}"

                # Save refined code to files
                self.save_code(response1, self.folder_name)

                # Execute the refined code
                execution_feedback = await self.execute_code(self.folder_name)
                yield f"Execution Feedback:\n{execution_feedback}"

                # Provide execution feedback to the agents
                self.conversation.append(f"Execution Feedback:\n{execution_feedback}")

                # Check if execution is successful
                if "errors:" in execution_feedback.lower() or "error" in execution_feedback.lower():

                    print("Execution successful.")
                    yield "Execution successful."
                    self.solved = True
                    return
                else:
                    print("Execution successful on first try.")
                    yield "Execution successful on first try."
                    self.solved = True

            if not self.solved:
                print("Execution refinement iterations exhausted without success.")
                yield "Execution refinement iterations exhausted without success."
        else:
            print("Execution successful on first try.")
            yield "Execution successful on first try."
            self.solved = True

    async def solver_provide_solution(self, conversation_history):
        agent1 = self.agents[0]
        triple_backtick = "```"
        solver_prompt = f"""{conversation_history}
        {solver_main_prompt.format(app_name=self.app_name)}
        {code_example}
        """

        response = await agent1.process_message(solver_prompt)
        print(f"{agent1.name} response:\n{response}")
        self.conversation.append(f"{agent1.name}: {response}")
        return response

    async def reviewer_evaluate_solution(self, conversation_history, response1):
        agent2 = self.agents[1]
        review_prompt = f"""{conversation_history}
{self.agents[0].name}: {response1}
{reviewer_main_prompt}
"""
        response = await agent2.process_message(review_prompt)
        print(f"{agent2.name} response:\n{response}")
        self.conversation.append(f"{agent2.name}: {response}")
        return response

    async def solver_refine_solution(self, conversation_history, response2):
        agent1 = self.agents[0]
        refine_prompt = f"""{conversation_history}
{self.agents[1].name}: {response2}
{reviewer_refine_prompt}
"""
        response = await agent1.process_message(refine_prompt)
        print(f"{agent1.name} refined response:\n{response}")
        self.conversation.append(f"{agent1.name}: {response}")
        return response

    async def solver_refine_execution(self, conversation_history, execution_feedback):
        agent1 = self.agents[0]
        refine_prompt = f"""{conversation_history}
Execution Feedback:
{execution_feedback}
{execution_refinement_prompt}
"""
        response = await agent1.process_message(refine_prompt)
        print(f"{agent1.name} refined response:\n{response}")
        self.conversation.append(f"{agent1.name}: {response}")
        return response

    async def execute_code(self, folder_name):
        execution_feedback = self.build_and_run_docker_container(folder_name, 'app.py')
        print(f"Execution Feedback:\n{execution_feedback}")
        return execution_feedback

    def save_code(self, response, folder_name=None):
        files, app_name = parse_files_from_response(response)
        if self.app_name == "default_app_name":
            if app_name:
                self.app_name = app_name  # Set the app name only if not already set
            else:
                print("Application name not found in the response. Using default name.")
        else:
            # Ignore app_name from the response to keep it constant
            app_name = self.app_name

        if folder_name is None:
            folder_name = create_unique_folder(self.app_name)
        self.save_code_to_files(files, folder_name)
        return folder_name

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

    def check_if_ready(self, response):
        # Check if the Reviewer agrees that the code is ready
        if response.lower().startswith("the problem is solved") or response.lower().startswith("the code is ready"):
            return True
        return False
