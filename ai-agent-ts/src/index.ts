import {findApartments} from "./depabarato_agent.ts";

const answer = await findApartments("quiero un depa en san isidro")

console.log(answer)