import { User_Repository_Interface } from "../../domain/repositories/user_repository_interface";
import { User_Model } from "../../domain/models/user_model";

/**
 * Caso de uso: Actualizar perfil de usuario.
 * Encapsula la lógica para modificar datos básicos del perfil.
 */
export class Update_User_Profile_Use_Case {
    private repository: User_Repository_Interface;

    constructor(repository: User_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta el caso de uso para actualizar el perfil del usuario.
     * @param user_id - ID del usuario.
     * @param updates - Campos del perfil a actualizar.
     * @returns Promesa con el usuario actualizado.
     * @throws Error si los datos son inválidos.
     */
    async execute(user_id: string, updates: Partial<Pick<User_Model, 'display_name' | 'email' | 'avatar_url'>>): Promise<User_Model> {
        if (!user_id || user_id.trim() === "") {
            throw new Error("El ID de usuario es requerido");
        }

        // Validación básica del email si se proporciona
        if (updates.email && !this.is_valid_email(updates.email)) {
            throw new Error("El formato del correo electrónico no es válido");
        }

        // Validación del nombre visible
        if (updates.display_name && updates.display_name.trim().length < 1) {
            throw new Error("El nombre visible no puede estar vacío");
        }

        return await this.repository.update_user_profile(user_id, updates);
    }

    /**
     * Valida formato básico de email.
     * @param email - Email a validar.
     * @returns true si el formato es válido.
     */
    private is_valid_email(email: string): boolean {
        const email_regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return email_regex.test(email);
    }
}
