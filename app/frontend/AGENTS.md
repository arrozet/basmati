# Basmati Frontend Development Guide

## Project Overview
Basmati Frontend is the presentation layer for the calendar management application. This guide covers **frontend development** using a Clean Architecture approach to decouple UI from logic and infrastructure.

## Technology Stack
*   **Language:** TypeScript 5.0+
*   **Framework:** React 18+
*   **Build Tool:** Vite
*   **Styling:** Tailwind CSS (Neobrutalism Design System)
*   **Icons:** Font Awesome
*   **State Management:** React Context / Hooks (Clean Architecture adaptation)
*   **HTTP Client:** Axios
*   **Deployment:** Docker (Dev environment)
*   **Code Style:** `snake_case` for methods and variables (Strict Rule)
*   **Documentation:** English for code, Spanish for comments and docstrings

## Development Requirements

### General Rules
1.  **Everything must be dockerized** - The app runs inside a container.
2.  **Strict Clean Architecture** - No direct API calls from UI components.
3.  **Naming Convention:** Use `snake_case` for **ALL** variables, functions, and props.
    *   *Exception:* React Component filenames and Class names use `PascalCase` (e.g., `EventCard.tsx`), but their internal methods/props use `snake_case`.
4.  **All functions must have JSDoc docstrings with:**
    *   Parameter descriptions
    *   Return value descriptions
    *   **Comments in Spanish**, code in English.

**Example:**

```typescript
/**
 * Obtiene la lista de calendarios del usuario activo.
 * @param user_id - El ID del usuario actual.
 * @returns Una promesa con la lista de modelos de calendario.
 */
const get_user_calendars = async (user_id: string): Promise<Calendar_Model[]> => {
    // ... implementation
}
```

## Architecture Layers
The project follows a strict unidirectional data flow based on Clean Architecture:

**UI Layer** $\rightarrow$ **Application Layer** $\rightarrow$ **Domain Layer** $\leftarrow$ **Infrastructure Layer**

### 1. UI Layer (React + Vite)
Located in `frontend/presentation`. Responsible for rendering views and handling user interaction.
*   **Components:** Reusable UI elements (buttons, inputs, cards).
*   **Pages:** Full views (Dashboard, Calendar, Profile).
*   **Hooks:** Custom hooks that instantiate Use Cases. **UI never imports Repositories directly.**

### 2. Application Layer (Use Cases)
Located in `frontend/application`. Contains pure business logic.
*   Each Use Case is a function or class responsible for **one** specific action.
*   Orchestrates data flow between Domain and UI.

### 3. Domain Layer (Core)
Located in `frontend/domain`. The heart of the system.
*   **Entities/Models:** TypeScript interfaces defining data structures (e.g., `Event_Model`).
*   **Repository Interfaces:** Abstract definitions of how to fetch data (e.g., `Event_Repository_Interface`).
*   **No external dependencies** (no Axios, no React).

### 4. Infrastructure Layer (API Clients)
Located in `frontend/infrastructure`. Implements Domain interfaces.
*   **Repositories:** Concrete implementations using Axios (e.g., `Http_Event_Repository`).
*   **Mappers:** Converts API JSON to Domain Models and vice versa.

## Design System: Neobrutalism
The application uses a **Neobrutalist** style: high contrast, bold borders, hard shadows, and vibrant colors.

### Color Palette
Define these in `tailwind.config.js`.

| Color Role | Hex Code | Tailwind Name | Usage |
| :--- | :--- | :--- | :--- |
| **Primary** | `#EBBE4D` | `basmati-yellow` | Main buttons, highlights, active states. |
| **Background** | `#FFFAEB` | `basmati-bg` | Main page background (very light yellow/off-white). |
| **Surface** | `#FFFFFF` | `white` | Cards, modals, input backgrounds. |
| **Border/Text** | `#1A1A1A` | `basmati-black` | Text, 3px borders, hard shadows. |
| **Accent Blue** | `#5496FF` | `basmati-blue` | Links, info alerts, calendar items type A. |
| **Accent Red** | `#FF6B6B` | `basmati-red` | Delete actions, errors, urgent items. |
| **Accent Green** | `#4ECDC4` | `basmati-green` | Success states, save actions. |

### Styling Rules (Tailwind Classes)
*   **Borders:** `border-3 border-basmati-black` (custom width 3px).
*   **Shadows:** `shadow-[4px_4px_0px_0px_rgba(26,26,26,1)]` (Hard shadow, no blur).
*   **Typography:** Sans-serif, bold headings.
*   **Rounded:** Slightly rounded `rounded-md` or square `rounded-none`.

