import { Calendar_Repository_Interface } from "../../domain/repositories/calendar_repository_interface";

export class Get_User_Calendars_Use_Case {
    private repository: Calendar_Repository_Interface;

    constructor(repository: Calendar_Repository_Interface) {
        this.repository = repository;
    }

    async execute(user_id: string) {
        return await this.repository.get_all(user_id);
    }
}
