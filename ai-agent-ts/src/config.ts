const OLLAMA_BASE_URL = process.env.OLLAMA_BASE_URL || 'http://localhost:11434';
const DATABASE_SQLITE_FILENAME = process.env.DB_FILENAME || 'result.sqlite';
const WHATSAPP_VERIFY_TOKEN = process.env.WHATSAPP_VERIFY_TOKEN;
const WHATSAPP_PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_NUMBER_ID;
const WHATSAPP_ACCESS_TOKEN = process.env.WHATSAPP_ACCESS_TOKEN;

// Validate required environment variables
if (!OLLAMA_BASE_URL) {
    console.error('OLLAMA_BASE_URL is not set');
    process.exit(-1);
}

if (!WHATSAPP_VERIFY_TOKEN) {
    console.error('WHATSAPP_VERIFY_TOKEN is not set');
    process.exit(-1);
}

if (!WHATSAPP_PHONE_NUMBER_ID) {
    console.error('WHATSAPP_PHONE_NUMBER_ID is not set');
    process.exit(-1);
}

if (!WHATSAPP_ACCESS_TOKEN) {
    console.error('WHATSAPP_ACCESS_TOKEN is not set');
    process.exit(-1);
}

async function urlMustWork(url: string): Promise<boolean> {
    try {
        const response = await fetch(url, {
            method: 'GET'
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return true;
    } catch (error) {
        console.error(`Could not connect to ${url}, error: ${error}`);
        process.exit(-1);
    }
}

// Check if URL works
await urlMustWork(OLLAMA_BASE_URL);

export {
    OLLAMA_BASE_URL,
    DATABASE_SQLITE_FILENAME,
    WHATSAPP_VERIFY_TOKEN,
    WHATSAPP_PHONE_NUMBER_ID,
    WHATSAPP_ACCESS_TOKEN
};