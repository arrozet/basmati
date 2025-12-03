import React, { useState, useRef, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faComments, faSpinner, faPaperPlane } from '@fortawesome/free-solid-svg-icons';
import { Event_Comment } from '../../../domain/models/event_model';
import { Neo_Button } from './Neo_Button';

interface CommentsSectionProps {
    comments: Event_Comment[];
    on_add_comment: (text: string) => Promise<void>;
    current_user_id: string;
}

export const Comments_Section: React.FC<CommentsSectionProps> = ({ 
    comments, 
    on_add_comment,
    current_user_id 
}) => {
    const [new_comment, set_new_comment] = useState('');
    const [submitting, set_submitting] = useState(false);
    const commentsEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll al último comentario al cargar o añadir
    useEffect(() => {
        if (commentsEndRef.current) {
            commentsEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [comments]);

    const handle_submit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!new_comment.trim()) return;

        set_submitting(true);
        try {
            await on_add_comment(new_comment);
            set_new_comment('');
        } catch (error) {
            console.error("Error adding comment", error);
        } finally {
            set_submitting(false);
        }
    };

    // Formateador de fecha relativo simple
    const time_ago = (date: Date) => {
        const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
        if (seconds < 60) return "hace un momento";
        
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `hace ${minutes} min`;
        
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `hace ${hours} h`;
        
        const days = Math.floor(hours / 24);
        return `hace ${days} días`;
    };

    return (
        <div className="flex flex-col h-full border-3 border-basmati-black bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] rounded-sm overflow-hidden">
            {/* Header de Comentarios */}
            <div className="bg-basmati-bg p-4 border-b-3 border-basmati-black flex justify-between items-center">
                <h3 className="font-black text-lg flex items-center gap-2">
                    <FontAwesomeIcon icon={faComments} className="text-basmati-blue" />
                    Comentarios
                </h3>
                <span className="bg-basmati-black text-white text-xs font-bold px-2 py-1 rounded-full">
                    {comments.length}
                </span>
            </div>

            {/* Lista de comentarios (Scrollable Area) */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                {comments.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center opacity-50 p-4">
                        <FontAwesomeIcon icon={faComments} className="text-4xl mb-2 text-gray-400" />
                        <p className="text-sm font-bold text-gray-500">Aún no hay comentarios.</p>
                        <p className="text-xs text-gray-400">¡Sé el primero en decir algo!</p>
                    </div>
                ) : (
                    comments.map((comment) => {
                        const is_me = comment.author_external_id === current_user_id;
                        return (
                            <div 
                                key={comment.id} 
                                className={`flex flex-col ${is_me ? 'items-end' : 'items-start'}`}
                            >
                                <div className={`max-w-[90%] relative group`}>
                                    {/* Autor y fecha */}
                                    <div className={`flex items-center gap-2 mb-1 text-xs ${is_me ? 'flex-row-reverse' : ''}`}>
                                        <span className="font-bold text-basmati-black">{is_me ? 'Tú' : comment.author_display_name}</span>
                                        <span className="text-gray-400">• {time_ago(comment.created_at)}</span>
                                    </div>
                                    
                                    {/* Burbuja de comentario */}
                                    <div className={`
                                        p-3 border-2 border-basmati-black text-sm shadow-sm whitespace-pre-wrap
                                        ${is_me 
                                            ? 'bg-basmati-blue text-white rounded-l-lg rounded-tr-lg' 
                                            : 'bg-white text-basmati-black rounded-r-lg rounded-tl-lg'}
                                    `}>
                                        {comment.text}
                                    </div>
                                </div>
                            </div>
                        );
                    })
                )}
                <div ref={commentsEndRef} />
            </div>

            {/* Footer: Input Area */}
            <div className="p-3 bg-white border-t-3 border-basmati-black">
                <form onSubmit={handle_submit} className="relative">
                    <textarea
                        className="w-full p-3 pr-12 border-2 border-basmati-black rounded-sm focus:ring-2 focus:ring-basmati-yellow focus:border-basmati-black outline-none resize-none text-sm min-h-[50px] max-h-[120px] shadow-inner bg-gray-50 focus:bg-white transition-colors"
                        rows={2}
                        placeholder="Escribe un comentario..."
                        value={new_comment}
                        onChange={(e) => set_new_comment(e.target.value)}
                        disabled={submitting}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handle_submit(e);
                            }
                        }}
                    />
                    <button 
                        type="submit" 
                        disabled={submitting || !new_comment.trim()}
                        className={`
                            absolute bottom-2 right-2 p-2 rounded-sm flex items-center justify-center transition-all
                            ${!new_comment.trim() 
                                ? 'text-gray-300 cursor-not-allowed' 
                                : 'text-basmati-black bg-basmati-yellow hover:bg-yellow-400 border-2 border-basmati-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:translate-y-[1px] active:translate-x-[1px] active:shadow-none'}
                        `}
                        aria-label="Enviar"
                    >
                        {submitting ? (
                            <FontAwesomeIcon icon={faSpinner} spin />
                        ) : (
                            <FontAwesomeIcon icon={faPaperPlane} />
                        )}
                    </button>
                </form>
                <div className="text-[10px] text-gray-400 mt-1 text-right px-1">
                    Presiona Enter para enviar
                </div>
            </div>
        </div>
    );
};
