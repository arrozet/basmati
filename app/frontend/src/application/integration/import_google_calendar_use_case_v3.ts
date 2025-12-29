import { Integration_Repository_Interface } from "../../domain/repositories/integration_repository_interface";
import { Google_Import_Request_V3, Import_Response_V3 } from "../../domain/models/integration_models";

/**
 * Caso de uso para importar calendarios desde Google Calendar (V3).
 * Utiliza la nueva API V3 con patrón Abstract Factory.
 */
export class Import_Google_Calendar_Use_Case_V3 {
    private repository: Integration_Repository_Interface;

    constructor(repository: Integration_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta la importación de calendarios desde Google Calendar.
     * @param request Datos de importación con token OAuth2
     * @returns Resultado detallado de la importación
     */
    async execute(request: Google_Import_Request_V3): Promise<Import_Response_V3> {
        return await this.repository.import_google_calendar_v3(request);
    }
}
