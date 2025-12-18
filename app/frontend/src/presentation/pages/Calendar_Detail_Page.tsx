import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faPencil,
  faArrowLeft,
  faClock,
  faEye,
  faEyeSlash,
  faLink,
  faCalendar,
} from "@fortawesome/free-solid-svg-icons";
import { MainLayout } from "../components/layout/MainLayout";
import { Neo_Card } from "../components/ui/Neo_Card";
import { Neo_Button } from "../components/ui/Neo_Button";
import { Comments_Section } from "../components/ui/Comments_Section";
import { Http_Calendar_Repository } from "../../infrastructure/repositories/http_calendar_repository";
import { Calendar_Model } from "../../domain/models/calendar_model";
import { Add_Calendar_Comment_Use_Case } from "../../application/calendar/add_calendar_comment_use_case";
import { use_page_title } from "../hooks/use_page_title";
import { use_user_context } from "../context/UserContext";

// Dependencies
const calendar_repository = new Http_Calendar_Repository();
const add_comment_use_case = new Add_Calendar_Comment_Use_Case(
  calendar_repository
);

export const Calendar_Detail_Page = () => {
  use_page_title("Calendar details");
  const { id } = useParams();
  const { user } = use_user_context();
  const current_user_id = user?.external_id || "user_dev_1";
  const navigate = useNavigate();

  const [loading, set_loading] = useState(true);
  const [error, set_error] = useState<string | null>(null);
  const [calendar, set_calendar] = useState<Calendar_Model | null>(null);

  const fetch_calendar = async () => {
    if (!id) return;
    try {
      const fetched_calendar = await calendar_repository.get_by_id(id);
      if (fetched_calendar) {
        set_calendar(fetched_calendar);
      } else {
        set_error("Calendario no encontrado");
      }
    } catch (err: any) {
      console.error(err);
      if (err.response?.status === 403) {
        set_error("No tienes permiso para ver este calendario");
      } else {
        set_error("Error al cargar el calendario");
      }
    } finally {
      set_loading(false);
    }
  };

  useEffect(() => {
    fetch_calendar();
  }, [id]);

  const handle_add_comment = async (text: string) => {
    if (!calendar || !id) return;

    try {
      const new_comment = await add_comment_use_case.execute(
        id,
        text,
        current_user_id,
        user?.display_name || "Usuario"
      );
      set_calendar((prev) =>
        prev
          ? {
              ...prev,
              comments: [...(prev.comments || []), new_comment],
            }
          : null
      );
    } catch (error) {
      console.error("Error posting comment:", error);
      throw error;
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-basmati-black"></div>
        </div>
      </MainLayout>
    );
  }

  if (error || !calendar) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center h-64 flex-col">
          <div className="text-xl font-bold text-basmati-red mb-4 border-2 border-basmati-black p-4 bg-red-50 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            {error || "Calendario no encontrado"}
          </div>
          <Neo_Button
            onClick={() => navigate("/dashboard")}
            variant="secondary"
          >
            <FontAwesomeIcon icon={faArrowLeft} className="mr-2" /> Volver al
            Dashboard
          </Neo_Button>
        </div>
      </MainLayout>
    );
  }

  // Helpers
  const format_date = (date?: Date) => {
    if (!date) return "N/A";
    return new Date(date).toLocaleDateString("es-ES", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const get_visibility_icon = () => {
    if (calendar.visibility === "private") return faEyeSlash;
    if (calendar.visibility === "unlisted") return faLink;
    return faEye;
  };

  const get_visibility_text = () => {
    if (calendar.visibility === "private") return "Privado";
    if (calendar.visibility === "unlisted") return "No listado";
    return "Público";
  };

  const is_owner = calendar.owner_id === current_user_id;

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto pb-10">
        <div className="mb-4">
          <Neo_Button onClick={() => navigate(-1)} variant="secondary">
            <FontAwesomeIcon icon={faArrowLeft} className="mr-2" /> Volver
          </Neo_Button>
        </div>

        {/* Detalles del Calendario - Compacto */}
        <Neo_Card className="!p-0 border-3 relative mb-6">
          {/* Header con color del calendario */}
          <div
            className="h-4 w-full border-b-3 border-basmati-black"
            style={{
              backgroundColor: calendar.color || "#EBBE4D",
            }}
          ></div>

          <div className="p-6">
            {/* Barra superior: Visibilidad y Botones */}
            <div className="flex justify-between items-start mb-4">
              <span className="inline-flex items-center px-3 py-1 rounded-full border-2 border-basmati-black bg-white text-xs font-bold uppercase tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                <FontAwesomeIcon
                  icon={get_visibility_icon()}
                  className="mr-2"
                />
                {get_visibility_text()}
              </span>
              {is_owner && (
                <Neo_Button
                  onClick={() => navigate(`/calendars/edit/${calendar.id}`)}
                  variant="secondary"
                >
                  <FontAwesomeIcon icon={faPencil} className="mr-2" /> Editar
                </Neo_Button>
              )}
            </div>

            {/* Título */}
            <h1 className="text-3xl md:text-4xl font-black mb-6 leading-tight text-basmati-black">
              {calendar.title}
            </h1>

            {/* Información en grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Creador */}
              <div>
                <h3 className="font-black text-xs mb-2 uppercase tracking-wide text-gray-400">
                  Creador
                </h3>
                <p className="text-base font-bold">
                  {calendar.creator_display_name || "Desconocido"}
                </p>
              </div>

              {/* Fechas */}
              <div>
                <h3 className="font-black text-xs mb-2 uppercase tracking-wide text-gray-400">
                  <FontAwesomeIcon icon={faClock} className="mr-1" />
                  Creado
                </h3>
                <p className="text-sm font-medium">
                  {format_date(calendar.created_at)}
                </p>
              </div>
              <div>
                <h3 className="font-black text-xs mb-2 uppercase tracking-wide text-gray-400">
                  <FontAwesomeIcon icon={faCalendar} className="mr-1" />
                  Actualizado
                </h3>
                <p className="text-sm font-medium">
                  {format_date(calendar.updated_at)}
                </p>
              </div>
            </div>

            {/* Descripción y Keywords si existen */}
            {(calendar.description ||
              (calendar.keywords && calendar.keywords.length > 0)) && (
              <div className="mt-6 space-y-4">
                {calendar.description && (
                  <div>
                    <h3 className="font-black text-xs mb-2 uppercase tracking-wide text-gray-400">
                      Descripción
                    </h3>
                    <div className="prose max-w-none text-basmati-black bg-gray-50 p-3 rounded-sm border-l-4 border-basmati-yellow text-sm">
                      {calendar.description}
                    </div>
                  </div>
                )}

                {calendar.keywords && calendar.keywords.length > 0 && (
                  <div>
                    <h3 className="font-black text-xs mb-2 uppercase tracking-wide text-gray-400">
                      Palabras clave
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {calendar.keywords.map((keyword, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-basmati-yellow border-2 border-basmati-black rounded-full text-sm font-bold shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </Neo_Card>

        {/* Comentarios - Ancho completo */}
        <div className="h-[500px]">
          <Comments_Section
            comments={calendar.comments || []}
            on_add_comment={handle_add_comment}
            current_user_id={current_user_id}
          />
        </div>
      </div>
    </MainLayout>
  );
};
