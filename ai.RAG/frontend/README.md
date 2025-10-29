# RAG System Frontend

Frontend interface for the RAG system built with React + TypeScript + Vite.

## Quick Start

### Install Dependencies

```bash
npm install
```

### Development

```bash
npm run dev
```

Visit http://localhost:5173

### Build

```bash
npm run build
```

Build output will be in the `dist/` directory.

### Preview

```bash
npm run preview
```

## Main Features

- 📄 PDF document upload (drag-and-drop support)
- 📋 Document list management
- 💬 Intelligent Q&A interface
- 🔍 Answer source tracing

## Tech Stack

- React 18
- TypeScript
- Vite
- Ant Design 5
- Axios

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── FileUpload.tsx
│   │   ├── DocumentList.tsx
│   │   └── ChatInterface.tsx
│   ├── services/         # API services
│   │   └── api.ts
│   ├── App.tsx           # Main component
│   ├── App.css
│   ├── main.tsx          # Entry file
│   └── index.css
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```
