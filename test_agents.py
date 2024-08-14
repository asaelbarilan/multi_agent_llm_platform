import unittest
from agents import ProblemSolvingAgent, initialize_agents, orchestrate_problem_solving

class TestAgents(unittest.TestCase):

    def test_problem_solving_agent(self):
        agent = ProblemSolvingAgent("TestAgent")
        response = agent.process_message("Test message")
        self.assertIsInstance(response, str)

    def test_initialize_agents(self):
        agents = initialize_agents()
        self.assertEqual(len(agents), 2)
        self.assertTrue(all(isinstance(agent, ProblemSolvingAgent) for agent in agents))

    def test_orchestrate_problem_solving(self):
        agents = initialize_agents()
        conversation, solution = orchestrate_problem_solving(agents, "Test prompt")
        self.assertIsInstance(conversation, list)
        self.assertIsInstance(solution, str)

if __name__ == '__main__':
    unittest.main()
