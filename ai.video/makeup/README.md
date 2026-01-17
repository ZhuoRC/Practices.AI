# FaceFusion Video Face Swap

A web application for video face swapping using FaceFusion AI.

## Project Structure

```
makeup/
├── backend/
│   ├── venv/              # Python virtual environment
│   ├── app/
│   │   ├── main.py        # FastAPI entry point
│   │   ├── routers/
│   │   │   └── faceswap.py    # API routes
│   │   ├── services/
│   │   │   └── faceswap_service.py  # Face swap logic
│   │   ├── models/
│   │   │   └── schemas.py     # Pydantic models
│   │   └── utils/
│   │       └── storage.py     # JSON storage utility
│   ├── data/
│   │   ├── tasks.json     # Task records
│   │   ├── uploads/       # Uploaded files
│   │   └── outputs/       # Processed videos
│   ├── requirements.txt
│   └── run.py
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── VideoUploader.tsx
    │   │   ├── FaceSelector.tsx
    │   │   ├── ProcessingStatus.tsx
    │   │   └── VideoPreview.tsx
    │   ├── pages/
    │   │   └── Home.tsx
    │   ├── services/
    │   │   └── api.ts
    │   ├── App.tsx
    │   └── main.tsx
    ├── package.json
    └── vite.config.ts
```

## One-Click Start (Recommended)

Simply double-click `start.bat` to automatically:
- Check and create Python virtual environment
- Install/update all dependencies
- Start both backend and frontend services

The script will open two separate windows for backend and frontend.

## Quick Start

### Backend

```bash
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run the server
python run.py
```

The backend will start at http://localhost:8802

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will start at http://localhost:3802

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/upload | Upload video or face image |
| POST | /api/faceswap | Start face swap processing |
| GET | /api/tasks/{task_id} | Get task status |
| GET | /api/tasks | List all tasks |
| GET | /api/download/{task_id} | Download processed video |

## Usage

1. Start the backend server
2. Start the frontend development server
3. Open http://localhost:5173 in your browser
4. Upload a target video (the video you want to modify)
5. Upload a source face image (the face you want to use)
6. Click "Start Face Swap" to begin processing
7. Wait for processing to complete
8. Download the result video

## Technology Stack

- **Backend**: FastAPI, Python 3.x
- **Frontend**: React, TypeScript, Vite
- **AI Model**: FaceFusion (facefusionlib)
- **Data Storage**: JSON files

## Notes

- The backend runs in a Python virtual environment (`venv/`)
- AI models are downloaded automatically on first use
- Processing time depends on video length and hardware capabilities
