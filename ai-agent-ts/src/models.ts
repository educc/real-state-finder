
export interface Apartment {
    name: string;
    address: string;
    district: string;
    construction_status: string;
    delivery_date: string;
    price_soles: number;
    bedrooms: number;
    bathrooms: number;
    area_m2: number;
    common_area_count: number;
    rent_price_soles: number;
    investment_ratio: number;
    url: string;
    url_location: string;
    builder: string;
    bank: string;
    phones: string;
    id: string;
    created_at: string;
}

// types.ts
export interface WhatsAppMessage {
    type: string;
    from: string;
    text?: {
        body: string;
    };
}

export interface WhatsAppChange {
    value: {
        messages: WhatsAppMessage[];
    };
}

export interface WhatsAppEntry {
    changes: WhatsAppChange[];
}

export interface WhatsAppWebhook {
    entry: WhatsAppEntry[];
}