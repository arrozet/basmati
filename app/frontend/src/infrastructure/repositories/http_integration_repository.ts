import { Integration_Repository_Interface } from "../../domain/repositories/integration_repository_interface";
import { Google_Import_Request, Teamup_Import_Request, Import_Response } from "../../domain/models/integration_models";
import { api_client } from "../api/axios_client";

export class Http_Integration_Repository implements Integration_Repository_Interface {
    async import_google_calendar(request: Google_Import_Request): Promise<Import_Response> {
        const response = await api_client.post('/v1/integrations/google/import', request);
        return response.data;
    }

    async import_teamup_calendar(request: Teamup_Import_Request): Promise<Import_Response> {
        const response = await api_client.post('/v2/teamup/import', request);
        return response.data;
    }
}
