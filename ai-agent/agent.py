import ollama


PROMPT_FILENAME = "system_prompt.txt"
def __read_filename(filename: str) -> str:
    with open(filename, "r") as file:
        return file.read()


# Define the system instruction (the "prompt") that will govern the agent's behavior.
SYSTEM_PROMPT = __read_filename(PROMPT_FILENAME)

def ask_agent(user_question: str) -> str:
    """
    Combine the system prompt and the user question, and send it to the model.
    """
    # Construct a prompt that includes both the system instructions and the user input.
    # You can adjust the formatting (for example, using "User:" or similar markers) as needed.
    complete_prompt = f"{SYSTEM_PROMPT}\nUser: {user_question}\nSQL Query:"

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": complete_prompt,
             }
        ]
    )
    return response