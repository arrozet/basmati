import { S3_Repository_Interface } from "../../domain/repositories/s3_repository_interface";
import { Event_Attachment } from "../../domain/models/event_model";
import { api_client } from "../api/axios_client";

/**
 * Repositorio HTTP para la gestión de imágenes en S3.
 * Se comunica con el Integration Service a través del API Gateway.
 */
export class Http_S3_Repository implements S3_Repository_Interface {
    /**
     * Sube una imagen al servidor (S3) a través del API Gateway.
     * @param file Archivo de imagen a subir.
     * @param folder Carpeta en S3 (default: 'events').
     * @returns Metadatos del archivo subido adaptados al modelo Event_Attachment.
     */
    async upload_image(file: File, folder: string = 'events'): Promise<Event_Attachment> {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('compress', 'true');

        try {
            // Usamos el API Gateway (api_client ya tiene la baseURL del gateway)
            const response = await api_client.post(`/v2/integrations/s3/upload-direct`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                params: {
                    folder: folder
                }
            });

            const metadata = response.data;

            // Mapear respuesta del backend (ImageMetadata) a Event_Attachment
            // El campo uploaded_by se rellena con el usuario dev actual ya que no tenemos auth real
            return {
                filename: metadata.filename,
                url: metadata.url,
                size: metadata.size || file.size,
                mime_type: metadata.content_type || file.type,
                is_image: true,
                uploaded_by: 'user_dev_1', 
                uploaded_at: new Date()
            };
        } catch (error) {
            console.error("Error uploading image to S3:", error);
            throw error;
        }
    }
}
