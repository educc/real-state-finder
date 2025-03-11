import {get_cheapest_apartments} from "./db.ts";
import {ask_agent_as_json} from "./lls_client.ts";
import type {Apartment} from "./models.ts";


export async function findApartments(userQuestion: string): Promise<[boolean, Apartment[]]> {
    try {

        const rs = await ask_agent_as_json(userQuestion);

        const logJson = {
            user_question: userQuestion,
            where_clause: rs.where_clause
        };
        console.info(JSON.stringify(logJson));

        let cheapestApartments = get_cheapest_apartments(rs.where_clause, 3);
        return [true, cheapestApartments];
    }catch (err){
        console.error(err);
        return [false, []];
    }
}