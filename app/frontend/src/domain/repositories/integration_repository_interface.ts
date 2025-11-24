import { Google_Import_Request, Teamup_Import_Request, Import_Response } from "../models/integration_models";

export interface Integration_Repository_Interface {
    import_google_calendar(request: Google_Import_Request): Promise<Import_Response>;
    import_teamup_calendar(request: Teamup_Import_Request): Promise<Import_Response>;
}
