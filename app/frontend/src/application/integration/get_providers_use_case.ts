import { Integration_Repository_Interface } from "../../domain/repositories/integration_repository_interface";
import { Provider_Capabilities } from "../../domain/models/integration_models";

/**
 * Caso de uso para obtener los proveedores de calendario soportados.
 */
export class Get_Providers_Use_Case {
    private repository: Integration_Repository_Interface;

    constructor(repository: Integration_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Obtiene la lista de proveedores soportados con sus capacidades.
     * @returns Lista de proveedores con información de capacidades
     */
    async execute(): Promise<Provider_Capabilities[]> {
        return await this.repository.get_providers();
    }
}
