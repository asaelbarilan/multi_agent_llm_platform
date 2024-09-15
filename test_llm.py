# File: test_llm.py

from agents import LocalModelLLM

def main():
    llm = LocalModelLLM(model_name="llama3")
    try:
        prompt = "Create a calculator app."
        response = llm._call(prompt)
        print("LLM Response:")
        print(response)
    except Exception as e:
        print(f"LLM call failed: {e}")

if __name__ == "__main__":
    main()
