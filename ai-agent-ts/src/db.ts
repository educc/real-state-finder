import { Database } from "bun:sqlite";
import {DATABASE_SQLITE_FILENAME} from "./config.ts";
import type {Apartment} from "./models.ts";

const db = new Database(DATABASE_SQLITE_FILENAME);

const QUERY_TEMPLATE = `
    WITH RankedApartments AS (
        SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY name ORDER BY price_soles) AS rn
    FROM
    apartment
    WHERE {where_clause}
    )
    SELECT *
    FROM RankedApartments
    WHERE rn = 1
    ORDER BY price_soles
    LIMIT {size};
`

export function get_cheapest_apartments(where_clause: string, size: number): Array<Apartment> {
    const query = db.query(QUERY_TEMPLATE
        .replace('{where_clause}', where_clause)
        .replace('{size}', size.toString()));
    return query.all() as Array<Apartment>;
}