### UX & Accessibility Standards
*   **Responsive Design:** Mobile-first approach. The layout must adapt seamlessly to mobile, tablet, and desktop screens using Tailwind's responsive prefixes (`sm:`, `md:`, `lg:`).
*   **Accessibility (a11y):** Follow WCAG 2.1 AA standards.
    *   All interactive elements must have visible focus states (`focus:ring`).
    *   Images must have descriptive `alt` text.
    *   Semantic HTML tags (`<main>`, `<nav>`, `<article>`, `<button>`) are mandatory.
    *   Ensure sufficient color contrast between text and background.
*   **Performance:**
    *   Implement Lazy Loading for routes and heavy components.
    *   Optimize images (use WebP format where possible).
*   **User Experience:**
    *   **Feedback:** Show loading spinners or skeletons during async operations.
    *   **Notifications:** Provide clear success/error toast notifications for all server actions.
    *   **Error Handling:** Graceful degradation and user-friendly error messages.

### Content Guidelines
*   **Language:** Spanish.
*   **Capitalization:** Use **Sentence case** for all UI text (buttons, titles, labels).
    *   ✅ "Crear evento", "Ajustes de cuenta"
    *   ❌ "Crear Evento", "Ajustes De Cuenta" (No Title Case in Spanish)
*   **Orthography:** Strict adherence to Spanish grammar rules (proper accents, opening question/exclamation marks `¿` `¡`).

## Directory Structure

```text
frontend/
├── application/                # Layer 2: Use Cases
│   ├── event/
│   │   ├── create_event_use_case.ts
│   │   └── get_events_use_case.ts
│   └── calendar/
├── domain/                     # Layer 3: Models & Interfaces
│   ├── models/
│   │   ├── event_model.ts
│   │   └── calendar_model.ts
│   └── repositories/
│       ├── event_repository_interface.ts
│       └── calendar_repository_interface.ts
├── infrastructure/             # Layer 4: API Implementation
│   ├── api/
│   │   └── axios_client.ts
│   └── repositories/
│       ├── http_event_repository.ts
│       └── http_calendar_repository.ts
├── presentation/               # Layer 1: React UI
│   ├── components/             # Atomic components
│   │   └── ui/
│   │       ├── Neo_Button.tsx
│   │       └── Neo_Card.tsx
│   ├── hooks/                  # View logic / Controllers
│   │   └── use_calendar_events.ts
│   └── pages/
│       ├── Dashboard_Page.tsx
│       └── Login_Page.tsx
└── main.tsx
```

## Implementation Examples

### 1. Domain Layer (Model & Interface)

`frontend/domain/models/event_model.ts`
```typescript
export interface Event_Model {
    id: string;
    title: string;
    start_time: Date;
    description?: string;
}
```

`frontend/domain/repositories/event_repository_interface.ts`
```typescript
import { Event_Model } from "../models/event_model";

export interface Event_Repository_Interface {
    /**
     * Obtiene todos los eventos de un calendario.
     * @param calendar_id ID del calendario.
     */
    get_events(calendar_id: string): Promise<Event_Model[]>;
}
```

### 2. Infrastructure Layer (Implementation)

`frontend/infrastructure/repositories/http_event_repository.ts`
```typescript
import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";
import { Event_Model } from "../../domain/models/event_model";
import { api_client } from "../api/axios_client";

export class Http_Event_Repository implements Event_Repository_Interface {
    async get_events(calendar_id: string): Promise<Event_Model[]> {
        // Llamada al endpoint del backend
        const response = await api_client.get(`/v1/events/search?calendar_id=${calendar_id}`);
        
        // Mapeo de datos (snake_case del backend a nuestro modelo)
        return response.data.map((item: any) => ({
            id: item.id,
            title: item.title,
            start_time: new Date(item.start_time),
            description: item.description
        }));
    }
}
```

### 3. Application Layer (Use Case)

`frontend/application/event/get_events_use_case.ts`
```typescript
import { Event_Repository_Interface } from "../../domain/repositories/event_repository_interface";

export class Get_Events_Use_Case {
    private repository: Event_Repository_Interface;

    constructor(repository: Event_Repository_Interface) {
        this.repository = repository;
    }

    /**
     * Ejecuta la lógica de negocio para obtener eventos.
     */
    async execute(calendar_id: string) {
        if (!calendar_id) throw new Error("Calendar ID is required");
        return await this.repository.get_events(calendar_id);
    }
}
```

### 4. UI Layer (Hook & Component)

