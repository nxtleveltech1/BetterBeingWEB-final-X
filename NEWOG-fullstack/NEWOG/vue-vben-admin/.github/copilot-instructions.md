# Copilot Instructions for AI Coding Agents

## Project Overview
- **Vue Vben Admin** is a Vue 3 + Vite + TypeScript admin dashboard template. It is designed for rapid development of middle and back-end web applications.
- The codebase is modular, with clear separation between UI components, routing, state management, and API integration.

## Architecture & Key Directories
- `src/` — Main source code. Contains:
  - `components/` — Reusable UI components.
  - `pages/` — Route-based views.
  - `hooks/`, `lib/`, `contexts/` — Custom logic, utilities, and state management.
  - `assets/`, `styles/` — Static assets and global styles.
- Uses **dynamic route-based permission generation** and built-in internationalization.
- Follows a feature-based structure for scalability.

## Developer Workflows
- **Install dependencies:**
  ```bash
  npm i -g corepack
  pnpm install
  ```
- **Start development server:**
  ```bash
  pnpm dev
  ```
- **Build for production:**
  ```bash
  pnpm build
  ```
- **Testing:**
  - Unit tests: Vitest
  - Run tests: `pnpm test`
- **Commit conventions:**
  - Use [Conventional Commits](https://github.com/vuejs/vue/blob/dev/.github/COMMIT_CONVENTION.md) (e.g., `feat:`, `fix:`, `test:`)

## Patterns & Conventions
- **TypeScript-first:** All new code should use TypeScript.
- **Component registration:** Prefer local registration for page-specific components, global for shared UI.
- **State management:** Use provided context/hooks patterns in `contexts/` and `hooks/`.
- **API integration:** Centralize API calls in `services/`.
- **Internationalization:** Use built-in i18n utilities for all user-facing text.
- **Permissions:** Route permissions are managed dynamically; see routing logic in `src/pages/` and related middleware.

## Integration Points
- **External dependencies:**
  - Vue 3, Vite, TypeScript, pnpm, Vitest
  - SonarCloud, CodeQL, GitHub Actions for CI/CD
- **CI/CD:**
  - Build, test, and deploy workflows defined in `.github/workflows/`

## Examples
- To add a new page: create a file in `src/pages/`, register the route, and ensure permissions are set.
- To add a new API service: add to `src/services/`, use hooks/context for state.

---

For further details, see the [README.md](../README.md) and [Documentation](https://doc.vben.pro/).
