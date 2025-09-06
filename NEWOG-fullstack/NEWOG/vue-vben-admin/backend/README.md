# Better Being Backend for Production

## 1. Tech Stack
- Node.js (TypeScript)
- Express (REST API framework)
- Prisma ORM (Type-safe DB access)
- Neon (Postgres, managed, scalable — https://neon.tech)
- JWT auth
- API-first, production-ready config

## 2. Folder Structure
backend/
  src/
    controllers/
    middlewares/
    models/
    routes/
    services/
    utils/
    prisma/
    app.ts
    server.ts
  .env
  package.json
  tsconfig.json
  prisma/schema.prisma
  README.md

## 3. Core Endpoints
- POST   /auth/login       # Login, returns JWT
- GET    /user/info        # returns current user profile for session (needs auth)
- Users CRUD: /users
- Content CRUD: /content
- Feedback: /feedback
- Analytics: /analytics (stubbed now)

## 4. Neon Database Integration
- Uses Prisma for full type-safety, migrations, and connection pooling
- .env example: 
  DATABASE_URL="postgresql://<user>:<password>@ep-xxx-db.eu-central-1.aws.neon.tech/neondb?sslmode=require"

## 5. Local Dev
- .env points to local Neon dev DB (or uses Neon proxy for local port)
- All migrations/raw SQL handled via prisma CLI

## 6. Deployment
- Ready to deploy to serverless/server: just set DATABASE_URL for Neon prod

## 7. Dev Scripts
- Install:   pnpm i (from ./backend)
- Dev:      pnpm dev (uses nodemon)
- Build:    pnpm build
- Test:     pnpm test

---

## Step 1 (Automated):
- Scaffold backend Node application in backend/
- Add Prisma, Express, Typescript setup
- Seed basic Neon Postgres schema (users, content, feedback, analytics)
- Write initialization scripts and starter API endpoints
- Document how to connect Neon to the local dev port

## Step 2 (Manual, you):
- Sign up at https://neon.tech, create a project+database
- Copy the connection string to backend/.env as DATABASE_URL
- Run: pnpm prisma migrate dev --name init

---
