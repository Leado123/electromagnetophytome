#!/usr/bin/env node
/**
 * Development mode: Run Flask backend and Astro dev server concurrently
 */
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PROJECT_ROOT = join(__dirname, '..');
const BACKEND_DIR = join(PROJECT_ROOT, 'backend');

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
      proc.kill('SIGTERM');
    } catch (e) {
      // Ignore errors
    }
  });
  process.exit(0);
}

process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);

// Start Flask backend server
log('Starting Flask backend server on http://localhost:5000', colors.green);
const flaskProcess = spawn('uv', ['run', 'python', 'run_server.py'], {
  cwd: BACKEND_DIR,
  stdio: 'inherit',
  shell: false,
});
processes.push(flaskProcess);

flaskProcess.on('error', (err) => {
  log(`Error starting Flask server: ${err.message}`, colors.yellow);
  log('Make sure uv is installed and backend dependencies are set up', colors.yellow);
  process.exit(1);
});

// Wait a moment for Flask to start, then start Astro
setTimeout(() => {
  // Start Astro dev server
  log('Starting Astro dev server on http://localhost:4321', colors.green);
  const astroProcess = spawn('bun', ['run', 'dev'], {
    cwd: PROJECT_ROOT,
    stdio: 'inherit',
    shell: false,
  });
  processes.push(astroProcess);

  astroProcess.on('error', (err) => {
    log(`Error starting Astro server: ${err.message}`, colors.yellow);
    process.exit(1);
  });

  log('\nBoth servers are running!', colors.blue);
  log('Flask API: http://localhost:5000', colors.green);
  log('Astro Frontend: http://localhost:4321', colors.green);
  log('\nPress Ctrl+C to stop both servers\n', colors.yellow);
}, 2000);
