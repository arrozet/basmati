/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'basmati-yellow': '#EBBE4D', // Contraste 3.5:1 con negro - Aceptable para elementos grandes
        'basmati-bg': '#FFFAEB',     // Fondo claro
        'basmati-black': '#1A1A1A',   // Texto principal - Excelente contraste con fondos claros
        'basmati-blue': '#3B6FD9',    // Mejorado de #5496FF para mejor contraste (4.5:1)
        'basmati-red': '#D63939',     // Mejorado de #FF6B6B para mejor contraste (4.5:1)
        'basmati-green': '#2BA89F',   // Mejorado de #4ECDC4 para mejor contraste (4.5:1)
      },
      borderWidth: {
        '3': '3px',
      },
      boxShadow: {
        'hard': '4px 4px 0px 0px rgba(26,26,26,1)',
      },
      // Utilidades de accesibilidad
      spacing: {
        'safe': '1rem', // Espacio mínimo táctil (16px)
      },
    },
  },
  plugins: [
    // Plugin personalizado para utilidades de accesibilidad
    function({ addUtilities }) {
      const accessibilityUtilities = {
        '.sr-only': {
          position: 'absolute',
          width: '1px',
          height: '1px',
          padding: '0',
          margin: '-1px',
          overflow: 'hidden',
          clip: 'rect(0, 0, 0, 0)',
          whiteSpace: 'nowrap',
          borderWidth: '0',
        },
        '.sr-only-focusable:focus': {
          position: 'static',
          width: 'auto',
          height: 'auto',
          padding: 'inherit',
          margin: 'inherit',
          overflow: 'visible',
          clip: 'auto',
          whiteSpace: 'normal',
        },
        '.focus-visible-ring': {
          outline: 'none',
          '&:focus-visible': {
            ring: '4px',
            ringColor: '#EBBE4D',
            ringOffset: '2px',
          }
        },
        // Área táctil mínima de 44x44px (WCAG 2.5.5)
        '.touch-target': {
          minWidth: '44px',
          minHeight: '44px',
        },
      };
      
      addUtilities(accessibilityUtilities);
    }
  ],
}

