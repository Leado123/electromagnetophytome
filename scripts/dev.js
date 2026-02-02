#!/usr/bin/env node
/**
 * Development mode: Run Flask backend and Astro dev server concurrently
 */
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PROJECT_ROOT = join(__dirname, '..');
const BACKEND_DIR = join(PROJECT_ROOT, 'backend');
const isWin = process.platform === 'win32';

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  blue: '\x1b[34m',
  yellow: '\x1b[33m',
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

// Cleanup function
let processes = [];
function cleanup() {
  log('\nShutting down servers...', colors.yellow);
  processes.forEach(proc => {
    try {
      const signal = isWin ? 'SIGINT' : 'SIGTERM';
      proc.kill(signal);
    } catch (e) {
      // Ignore errors
    }
  });
  process.exit(0);
}

process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);

function startBackend() {
  log('Starting Flask backend server on http://localhost:5000', colors.green);

  // Helper to spawn a process and track it
  const spawnTracked = (cmd, args, options) => {
    const p = spawn(cmd, args, options);
    processes.push(p);
    return p;
  };

  // Try using `uv` first (cross-platform if installed)
  let backend = spawnTracked('uv', ['run', 'python', 'run_server.py'], {
    cwd: BACKEND_DIR,
    stdio: 'inherit',
    shell: false,
  });

  backend.on('error', (err) => {
    // Fallback to venv python or system python if uv is not available
    if (err.code === 'ENOENT') {
      log('`uv` not found, falling back to virtualenv/system Python...', colors.yellow);
      const venvPython = isWin
        ? join(BACKEND_DIR, '.venv', 'Scripts', 'python.exe')
        : join(BACKEND_DIR, '.venv', 'bin', 'python');

      if (fs.existsSync(venvPython)) {
        backend = spawnTracked(venvPython, ['run_server.py'], {
          cwd: BACKEND_DIR,
          stdio: 'inherit',
          shell: false,
        });
      } else {
        // Use system python as last resort
        backend = spawnTracked(isWin ? 'python' : 'python3', ['run_server.py'], {
          cwd: BACKEND_DIR,
          stdio: 'inherit',
          shell: false,
        });
      }

      backend.on('error', (e2) => {
        log(`Error starting Flask server: ${e2.message}`, colors.yellow);
        process.exit(1);
      });
    } else {
      log(`Error starting Flask server: ${err.message}`, colors.yellow);
      process.exit(1);
    }
  });

  return backend;
}

const flaskProcess = startBackend();

// Wait a moment for Flask to start, then start Astro
setTimeout(() => {
  // Start Astro dev server
  log('Starting Astro dev server on http://localhost:4321', colors.green);

  const spawnTracked = (cmd, args, options) => {
    const p = spawn(cmd, args, options);
    processes.push(p);
    return p;
  };

  let astroProcess = spawnTracked('bun', ['run', 'dev'], {
    cwd: PROJECT_ROOT,
    stdio: 'inherit',
    shell: false,
  });

  astroProcess.on('error', (err) => {
    if (err.code === 'ENOENT') {
      log('`bun` not found, falling back to npm...', colors.yellow);
      astroProcess = spawnTracked(isWin ? 'npm.cmd' : 'npm', ['run', 'dev'], {
        cwd: PROJECT_ROOT,
        stdio: 'inherit',
        shell: false,
      });
      astroProcess.on('error', (e2) => {
        log(`Error starting Astro server: ${e2.message}`, colors.yellow);
        process.exit(1);
      });
    } else {
      log(`Error starting Astro server: ${err.message}`, colors.yellow);
      process.exit(1);
    }
  });

  log('\nBoth servers are running!', colors.blue);
  log('Flask API: http://localhost:5000', colors.green);
  log('Astro Frontend: http://localhost:4321', colors.green);
  log('\nPress Ctrl+C to stop both servers\n', colors.yellow);
}, 2000);