`frontend/presentation/hooks/use_events.ts`
```typescript
import { useState, useEffect } from "react";
import { Get_Events_Use_Case } from "../../application/event/get_events_use_case";
import { Http_Event_Repository } from "../../infrastructure/repositories/http_event_repository";

// Inyección de dependencias manual (Poor man's DI)
const repository = new Http_Event_Repository();
const get_events_use_case = new Get_Events_Use_Case(repository);

export const use_events = (calendar_id: string) => {
    const [events, set_events] = useState([]);
    const [loading, set_loading] = useState(true);

    useEffect(() => {
        const fetch_data = async () => {
            try {
                const result = await get_events_use_case.execute(calendar_id);
                set_events(result);
            } catch (error) {
                console.error(error);
            } finally {
                set_loading(false);
            }
        };
        fetch_data();
    }, [calendar_id]);

    return { events, loading };
};
```

## Docker Setup
The frontend is built using a simple Node container for development (no Nginx for now).

`Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json ./

RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose Vite default port
EXPOSE 5173

# Run dev server accessible from outside the container
CMD ["npm", "run", "dev", "--", "--host"]
```

`docker-compose.yml` entry:
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  ports:
    - "5173:5173"
  volumes:
    - ./frontend:/app
    - /app/node_modules
  environment:
    - VITE_API_GATEWAY_URL=http://localhost:8000
  depends_on:
    - api-gateway
```

## Environment Variables
Create a `.env` file in the root of the frontend project:
*   `VITE_API_GATEWAY_URL`: Base URL for the backend API Gateway (e.g., `http://localhost:8000`).

## Backend Integration Requirements
These are critical requirements for the Backend to support this Frontend architecture:

**1. CORS Configuration**
The Backend **API Gateway** (running on port 8000) must explicitly allow requests from the frontend origin (typically `http://localhost:5173`).
*   **Action:** Add `CORSMiddleware` in FastAPI with `allow_origins=["*"]` (or specific frontend URL) to prevent browser blocking.

**2. Mock Authentication (No OAuth yet)**
Since OAuth is not implemented yet, the frontend cannot send real tokens.
*   **Action:** Backend must seed a "Developer User" (e.g., ID: `user_dev_1`) on startup.
*   **Frontend Logic:** We will hardcode `CURRENT_USER_ID = "user_dev_1"` in our `UserContext` and send this ID in requests that require `user_id` or `creator_id`.

**3. Image Upload Proxy**
The frontend cannot upload images directly to cloud storage (S3/GCS) to avoid exposing API Keys.
*   **Action:** Backend (Integration Service) must provide an endpoint `POST /v1/files/upload` that accepts `multipart/form-data`.
*   **Flow:** Frontend sends file to Backend -> Backend uploads to Cloud -> Backend returns public URL -> Frontend saves URL in Event.

**4. Maps API Proxy**
To avoid exposing the Google Maps API Key in the client code (which is insecure), Geocoding must be handled server-side.
*   **Action:** Backend (Integration Service) must provide `GET /v1/integrations/maps/search?query=...`.
*   **Flow:** Frontend sends address string -> Backend queries Google Maps API -> Backend returns coordinates (Lat/Lng).

**5. Unified Search Strategy**
The UI design features a single Global Search bar.
*   **Action:** Frontend will likely need to perform parallel calls to `searchCalendars` and `searchEvents` use cases and merge results in the UI, as the backend microservices are decoupled.

**6. Versioning Strategy**

### API Versioning

To ensure backward compatibility for existing clients, the system uses a **directory-based versioning** approach.

1.  **Directory Structure:** Endpoints and logic are organized in versioned directories (e.g., `src/api/v1`, `src/api/v2`).
2.  **Immutability of V1:** The `v1` implementation is currently in use by active clients and must remain **intact**. Do not modify `v1` files to introduce breaking changes.
3.  **New Versions:** When breaking changes are required, create a `v2` directory. All dependencies (routers, schemas, controllers) must be versioned or isolated to ensure that `v1` continues to function exactly as before without regression.

### Database Versioning

The database must support schema evolution while maintaining access to older data structures.

1.  **Schema Versioning Pattern:** Use a `schema_version` field (integer) in documents within collections that undergo structural changes.
    *   *Example:* `{ "_id": "...", "schema_version": 2, "new_field": "value" }` vs `{ "_id": "...", "schema_version": 1, "old_field": "value" }`
2.  **Backward Compatibility:** The application domain layer must be capable of reading documents with older `schema_version` values.
3.  **Migration Strategy:** Implement **Lazy Migration** (Read-Repair). When a legacy document (`v1`) is read, convert it to the new model (`v2`) in memory, and save it back to the database in the new format upon the next write. Avoid downtime caused by massive batch updates.