import json

import ollama


SYSTEM_PROMPT_FILENAME = "prompts/system_prompt_v3.txt"
USER_PROMPT_FILENAME = "prompts/user_prompt_v3.txt"
def __read_filename(filename: str) -> str:
    with open(filename, "r") as file:
        return file.read()

SYSTEM_PROMPT = __read_filename(SYSTEM_PROMPT_FILENAME)
USER_PROMPT_FILENAME = __read_filename(USER_PROMPT_FILENAME)

def ask_agent(user_question: str) -> str:
    """
    Combine the system prompt and the user question, and send it to the model.
    """
    user_prompt = USER_PROMPT_FILENAME.replace("$USER_QUESTION", user_question)

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
              "role": "system",
              "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt,
             }
        ],
        format={
            "type": "object",
            "properties": {
                "where_clause": {
                    "type": "string"
                }
            }
        }
    )
    return response

def ask_agent_content_json(user_question: str) -> dict:
    response = ask_agent(user_question)
    json_response = json.loads(response["message"]["content"])
    return json_response