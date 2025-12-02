export interface Google_Import_Request {
    user_external_id: string;
    google_access_token: string;
    calendar_ids?: string[];
}

export interface Teamup_Import_Request {
    user_external_id: string;
    calendar_keys: string[];
    teamup_api_key?: string;
}

export interface Import_Response {
    success: boolean;
    message: string;
    imported_sources: string[];
}
