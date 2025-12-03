import React, { useState, useRef } from 'react';
import { Neo_Button } from './Neo_Button';
import { Event_Attachment } from '../../../domain/models/event_model';
import { Http_S3_Repository } from '../../../infrastructure/repositories/http_s3_repository';
import { Upload_Image_Use_Case } from '../../../application/s3/upload_image_use_case';

interface ImageUploaderProps {
    attachments: Event_Attachment[];
    onChange: (attachments: Event_Attachment[]) => void;
    id?: string;
    disabled?: boolean;
}

// Poor man's DI
const s3_repository = new Http_S3_Repository();
const upload_image_use_case = new Upload_Image_Use_Case(s3_repository);

export const Image_Uploader: React.FC<ImageUploaderProps> = ({ 
    attachments, 
    onChange, 
    id = "image-uploader",
    disabled = false 
}) => {
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files || e.target.files.length === 0) return;
        
        const files = Array.from(e.target.files);
        setUploading(true);
        setError(null);

        try {
            const newAttachments: Event_Attachment[] = [];
            
            // Subir imágenes en paralelo
            const uploadPromises = files.map(file => upload_image_use_case.execute(file));
            const results = await Promise.all(uploadPromises);
            
            newAttachments.push(...results);
            
            // Actualizar lista
            onChange([...attachments, ...newAttachments]);
            
            // Limpiar input
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        } catch (err: any) {
            console.error("Error uploading images:", err);
            setError(err.message || "Error al subir las imágenes.");
        } finally {
            setUploading(false);
        }
    };

    const handleRemove = (index: number) => {
        const newAttachments = [...attachments];
        newAttachments.splice(index, 1);
        onChange(newAttachments);
    };

    return (
        <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
                <label htmlFor={id} className="font-bold text-sm text-basmati-black">
                    Imágenes del evento
                </label>
                
                <input 
                    type="file" 
                    id={id}
                    ref={fileInputRef}
                    className="hidden" 
                    multiple 
                    accept="image/*"
                    onChange={handleFileSelect}
                    disabled={disabled || uploading}
                />
                
                <Neo_Button 
                    type="button" 
                    variant="secondary" 
                    onClick={() => fileInputRef.current?.click()}
                    disabled={disabled || uploading}
                    loading={uploading}
                    className="w-fit"
                >
                    {uploading ? 'Subiendo...' : 'Añadir imágenes'}
                </Neo_Button>
                
                {error && (
                    <p className="text-basmati-red text-sm font-bold mt-1" role="alert">
                        {error}
                    </p>
                )}
            </div>

            {attachments.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                    {attachments.map((att, index) => (
                        <div key={index} className="relative group border-3 border-basmati-black bg-white shadow-hard aspect-square overflow-hidden">
                            <img 
                                src={att.url} 
                                alt={att.filename} 
                                className="w-full h-full object-cover"
                            />
                            
                            {!disabled && (
                                <button
                                    type="button"
                                    onClick={() => handleRemove(index)}
                                    className="absolute top-1 right-1 bg-basmati-red text-white w-8 h-8 flex items-center justify-center border-2 border-basmati-black shadow-sm hover:scale-105 transition-transform"
                                    aria-label={`Eliminar imagen ${att.filename}`}
                                >
                                    ✕
                                </button>
                            )}
                            
                            <div className="absolute bottom-0 left-0 right-0 bg-basmati-black/80 text-white text-xs p-1 truncate px-2">
                                {att.filename}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

