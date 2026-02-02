# Electromagnetophytome

A plant sequencer application for studying electromagnetic field effects on plant growth. Features a Flask backend with HDF5 data storage and an Astro frontend with real-time simulation visualization.

## Project Structure

```
electromagnetophytome/
├── src/                          # Frontend (Astro)
│   ├── components/               # Reusable UI components
│   │   ├── common/               # Shared components (Button, Icon, Header)
│   │   ├── sequencer/            # Sequencer page components
│   │   │   ├── SimulationControls.astro
│   │   │   ├── ResourceSidebar.astro
│   │   │   ├── SequencerGrid.astro
│   │   │   └── StatusSidebar.astro
│   │   └── graph/                # Graph page components
│   │       ├── ChartCard.astro
│   │       └── StatsSidebar.astro
│   ├── lib/                      # Frontend utilities
│   │   └── sequencer/            # Sequencer logic
│   │       ├── config.ts         # Constants and configuration
│   │       └── api.ts            # API client functions
│   ├── pages/                    # Page routes
│   │   ├── index.astro
│   │   ├── sequencer.astro
│   │   └── graph.astro
│   └── styles/                   # Global styles
│       └── global.css
├── backend/                      # Backend (Flask + Jupyter)
│   ├── server.ipynb              # Main server notebook
│   ├── run_server.py             # Server entry point
│   ├── lib/                      # Backend modules
│   │   ├── data/                 # Data layer
│   │   │   ├── init.ipynb        # HDF5 schema initialization
│   │   │   └── h5_operations.ipynb # HDF5 CRUD operations
│   │   ├── api/                  # API route modules
│   │   │   ├── plants.ipynb      # Plant endpoints
│   │   │   ├── effects.ipynb     # Effect endpoints
│   │   │   └── simulation.ipynb  # Simulation endpoints
│   │   └── simulation/           # Simulation engine
│   │       └── engine.ipynb      # Core simulation logic
│   └── pyproject.toml            # Python dependencies
├── data/                         # HDF5 data storage
│   └── data.h5                   # Main data file
├── db/                           # Database utilities
├── public/                       # Static assets
└── scripts/                      # Build/dev scripts
```

## Key Technologies

- **Frontend**: Astro 5.x, Tailwind CSS, Chart.js
- **Backend**: Flask, HDF5 (h5py), Jupyter Notebooks
- **Styling**: Tailwind CSS (utility-first, no loose CSS)

## Prerequisites

- **Python**: Python 3.13+ with [uv](https://github.com/astral-sh/uv) package manager
- **Node.js**: Node.js with [bun](https://bun.sh) package manager

## Setup

### Backend Setup

```bash
cd backend
uv sync
```

### Frontend Setup

```bash
bun install
```

## Running the Application

### Development Mode

Run both Flask backend and Astro dev server concurrently:

```bash
# Using npm/bun scripts
bun run dev:all

# Or directly
./scripts/dev.sh
```

This will start:
- Flask API server on `http://localhost:5000`
- Astro dev server on `http://localhost:4321`

### Production Build

Build and run in production mode:

```bash
# Using npm/bun scripts
bun run build:all


# Or directly
./scripts/build.sh
```

This will:
1. Build the Astro application
2. Start Flask API server on `http://localhost:5000`
3. Start Astro preview server on `http://localhost:4321`

### Running Servers Individually

You can also run servers separately:

```bash
# Backend only
bun run start:backend

# Frontend only
bun run start:frontend
```

## Project Structure

```
.
├── backend/
│   ├── lib/
│   │   └── data/
│   │       └── init.ipynb          # Data initialization notebook
│   ├── server.ipynb                 # Flask server notebook
│   └── run_server.py                # Script to run server from notebook
├── scripts/
│   ├── dev.sh                       # Development startup script
│   └── build.sh                     # Production build script
├── src/
│   └── pages/
│       └── sequencer.astro          # Main sequencer UI
└── data/
    └── data.h5                      # HDF5 data file
```

## API Endpoints

- `POST /api/plants` - Create a new plant
- `GET /api/plants` - List all plants
- `GET /api/sequencer` - Get current sequencer grid state
- `PUT /api/sequencer` - Update sequencer position (body: `{row, col, plant_id}`)

## Development

All Python code is kept in Jupyter notebooks for easy experimentation and iteration. The Flask server loads functions from `init.ipynb` and runs from `server.ipynb`.
