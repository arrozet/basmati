import { Event_Attachment } from "../models/event_model";

export interface S3_Repository_Interface {
    /**
     * Sube una imagen directamente al servicio de integración.
     * @param file Archivo a subir
     * @param folder Carpeta opcional
     * @returns Metadatos de la imagen subida adaptados al modelo de adjunto
     */
    upload_image(file: File, folder?: string): Promise<Event_Attachment>;
}



