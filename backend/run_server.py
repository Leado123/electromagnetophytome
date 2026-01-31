#!/usr/bin/env python3
"""
Run the Flask server from server.ipynb notebook.
This script loads and executes the notebook cells to start the Flask server.
"""
import sys
from pathlib import Path
import nbformat

# Get the backend directory
backend_dir = Path(__file__).parent
notebook_path = backend_dir / "server.ipynb"

if not notebook_path.exists():
    print(f"Error: Notebook not found at {notebook_path}")
    sys.exit(1)

# Load and execute the notebook
print(f"Loading notebook: {notebook_path}")
nb = nbformat.read(str(notebook_path), as_version=4)

# Execute all code cells (except the last one which has __name__ check)
# Set up namespace with proper __name__ and __file__ for Flask
namespace = {
    '__name__': '__main__',
    '__file__': str(notebook_path),
}
for i, cell in enumerate(nb.cells[:-1]):  # Skip last cell
    if cell.cell_type == "code":
        print(f"Executing cell {i+1}...")
        try:
            exec(cell.source, namespace)
        except Exception as e:
            print(f"Error in cell {i+1}: {e}")
            import traceback
            traceback.print_exc()
            # Stop execution on error - cells depend on each other
            print(f"\nFailed to execute notebook. Please check the error above.")
            sys.exit(1)

# Check if Flask app was created
if 'app' not in namespace:
    print("Error: Flask app not found. Make sure server.ipynb is properly configured.")
    sys.exit(1)

# Start the Flask server
print("\n" + "="*60)
print("Starting Flask server on http://localhost:5000")
print("API endpoints:")
print("  POST /api/plants - Create a new plant")
print("  GET /api/plants - List all plants")
print("  GET /api/sequencer - Get sequencer grid")
print("  PUT /api/sequencer - Update sequencer position")
print("="*60 + "\n")

namespace['app'].run(host='0.0.0.0', port=5000, debug=True)

