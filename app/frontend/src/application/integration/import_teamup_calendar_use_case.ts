import { Integration_Repository_Interface } from "../../domain/repositories/integration_repository_interface";
import { Teamup_Import_Request } from "../../domain/models/integration_models";

export class Import_Teamup_Calendar_Use_Case {
    private repository: Integration_Repository_Interface;

    constructor(repository: Integration_Repository_Interface) {
        this.repository = repository;
    }

    async execute(request: Teamup_Import_Request) {
        return await this.repository.import_teamup_calendar(request);
    }
}
