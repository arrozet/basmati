import { User_Repository_Interface } from "../../domain/repositories/user_repository_interface";
import { User_Model } from "../../domain/models/user_model";

/**
 * Caso de uso: Obtener perfil de usuario.
 * Encapsula la lógica de negocio para recuperar información del perfil.
 */
export class Get_User_Profile_Use_Case {
    private repository: User_Repository_Interface;

    constructor(repository: User_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta el caso de uso para obtener el perfil del usuario.
     * @param user_id - ID del usuario a consultar.
     * @returns Promesa con el modelo de usuario.
     * @throws Error si el user_id es inválido o vacío.
     */
    async execute(user_id: string): Promise<User_Model> {
        if (!user_id || user_id.trim() === "") {
            throw new Error("El ID de usuario es requerido");
        }
        
        return await this.repository.get_user(user_id);
    }
}
