 # Multi-Agent Collaboration System with UI

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview

Welcome to the **Multi-Agent Collaboration System**! This project demonstrates how multiple intelligent agents can interact and collaborate within a shared environment to solve problems, all through an intuitive User Interface.

## Table of Contents

- [Features](#features)
- [What are Multi-Agent Systems?](#what-are-multi-agent-systems)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Agent Collaboration:** Agents communicate and build upon each other's responses to solve complex problems.
- **Interactive UI:** A React-based frontend for users to input prompts and view agent interactions in real-time.
- **Modular Design:** Easily extend the system by adding new agents or modifying existing ones.
- **Asynchronous Processing:** Efficient handling of agent interactions using asynchronous programming.

## What are Multi-Agent Systems?

**Multi-Agent Systems (MAS)** involve multiple autonomous agents that interact within an environment to achieve individual or collective goals. Each agent operates independently but can collaborate with others, making MAS ideal for:

- **Complex Problem Solving:** Tackling tasks too intricate for a single agent.
- **Distributed Computing:** Spreading computational tasks across multiple agents.
- **Simulation and Modeling:** Representing complex systems in fields like economics, biology, and social sciences.

## Getting Started

### Prerequisites

- **Python 3.7+**
- **Node.js and npm**
- **Ollama** (or your preferred LLM platform)
- **Git** (for cloning the repository)

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/asaelbarilan/multi_agent_llm_platform.git
   cd ./multi_agent_llm_platform

### Set Up the Backend

- **Navigate to the project root directory.

- **Create and activate a virtual environment (optional but recommended):

 ```bash
 python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
 ```

### Install Python dependencies:

 ```bash
pip install -r requirements.txt
 ```

- **Ollama Setup: Ensure Ollama is installed and configured on your system. If using API keys or environment variables, set them up accordingly.

### Set Up the Frontend

- **Navigate to the frontend directory:

 ```bash
cd multiagentapp
 ```
### Install npm dependencies:

 ```bash
npm install
 ```
### Usage:

- **Running the Application
- **Start the Backend Server

From the project root directory, run:

 ```bash
uvicorn main:app --reload
 ```

This will start the FastAPI backend server at http://localhost:8000.

- **Start the Frontend Application

- **In a new terminal, navigate to the multiagentapp directory if not already there:

 ```bash
cd multiagentapp  
 ```
Start the React application:

 ```bash
npm start
 ```

This will open the app in your default browser at http://localhost:3000.

### Interacting with the Agents
  - **Enter a Prompt: Type a problem or task into the input field (e.g., "Create a calculator app").
  - **Submit: Click the "Submit" button to initiate the agents' collaboration.
  - **Observe: Watch as the agents interact in the conversation area, building upon each other's responses to solve the problem.

### Project Structure
  - **main.py: The FastAPI backend server handling API requests and streaming responses.
  - **agents.py: Contains the ProblemSolvingAgent and Environment classes that define agent behaviors and interaction protocols.
  - **multiagentapp/: The React frontend application.
  - **src/: Source code for the React app.
  - **public/: Static files and the HTML template.
### Contributing
  - **Contributions are welcome! Here's how you can help:

### Report Bugs:
  If you find a bug, please open an issue with detailed information.
  Suggest Features: Have an idea for a new feature? Let's discuss it!
  Submit Pull Requests: Feel free to fix bugs or add new features and submit a pull request.
### License
  This project is licensed under the MIT License.

### Contact
If you have any questions, suggestions, or would like to collaborate, feel free to reach out:

Email: asaelbarilan@gmail.com
LinkedIn: (https://www.linkedin.com/in/asaelbarilan/)

