# Server-Side Files and H5 File Impact Summary

## Backend Files

### `server.ipynb` (Main Flask Server)
**Purpose**: Core simulation server that manages robots, plants, EM effects, and data collection.

**H5 File Impact**:
- **`/sequencer` dataset**: Stores plant positions (2x12 grid) - which plant is in which cell
- **`/sequencer_effects` dataset**: Stores EM effect UUIDs for each grid cell (2x12 grid)
- **`/sequencer_effects_properties/` group**: Stores detailed EM effect configurations (effect_type, frequency, voltage, etc.) keyed by UUID
- **`/plant_growth_data/` group**: Stores all plant growth observations with unified EM parameter schema:
  - `ticks` dataset: Tick numbers when observations occurred
  - `growth` dataset: Growth values (normalized)
  - `ac_frequency`, `ac_voltage`, `ac_phase` datasets: AC parameters (0 if not AC)
  - `dc_voltage`, `dc_current` datasets: DC parameters (0 if not DC)
  - `amf_frequency`, `amf_amplitude`, `amf_phase` datasets: AMF parameters (0 if not AMF)
  - `cmf_strength`, `cmf_direction` datasets: CMF parameters (0 if not CMF)
  - `em_effect` attribute: Effect type string

**Key Functions**:
- `simulation_tick()`: Updates robots, processes observations, records growth data to H5
- `update_robot()`: Moves robots, picks up/places plants, triggers observations
- `record_growth_data()`: Writes unified EM parameter data to H5
- `update_test_queue()`: Analyzes data, generates novel EM configs, populates queue
- Auto-assignment (every 25 ticks): Assigns queued configs to EM zones

### `run_server.py`
**Purpose**: Executes `server.ipynb` cells and starts Flask server.

**H5 File Impact**: None directly - just loads and executes the notebook.

### `h5_cli.py`
**Purpose**: Command-line tool for inspecting and managing H5 file contents.

**H5 File Impact**: Read-only inspection and manual clearing of growth data.

**Commands**:
- `inspect`: Shows H5 structure
- `growth`: Shows plant growth data with EM parameters
- `plants`: Shows plant distribution
- `effects`: Shows EM effect configurations
- `clear-growth`: Clears growth data (for testing)

### `diagnostic_test.py`
**Purpose**: Runs 1000-tick simulation test and traces robot/plant movements.

**H5 File Impact**: None - only reads via API, doesn't modify H5.

### `diagnose_queue.py`
**Purpose**: Analyzes test queue and parameter diversity.

**H5 File Impact**: None - only reads via API.

### `fast_diagnostic.py`
**Purpose**: Quick diagnostic for queue and parameter diversity at high speed.

**H5 File Impact**: None - only reads via API.

## Queue System Flow

1. **Data Collection**: `record_growth_data()` writes to H5 with unified EM parameters
2. **Analysis** (every 25 ticks): `update_test_queue()` reads H5 data and:
   - Finds high-variance configs → generates variants for std reduction
   - Finds parameter gaps → generates intermediate values
   - Generates exploration values between tested ranges
   - Generates novel parameter values
3. **Auto-Assignment** (every 25 ticks): Assigns queued configs to empty EM zones or replaces effects that have been tested >= 8 times
4. **Effect Application**: Plants in EM zones get exposed to the assigned effects
5. **Observation**: Robots observe plants and `record_growth_data()` writes new data to H5
6. **Cycle Repeats**: Queue updates with new data, generates more diverse configs

## Current Issue: Only 4 AC Frequency Values

**Root Cause**: Queue is generating configs (22+ configs with diverse AC frequencies like 44, 58, 72, 86 Hz) but they're not being assigned to EM zones because:
1. EM zones already have effects set
2. Auto-assignment only replaces effects that have been tested >= 8 times
3. With only 2 data points, no effects have reached MAX_RETESTS yet
4. Queue configs aren't being used until existing effects are "exhausted"

**Solution Implemented**:
- Queue now replaces effects even if not fully tested (when queue has high-priority configs)
- More aggressive gap detection (2% threshold, 1-5 intermediates per gap)
- Initial config generation when no data exists
- Speed limit increased to 1000x for fast debugging
