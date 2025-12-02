# Documentación de la Capa de Presentación - Frontend Basmati

## Introducción

La capa de presentación del frontend de **Basmati** implementa una interfaz de usuario moderna siguiendo el estilo **Neobrutalism** (colores vibrantes, bordes gruesos y sombras duras). Desarrollado con **React + TypeScript** y **Tailwind CSS**, cumple con los estándares **WCAG 2.1 AA** de accesibilidad.

---

## Arquitectura y Componentes

### Estructura
```
src/presentation/
├── components/
│   ├── ui/           # Componentes reutilizables (Button, Card, Input, Modal)
│   └── layout/       # Estructura (Navbar, Sidebar, MainLayout)
├── pages/            # Páginas principales (Dashboard, Login, Settings, etc.)
├── hooks/            # Lógica reutilizable
└── router/           # Configuración de rutas
```

### Sistema de Diseño

**Paleta de colores** (cumple contraste WCAG AA):
- Amarillo primario `#EBBE4D` - Botones principales
- Negro `#1A1A1A` - Texto y bordes
- Azul `#5496FF`, Rojo `#D63939`, Verde `#2BA9F` - Estados y acciones

**Características visuales**:
- Bordes de 3px en negro
- Sombras duras (4px 4px 0px)
- Animaciones de "hundimiento" al hacer clic
- Tipografía en negrita para jerarquía

**[ESPACIO PARA CAPTURA: Interfaz principal mostrando diseño Neobrutalism]**

---

## Componentes UI Principales

### Neo_Button
Botón con 4 variantes (`primary`, `secondary`, `danger`, `success`), estados de loading, accesibilidad completa con `aria-busy`, focus visible y área táctil mínima de 44x44px.

### Neo_Input
Campo de entrada con labels asociados automáticamente, validación visual, mensajes de error con `role="alert"`, helper text y soporte para campos requeridos.

### Neo_Modal
Modal accesible con focus trap, navegación por teclado (ESC para cerrar, TAB para navegar), overlay bloqueante y atributos ARIA completos (`role="dialog"`, `aria-modal`).

### Neo_Card
Tarjeta con borde y sombra características, título opcional y renderizado semántico flexible (`<div>` o `<section>`).

---

## Layout y Navegación

### Navbar
Barra superior fija con logo, búsqueda (oculta en móvil), menú hamburguesa para móvil y botón de perfil. Usa `<nav>` semántico con `aria-label="Navegación principal"`.

### Sidebar
Panel lateral con botones de creación rápida, listado de calendarios con indicadores de color y comportamiento responsive (fijo en desktop, overlay en móvil). Navegación completa por teclado.

### MainLayout
Contenedor que compone Navbar + Sidebar + contenido principal, gestionando estados de apertura/cierre del menú móvil.

**[ESPACIO PARA CAPTURA: Vista completa del layout en desktop]**

---

## Páginas Funcionales

### Dashboard_Page
Vista principal con calendario en 4 formatos: **Año** (grid de 12 meses), **Mes** (calendario clásico), **Semana** (7 columnas) y **Día** (lista detallada). Incluye navegación por flechas, gestión de eventos (crear, editar, eliminar) con modales de confirmación y navegación completa por teclado usando `role="grid"` y `role="gridcell"`.

**[ESPACIO PARA CAPTURA: Vista de mes con eventos]**

### Create/Edit Event Pages
Formularios accesibles con `<fieldset>` y `<legend>` para agrupar campos relacionados, validación en tiempo real, mensajes de error con `role="alert"` y funcionalidad de eliminación de eventos con modal de confirmación.

### Login_Page
Formulario de autenticación con labels asociados, validación de campos y estado de loading en el botón de envío.

### Settings_Page
Configuración de perfil, notificaciones y preferencias con formularios estructurados semánticamente.

---

## Accesibilidad y Cumplimiento WCAG 2.1 AA

La aplicación implementa accesibilidad completa siguiendo los estándares WCAG 2.1 nivel AA:

### Implementación
- **HTML semántico**: Uso de landmarks (`<nav>`, `<main>`, `<aside>`), jerarquía de encabezados correcta (h1→h2→h3)
- **Contraste de color**: Ratio mínimo 4.5:1 en textos, validado con herramientas
- **Navegación por teclado**: Todos los elementos interactivos accesibles con TAB, ENTER, SPACE y ESC
- **Focus visible**: Anillo amarillo de 4px con offset de 2px en todos los elementos interactivos
- **ARIA apropiado**: `aria-label`, `aria-expanded`, `aria-pressed`, `aria-describedby`, `role="alert"`
- **Mensajes de estado**: Uso de `aria-live` y `role="alert"` para feedback dinámico
- **Área táctil**: Mínimo 44x44px en todos los botones (WCAG 2.5.5)

### Compatibilidad
Compatible con lectores de pantalla modernos (NVDA, JAWS, VoiceOver).

**[ESPACIO PARA CAPTURA: Resultados de análisis WAVE sin errores]**

---

## Diseño Responsivo

La aplicación se adapta a tres breakpoints principales:

| Dispositivo | Resolución | Adaptaciones |
|-------------|------------|--------------|
| **Móvil** | < 768px | Sidebar en overlay, menú hamburguesa, búsqueda en página dedicada |
| **Tablet** | 768-1024px | Sidebar visible, búsqueda expandida |
| **Desktop** | > 1024px | Layout completo, grid de calendario expandido |

**Optimizaciones**: Lazy loading de componentes, CSS optimizado con Tailwind, soporte para `prefers-reduced-motion`.

**[ESPACIO PARA CAPTURA: Vista móvil de la aplicación]**

---

## Conclusión

El frontend de Basmati combina un diseño visual distintivo (Neobrutalism) con accesibilidad completa (WCAG 2.1 AA), arquitectura escalable basada en componentes reutilizables y diseño responsive adaptado a todos los dispositivos. Implementa navegación por teclado completa, feedback visual claro en todas las interacciones y compatibilidad con tecnologías asistivas.

**Tecnologías**: React 18 + TypeScript + Tailwind CSS  
**Cumplimiento**: WCAG 2.1 AA ✅
