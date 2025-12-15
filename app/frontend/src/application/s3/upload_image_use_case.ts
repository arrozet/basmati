import { S3_Repository_Interface } from "../../domain/repositories/s3_repository_interface";
import { Event_Attachment } from "../../domain/models/event_model";

export class Upload_Image_Use_Case {
    private s3_repository: S3_Repository_Interface;

    constructor(s3_repository: S3_Repository_Interface) {
        this.s3_repository = s3_repository;
    }

    /**
     * Sube una imagen al servidor (S3) y retorna los metadatos.
     * @param file Archivo de imagen a subir.
     */
    async execute(file: File): Promise<Event_Attachment> {
        // Validaciones básicas de tamaño y tipo antes de subir
        const MAX_SIZE = 10 * 1024 * 1024; // 10MB
        if (file.size > MAX_SIZE) {
            throw new Error(`La imagen es demasiado grande. Máximo ${MAX_SIZE / 1024 / 1024}MB.`);
        }

        if (!file.type.startsWith('image/')) {
            throw new Error("El archivo debe ser una imagen.");
        }

        return await this.s3_repository.upload_image(file);
    }
}


