import asyncio
import subprocess
import sys

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

    async def run_conversation(self):
        iteration_count = 0
        max_iterations = 3  # Prevent infinite loops

        while not self.solved and iteration_count < max_iterations:
            iteration_count += 1
            print(f"--- Iteration {iteration_count} ---")

            # Agent 1 (Solver) provides an initial solution
            agent1 = self.agents[0]
            conversation_history = "\n".join(self.conversation)
            solver_prompt = f"{conversation_history}\nAs the Solver, please provide a solution to the problem."
            response1 = await agent1.process_message(solver_prompt)
            print(f"{agent1.name} response: {response1}")
            self.conversation.append(f"{agent1.name}: {response1}")
            yield f"{agent1.name}: {response1}"

            if self.validate_solution(response1):
                self.solved = await self.verify_solution_with_agents(response1)
                if self.solved:
                    yield "Solution verified, stopping conversation."
                    return

            # Agent 2 (Reviewer) reviews and improves upon Agent 1's response
            agent2 = self.agents[1]
            review_prompt = (
                f"{conversation_history}\n{agent1.name}: {response1}\n"
                "As the Reviewer, please evaluate the Solver's solution and suggest improvements if necessary."
            )
            response2 = await agent2.process_message(review_prompt)
            print(f"{agent2.name} response: {response2}")
            self.conversation.append(f"{agent2.name}: {response2}")
            yield f"{agent2.name}: {response2}"

            if self.validate_solution(response2):
                self.solved = await self.verify_solution_with_agents(response2)
                if self.solved:
                    yield "Solution verified, stopping conversation."
                    return

            # Solver refines the solution based on the Reviewer's feedback
            refine_prompt = (
                f"{conversation_history}\n{agent2.name}: {response2}\n"
                "As the Solver, please refine your solution based on the Reviewer's feedback."
            )
            response1 = await agent1.process_message(refine_prompt)
            print(f"{agent1.name} refined response: {response1}")
            self.conversation.append(f"{agent1.name}: {response1}")
            yield f"{agent1.name}: {response1}"

            # Update the conversation history
            self.conversation.append(f"{agent1.name}: {response1}")
            self.conversation.append(f"{agent2.name}: {response2}")

        if not self.solved:
            print("Conversation ended without a verified solution.")
            yield "Conversation ended without a verified solution."

    def validate_solution(self, response):
        # Check if the response indicates the problem is solved
        if "yes problem is solved" in response.lower() or "the problem is solved" in response.lower():
            print("Validation check: Solved")
            return True
        print("Validation check: Not Solved")
        return False

    async def verify_solution_with_agents(self, solution):
        # Ask all agents if they agree with the solution
        for agent in self.agents:
            verification_prompt = (
                f"The proposed solution is:\n{solution}\n"
                "Do you agree that this solution solves the problem? "
                "Please respond with 'Yes, the problem is solved.' or 'No, the problem is not solved.'"
            )
            verification_response = await agent.process_message(verification_prompt)
            print(f"{agent.name} verification response: {verification_response}")
            if "no" in verification_response.lower():
                print(f"{agent.name} does not agree with the solution.")
                return False
        return True

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
    prompt = "Solve 1+1"

    async def main():
        async for message in orchestrate_problem_solving(agents, prompt):
            print(message)

    asyncio.run(main())
