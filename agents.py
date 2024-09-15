import asyncio
import subprocess
import sys
import os

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

    def add_agent(self, agent):
        self.agents.append(agent)

    def initiate_conversation(self, prompt):
        self.conversation.append(f"Initial Prompt: {prompt}")
        self.problem_description = prompt

    async def run_conversation(self):
        iteration_count = 0
        max_iterations = 5  # Adjust as needed

        while not self.solved and iteration_count < max_iterations:
            iteration_count += 1
            print(f"\n--- Iteration {iteration_count} ---")

            # Agent 1 (Solver) provides an initial solution
            agent1 = self.agents[0]
            conversation_history = "\n".join(self.conversation)
            solver_prompt = f"{conversation_history}\nAs the Solver, please provide the code solution to the problem."
            response1 = await agent1.process_message(solver_prompt)
            print(f"{agent1.name} response:\n{response1}")
            self.conversation.append(f"{agent1.name}: {response1}")
            yield f"{agent1.name}: {response1}"

            # Save the generated code
            code_filename = "app.py"  # Or another appropriate filename
            self.save_code_to_file(response1, code_filename)

            # Execute the code in Docker
            execution_feedback = self.build_and_run_docker_container(code_filename)
            print(f"Execution Feedback:\n{execution_feedback}")

            # Provide execution feedback to the agents
            self.conversation.append(f"Execution Feedback:\n{execution_feedback}")

            # Agent 2 (Reviewer) reviews and evaluates the solution
            agent2 = self.agents[1]
            review_prompt = (
                f"{conversation_history}\n{agent1.name}: {response1}\n{execution_feedback}\n"
                "As the Reviewer, please evaluate the Solver's solution based on the execution results and determine if the problem is solved. "
                "If not, suggest improvements."
            )
            response2 = await agent2.process_message(review_prompt)
            print(f"{agent2.name} response:\n{response2}")
            self.conversation.append(f"{agent2.name}: {response2}")
            yield f"{agent2.name}: {response2}"

            # Check if the Reviewer agrees that the problem is solved
            if self.check_if_solved(response2):
                print("Both agents agree that the problem is solved.")
                self.solved = True
                yield "Solution verified by agents, stopping conversation."
                return

            # Solver refines the solution based on the Reviewer's feedback
            refine_prompt = (
                f"{conversation_history}\n{agent2.name}: {response2}\n"
                "As the Solver, please refine your solution based on the Reviewer's feedback."
            )
            response1 = await agent1.process_message(refine_prompt)
            print(f"{agent1.name} refined response:\n{response1}")
            self.conversation.append(f"{agent1.name}: {response1}")
            yield f"{agent1.name}: {response1}"

            # Save the refined code
            self.save_code_to_file(response1, code_filename)

            # Execute the refined code
            execution_feedback = self.build_and_run_docker_container(code_filename)
            print(f"Execution Feedback:\n{execution_feedback}")

            # Provide execution feedback to the agents
            self.conversation.append(f"Execution Feedback:\n{execution_feedback}")

            # Update the conversation history for the next iteration
            self.conversation.append(f"{agent1.name}: {response1}")
            self.conversation.append(f"{agent2.name}: {response2}")

        if not self.solved:
            print("Conversation ended without a verified solution.")
            yield "Conversation ended without a verified solution."

    def save_code_to_file(self, code, filename='app.py'):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(code)

    def build_and_run_docker_container(self, code_filename):
        # Ensure Dockerfile exists
        self.create_dockerfile(code_filename)

        # Build the Docker image
        build_command = ['docker', 'build', '-t', 'generated_app', '.']
        try:
            subprocess.run(build_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            error_message = f"Docker build failed: {e.stderr.decode()}"
            print(error_message)
            return error_message

        # Run the Docker container with safety options
        run_command = [
            'docker', 'run', '--rm',
            '--memory', '256m', '--cpus', '1.0',
            '--read-only', '--network', 'none',
            'generated_app'
        ]
        try:
            result = subprocess.run(run_command, capture_output=True, text=True, timeout=30)
            execution_output = f"Output:\n{result.stdout}\nErrors:\n{result.stderr}"
            return execution_output
        except subprocess.TimeoutExpired:
            return "Execution timed out."
        except subprocess.CalledProcessError as e:
            return f"Execution failed: {e.stderr}"

    def create_dockerfile(self, code_filename):
        dockerfile_content = f"""
        FROM python:3.9-slim

        WORKDIR /app

        COPY {code_filename} /app/{code_filename}

        CMD ["python", "{code_filename}"]
        """
        with open("Dockerfile", "w") as dockerfile:
            dockerfile.write(dockerfile_content)

    def check_if_solved(self, response):
        # Check if the Reviewer agrees that the problem is solved
        if any(phrase in response.lower() for phrase in ["problem is solved", "solution works", "it is correct", "yes,"]):
            return True
        return False

def initialize_agents():
    agent1 = ProblemSolvingAgent("Solver")
    agent2 = ProblemSolvingAgent("Reviewer")
    return [agent1, agent2]

async def orchestrate_problem_solving(agents, prompt):
    env = Environment()
    for agent in agents:
        env.add_agent(agent)

    env.initiate_conversation(prompt)
    async for message in env.run_conversation():
        yield message

# Usage example
if __name__ == "__main__":
    agents = initialize_agents()
    prompt = "Create a simple calculator app that adds two numbers provided by the user."

    async def main():
        async for message in orchestrate_problem_solving(agents, prompt):
            print(message)

    asyncio.run(main())
