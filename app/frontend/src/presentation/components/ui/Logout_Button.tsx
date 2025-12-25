import React from "react";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSignOutAlt } from "@fortawesome/free-solid-svg-icons";
import { use_user_context } from "../../context/UserContext";

interface LogoutButtonProps {
  /**
   * Variante del botón: "icon" muestra solo el icono, "text" muestra texto con icono
   */
  variant?: "icon" | "text";
  /**
   * Clases CSS adicionales
   */
  className?: string;
  /**
   * Título del botón (tooltip)
   */
  title?: string;
  /**
   * Label de accesibilidad
   */
  "aria-label"?: string;
}

/**
 * Botón reutilizable para cerrar sesión.
 * Elimina el usuario actual del localStorage y redirige al login.
 * Compatible con usuarios de desarrollo y OAuth.
 */
export const Logout_Button: React.FC<LogoutButtonProps> = ({
  variant = "icon",
  className = "",
  title = "Cerrar sesión",
  "aria-label": ariaLabel = "Cerrar sesión",
}) => {
  const navigate = useNavigate();
  const { logout } = use_user_context();

  const handle_logout = () => {
    // Usar logout del contexto para limpiar todo correctamente
    logout();
    // Redirigir al login
    navigate("/login");
  };

  if (variant === "text") {
    return (
      <button
        type="button"
        onClick={handle_logout}
        className={`flex items-center gap-2 text-basmati-red hover:text-white hover:bg-basmati-red px-3 py-1 rounded border-2 border-transparent hover:border-basmati-black transition-all font-bold text-sm ${className}`}
        title={title}
        aria-label={ariaLabel}
      >
        <FontAwesomeIcon icon={faSignOutAlt} />
        <span>Cerrar sesión</span>
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={handle_logout}
      className={`hidden md:inline-flex p-2 text-gray-600 hover:text-basmati-red transition-colors focus:outline-none focus:ring-4 focus:ring-basmati-yellow focus:ring-offset-2 rounded ${className}`}
      aria-label={ariaLabel}
      title={title}
    >
      <FontAwesomeIcon icon={faSignOutAlt} />
    </button>
  );
};

