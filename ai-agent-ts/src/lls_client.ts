import {type ChatResponse, Ollama} from 'ollama';


const SYSTEM_PROMPT = await Bun.file("prompts/system_prompt_v3.txt").text();

const ollama = new Ollama();

export async function ask_agent(prompt: string): Promise<ChatResponse> {
    try {
        const response = await ollama.chat({
            model: 'llama3.2',
            messages: [
                {
                    role: 'system',
                    content: SYSTEM_PROMPT
                },
                {
                    role: 'user',
                    content: prompt
                }
            ],
            format: {
                "type": "object",
                "properties": {
                    "where_clause": {
                        "type": "string"
                    }
                }
            }
        });

        return response;
    } catch (error) {
        console.error('Error querying Ollama:', error);
        throw error;
    }
}

export async function ask_agent_as_json(prompt: string): Promise<{ where_clause: string }> {
    const response = await ask_agent(prompt);
    return JSON.parse(response.message.content);
}