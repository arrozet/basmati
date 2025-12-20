import React from "react";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft } from "@fortawesome/free-solid-svg-icons";
import { Neo_Button } from "./Neo_Button";

interface Back_Button_Props {
  /** Ruta opcional a la que navegar. Si no se proporciona, usa navigate(-1). */
  to?: string;
  /** Clases de CSS adicionales. */
  className?: string;
}

/**
 * Componente de botón para volver atrás con estilo Neobrutalista.
 * Muestra únicamente una flecha hacia la izquierda.
 * 
 * @param to - Ruta opcional a la que navegar.
 * @param className - Clases de CSS adicionales.
 * @returns Componente React.
 */
export const Back_Button: React.FC<Back_Button_Props> = ({ to, className }) => {
  const navigate = useNavigate();

  /**
   * Maneja el clic en el botón navegando a la ruta proporcionada o un paso atrás.
   */
  const handle_click = () => {
    if (to) {
      navigate(to);
    } else {
      navigate(-1);
    }
  };

  return (
    <Neo_Button
      onClick={handle_click}
      variant="secondary"
      className={className}
      aria-label="Volver"
    >
      <FontAwesomeIcon icon={faArrowLeft} />
    </Neo_Button>
  );
};

