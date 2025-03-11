import {serve} from "bun";
import {type WhatsAppMessage, type WhatsAppWebhook} from "./models";
import {apartmentAnswer} from "./depabarato_agent.ts";

const WHATSAPP_VERIFY_TOKEN = process.env.WHATSAPP_VERIFY_TOKEN;
const LAST_MSG_EXPIRATION_MINUTES = 15;
const usersLastMessage: Map<string, Date> = new Map();

const WELCOME_MESSAGE = [
    "Hola, soy David el asistente virtual de depabarato.com\n",
    "Yo puedo ayudarte a buscar el departamento más barato en Lima según tus necesidades\n",
    "\n",
    "Ejemplos de consultas de nuestros usuarios:\n",
    "- quiero un depa en san miguel\n",
    "- un depa en Lince con tres dormitorios\n",
    "- busco depa en San Isidro de al menos 100 m2\n",
    "- en San Martin de Porras con 3 cuartos\n",
    "- mínimo 70 m2 y 3 cuartos\n",
    "\n",
    "Dime tu consulta en un solo mensaje y buscaré el departamento más barato para ti",
].join("");

function isFirstMessage(phone: string): boolean {
    const now = new Date();
    const lastMsgTime = usersLastMessage.get(phone) || new Date(2000, 0, 1);
    const lastMsgPlusExpTime = new Date(
        lastMsgTime.getTime() + LAST_MSG_EXPIRATION_MINUTES * 60000
    );

    usersLastMessage.set(phone, now);
    return lastMsgPlusExpTime < now;
}


function getMessagesFromWhatsapp(body: WhatsAppWebhook): WhatsAppMessage[] | null {
    try {
        const messages: WhatsAppMessage[] = [];
        for (const entry of body.entry) {
            for (const change of entry.changes) {
                for (const msg of change.value.messages) {
                    if (msg.type === "text" || msg.type === "image") {
                        messages.push(msg);
                    } else {
                        console.info(`Invalid message type: ${msg.type}`);
                    }
                }
            }
        }
        return messages.length > 0 ? messages : null;
    } catch (e) {
        console.error("Error parsing messages:", e);
        return null;
    }
}

function handleGetWebhook(req: Request): Response {
    const url = new URL(req.url);
    const params = url.searchParams;
    const hubVerifyToken = params.get("hub.verify_token");
    const hubChallenge = params.get("hub.challenge");

    if (hubVerifyToken === WHATSAPP_VERIFY_TOKEN) {
        return new Response(hubChallenge);
    } else {
        console.error("Invalid token, verifyToken=", hubVerifyToken);
        return new Response("Forbidden", {status: 403});
    }
}

async function handlePostWebhook(req: Request): Response {
    const body: WhatsAppWebhook = await req.json() as WhatsAppWebhook;
    const messages = getMessagesFromWhatsapp(body);

    if (!messages) {
        console.error("No messages found");
        return new Response("");
    }

    const toPhone = messages[0]?.from;
    if (!toPhone) {
        console.error("No phone number found");
        return new Response("");
    }

    console.info(`message=${JSON.stringify(messages[0])}, from=${toPhone}`);

    if (isFirstMessage(toPhone)) {
        // Send welcome message using your WhatsApp client
        return new Response("");
    }

    const userQuestion = messages[0]?.text?.body;
    if (userQuestion) {
        // Process user question and send reply using your WhatsApp client
    }

    return new Response("");
}

async function handleTestAgentEndpoint(req: Request): Promise<Response> {
    const body: any = await req.json();
    const userQuestion = body.question;
    const response = await apartmentAnswer(userQuestion);
    return new Response(response);
}

const server = serve({
    port: 3000,
    async fetch(req) {
        console.log(`Got request at ${req.method} ${req.url}`);
        const url = new URL(req.url);

        if (req.method === "GET" && url.pathname === "/api/webhooks/whatsapp") {
            return handleGetWebhook(req);
        }

        if (req.method === "POST" && url.pathname === "/api/webhooks/whatsapp") {
            return handlePostWebhook(req);
        }

        if (req.method === "POST" && url.pathname === "/api/depabarato") {
            return handleTestAgentEndpoint(req);
        }

        return new Response("Not Found", {status: 404});
    },
});

console.info(`Listening on localhost:${server.port}`);