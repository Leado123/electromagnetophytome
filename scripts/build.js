#!/usr/bin/env node
/**
 * Build mode: Build Astro and start Flask server with production Astro server
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

async function main() {
  // Build Astro
  log('Building Astro application...', colors.green);
  const buildProcess = spawn('bun', ['run', 'build'], {
    cwd: PROJECT_ROOT,
    stdio: 'inherit',
    shell: false,
  });

  await new Promise((resolve, reject) => {
    buildProcess.on('exit', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Build failed with code ${code}`));
      }
    });
    buildProcess.on('error', reject);
  });

  // Start Flask backend server
  log('\nStarting Flask backend server on http://localhost:5000', colors.green);
  const flaskProcess = spawn('uv', ['run', 'python', 'run_server.py'], {
    cwd: BACKEND_DIR,
    stdio: 'inherit',
    shell: false,
  });
  processes.push(flaskProcess);

  flaskProcess.on('error', (err) => {
    log(`Error starting Flask server: ${err.message}`, colors.yellow);
    log('Make sure uv is installed and backend dependencies are set up', colors.yellow);
  });

  // Wait a moment for Flask to start
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Start Astro preview server
  log('Starting Astro preview server on http://localhost:4321', colors.green);
  const astroProcess = spawn('bun', ['run', 'preview'], {
    cwd: PROJECT_ROOT,
    stdio: 'inherit',
    shell: false,
  });
  processes.push(astroProcess);

  astroProcess.on('error', (err) => {
    log(`Error starting Astro server: ${err.message}`, colors.yellow);
  });

  log('\nBoth servers are running!', colors.blue);
  log('Flask API: http://localhost:5000', colors.green);
  log('Astro Frontend: http://localhost:4321', colors.green);
  log('\nPress Ctrl+C to stop both servers\n', colors.yellow);
}

main().catch((err) => {
  log(`Error: ${err.message}`, colors.yellow);
  cleanup();
});

