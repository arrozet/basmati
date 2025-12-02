import { Integration_Repository_Interface } from "../../domain/repositories/integration_repository_interface";
import { Google_Import_Request } from "../../domain/models/integration_models";

export class Import_Google_Calendar_Use_Case {
    private repository: Integration_Repository_Interface;

    constructor(repository: Integration_Repository_Interface) {
        this.repository = repository;
    }

    async execute(request: Google_Import_Request) {
        return await this.repository.import_google_calendar(request);
    }
}
