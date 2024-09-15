# File: agents.py
# Path: C:/Users/Asael/PycharmProjects/multi_agent_llm_platform/agents.py

import asyncio
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class ProblemSolvingAgent:
    def __init__(self, name, model_name='gpt2'):
        self.name = name
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load the tokenizer and model with error handling
        try:
            print(f"Loading model '{self.model_name}' for {self.name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name, trust_remote_code=True).to(self.device)
            self.model.eval()
            print(f"Model '{self.model_name}' loaded successfully for {self.name}.")
        except Exception as e:
            print(f"Error loading model {self.model_name} for {self.name}: {e}")
            raise e

    async def process_message(self, message):
        # Run the model inference in a separate thread to avoid blocking the event loop
        response = await asyncio.to_thread(self.generate_response, message)
        return response

    def generate_response(self, prompt):
        # Encode the input prompt with truncation to prevent exceeding model's max length
        inputs = self.tokenizer(
            prompt,
            return_tensors='pt',
            truncation=True,
            max_length=self.model.config.max_position_embeddings - 150  # Reserve tokens for output
        ).to(self.device)

        # Calculate available tokens for generation
        input_length = inputs['input_ids'].shape[1]
        model_max_length = self.model.config.max_position_embeddings
        available_tokens = model_max_length - input_length

        if available_tokens <= 0:
            return "Error: Input is too long to generate a response."

        # Generate a response with max_new_tokens
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=150,  # Number of tokens to generate
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            do_sample=True,
            eos_token_id=self.tokenizer.eos_token_id
        )

        # Decode the generated tokens
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Optionally remove the prompt from the response
        if response.startswith(prompt):
            response = response[len(prompt):].strip()

        return response

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
            for agent in self.agents:
                # Share the entire conversation history with each agent
                conversation_history = "\n".join(self.conversation)
                response = await agent.process_message(conversation_history)
                print(f"{agent.name} response: {response}")
                self.conversation.append(f"{agent.name}: {response}")
                yield f"{agent.name}: {response}"

                if self.validate_solution(response):
                    self.solved = await self.verify_solution_with_agents(response)
                    if self.solved:
                        yield "Solution verified, stopping conversation."
                        return
            if iteration_count >= max_iterations:
                print("Max iterations reached, stopping conversation.")
                break
        if not self.solved:
            print("Conversation ended without a verified solution.")

    def validate_solution(self, response):
        # Check if the response contextually solves the problem by looking for specific keywords
        if "yes problem is solved" in response.lower() or "we can't solve this" in response.lower():
            print("Validation check: Solved")
            return True
        print("Validation check: Not Solved")
        return False

    async def verify_solution_with_agents(self, solution):
        # Ask all agents if they agree with the solution
        for agent in self.agents:
            verification_prompt = (
                f"The proposed solution is: {solution}\n"
                "Do you agree with this solution? If so, say 'yes problem is solved' and explain why. "
                "If you can't solve the problem, say 'we can't solve this'. If not, explain why not."
            )
            verification_response = await agent.process_message(verification_prompt)
            print(f"{agent.name} verification response: {verification_response}")
            if "no" in verification_response.lower():
                print(f"{agent.name} does not agree with the solution.")
                return False
        return True

def initialize_agents(model_name='gpt2'):
    agent1 = ProblemSolvingAgent("Agent1", model_name)
    agent2 = ProblemSolvingAgent("Agent2", model_name)
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
    agents = initialize_agents(model_name="microsoft/Phi-3.5-MoE-instruct")
    prompt = "Solve 1+1"

    async def main():
        async for message in orchestrate_problem_solving(agents, prompt):
            print(message)

    asyncio.run(main())
