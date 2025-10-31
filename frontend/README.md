# SCIMS Frontend

React 18 + TypeScript frontend for the Star Citizen Inventory Management System, built with Vite.

## Technology Stack

- **Framework:** React 18.3+
- **Language:** TypeScript 5.5+
- **Build Tool:** Vite 5.4+
- **Package Manager:** pnpm (workspace support)
- **UI Framework:** (Blueprint.js - to be added)
- **State Management:** (React Query - to be added)

## Prerequisites

- Node.js 20+ 
- pnpm 9+ (or npm/yarn)
- Git

## Development Setup

### Using Docker (Recommended)

The frontend runs automatically when you start the Docker Compose stack:

```bash
docker compose up frontend
```

The frontend will be available at `http://localhost` (via Nginx) or `http://localhost:5173` (direct Vite dev server) with hot-reload enabled.

### Local Setup (Without Docker)

1. **Install pnpm (if not already installed):**
   ```bash
   npm install -g pnpm
   # Or using corepack (Node.js 16.13+)
   corepack enable
   corepack prepare pnpm@latest --activate
   ```

2. **Install dependencies:**
   ```bash
   pnpm install
   ```

3. **Set up environment variables:**
   ```bash
   cp ../.env.example .env.local
   # Edit .env.local with your API URLs
   ```

4. **Start the development server:**
   ```bash
   pnpm dev
   ```

   The app will be available at `http://localhost:5173`

## Environment Variables

Frontend environment variables must be prefixed with `VITE_` to be accessible in the code:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

Access in code:
```typescript
import.meta.env.VITE_API_URL
```

See `src/vite-env.d.ts` for TypeScript type definitions.

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable React components
│   ├── pages/            # Page-level components
│   ├── services/         # API service functions
│   ├── hooks/            # Custom React hooks
│   ├── types/            # TypeScript type definitions
│   ├── App.tsx           # Root component
│   ├── main.tsx          # Application entry point
│   └── vite-env.d.ts     # Vite environment variable types
├── public/               # Static assets
├── index.html            # HTML template
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── tsconfig.node.json    # TypeScript config for Vite
├── vite.config.ts        # Vite configuration
└── Dockerfile            # Docker build configuration
```

## Available Scripts

```bash
# Start development server
pnpm dev

# Build for production
pnpm build

# Preview production build locally
pnpm preview

# Run TypeScript type checking
pnpm type-check  # (if added to scripts)

# Run linter (when configured)
pnpm lint
```

## Development

### Hot Module Replacement

Vite provides instant HMR. Changes to components will update in the browser without a full page reload.

### TypeScript

The project uses strict TypeScript configuration. Type definitions are available for:
- React components
- Environment variables (`import.meta.env`)
- API responses (to be added as APIs are implemented)

### Adding New Components

1. Create component file in `src/components/`
2. Use TypeScript for props: `interface ComponentProps { ... }`
3. Export as default or named export
4. Import where needed

Example:
```typescript
// src/components/ItemCard.tsx
interface ItemCardProps {
  name: string
  quantity: number
}

export default function ItemCard({ name, quantity }: ItemCardProps) {
  return (
    <div>
      <h3>{name}</h3>
      <p>Quantity: {quantity}</p>
    </div>
  )
}
```

### API Integration

API calls should be made through service functions in `src/services/`:

```typescript
// src/services/api.ts
const API_URL = import.meta.env.VITE_API_URL

export async function getItems() {
  const response = await fetch(`${API_URL}/items`)
  return response.json()
}
```

### Environment Variable Types

Type definitions for environment variables are in `src/vite-env.d.ts`. Add new variables there:

```typescript
interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_WS_URL: string
  // Add new variables here
}
```

## Building for Production

```bash
# Build the application
pnpm build

# Output will be in dist/
# This can be served by Nginx or any static file server
```

The production build:
- Minifies and optimizes code
- Tree-shakes unused code
- Generates source maps (disabled in current config)
- Creates hashed filenames for caching

## Docker

The frontend has multi-stage Docker builds:

- **Development:** Runs Vite dev server with hot-reload
- **Production:** Builds static files and serves with Nginx

See `Dockerfile` for details.

## Troubleshooting

### Module Not Found Errors

- Run `pnpm install` to ensure all dependencies are installed
- Check `node_modules` exists
- Verify import paths are correct

### TypeScript Errors

- Check `tsconfig.json` configuration
- Ensure type definitions are properly imported
- Run `tsc --noEmit` to check types without building

### Environment Variables Not Working

- Variables must be prefixed with `VITE_`
- Restart dev server after changing `.env` files
- Check `vite-env.d.ts` has the variable typed

### Build Failures

- Clear `dist/` and `node_modules/.vite` directories
- Run `pnpm install` to ensure dependencies are up to date
- Check for TypeScript errors: `tsc --noEmit`

## Next Steps

- [ ] Add Blueprint.js UI components
- [ ] Set up React Query for state management
- [ ] Create authentication context
- [ ] Implement routing (React Router)
- [ ] Add API service layer
- [ ] Create basic page layouts

See the [Implementation Roadmap](../planning/implementation-roadmap.md) for detailed development tasks.

