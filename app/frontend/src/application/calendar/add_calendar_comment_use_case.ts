import { Http_Calendar_Repository } from "../../infrastructure/repositories/http_calendar_repository";
import { Calendar_Comment } from "../../domain/models/calendar_model";

export class Add_Calendar_Comment_Use_Case {
  private repository: Http_Calendar_Repository;

  constructor(repository: Http_Calendar_Repository) {
    this.repository = repository;
  }

  /**
   * Añade un comentario a un calendario.
   * @param calendar_id ID del calendario
   * @param text Texto del comentario
   * @param user_id ID del usuario
   * @param display_name Nombre del usuario
   */
  async execute(
    calendar_id: string,
    text: string,
    user_id: string,
    display_name: string
  ): Promise<Calendar_Comment> {
    if (!text || text.trim().length === 0) {
      throw new Error("El comentario no puede estar vacío");
    }
    return await this.repository.add_comment(
      calendar_id,
      text,
      user_id,
      display_name
    );
  }
}
