#!/usr/bin/env python3
"""
Fast diagnostic - runs simulation at ultra-high speed and checks queue/parameter diversity
"""
import requests
import time
import json

API_BASE = "http://localhost:5000/api"

def check_server():
    """Check if server is running"""
    try:
        r = requests.get(f"{API_BASE}/simulation/state", timeout=2)
        return r.json() if r.ok else None
    except:
        return None

def main():
    print("=" * 80)
    print("FAST QUEUE DIAGNOSTIC")
    print("=" * 80)
    
    # Check server
    state = check_server()
    if not state:
        print("ERROR: Server not running at localhost:5000")
        print("Please start the server first!")
        return
    
    print(f"Current state: Tick={state.get('tick')} Running={state.get('running')} Speed={state.get('speed')}")
    
    # Stop simulation
    try:
        requests.post(f"{API_BASE}/simulation/pause", timeout=3)
    except Exception:
        pass
    time.sleep(0.5)
    
    # Check current parameter diversity
    print("\n[1] Checking current parameter diversity...")
    try:
        r = requests.get(f"{API_BASE}/plant-growth/unified", timeout=5)
        if r.ok:
            data = r.json()
            points = data.get('data_points', [])
            
            # Analyze AC frequency values
            ac_freqs = sorted(set([p.get('ac_frequency', 0) for p in points if p.get('ac_frequency', 0) > 0]))
            dc_volts = sorted(set([p.get('dc_voltage', 0) for p in points if p.get('dc_voltage', 0) > 0]))
            
            print(f"  Total data points: {len(points)}")
            print(f"  AC frequencies tested: {len(ac_freqs)} values - {ac_freqs}")
            print(f"  DC voltages tested: {len(dc_volts)} values - {dc_volts}")
            
            if len(ac_freqs) <= 4:
                print(f"  ⚠️  WARNING: Only {len(ac_freqs)} AC frequency values!")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Check queue
    print("\n[2] Checking test queue...")
    try:
        r = requests.get(f"{API_BASE}/test-queue", timeout=5)
        if r.ok:
            queue_data = r.json()
            queue_size = queue_data.get('queue_size', 0)
            print(f"  Queue size: {queue_size}")
            
            if queue_size == 0:
                print("  ⚠️  WARNING: Queue is EMPTY!")
            else:
                # Show AC frequency values in queue
                queue_items = queue_data.get('queue', [])
                ac_freqs_in_queue = []
                for item in queue_items:
                    if item.get('effect_type') == 'AC':
                        freq = item.get('properties', {}).get('frequency', 0)
                        if freq > 0:
                            ac_freqs_in_queue.append(freq)
                
                if ac_freqs_in_queue:
                    print(f"  AC frequencies in queue: {sorted(set(ac_freqs_in_queue))[:10]}")
                else:
                    print("  ⚠️  No AC configs in queue!")
    except Exception as e:
        print(f"  Queue endpoint not available: {e}")
    
    # Update queue manually
    print("\n[3] Manually updating queue...")
    try:
        r = requests.post(f"{API_BASE}/test-queue/update", timeout=10)
        if r.ok:
            result = r.json()
            print(f"  Queue updated: {result.get('queue_size', 0)} configs")
            
            # Show top AC configs
            queue_items = result.get('queue', [])
            ac_configs = [item for item in queue_items if item.get('effect_type') == 'AC'][:5]
            if ac_configs:
                print(f"  Top 5 AC configs in queue:")
                for i, item in enumerate(ac_configs):
                    props = item.get('properties', {})
                    print(f"    {i+1}. freq={props.get('frequency')} volt={props.get('voltage')} (priority: {item.get('priority')}, tested: {item.get('test_count')}x)")
        else:
            print(f"  Failed: {r.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Ensure sequencer has plants
    print("\n[4] Auto-populating sequencer storage with plants...")
    try:
        r = requests.post(f"{API_BASE}/sequencer/auto-populate", timeout=10)
        if r.ok:
            res = r.json()
            print(f"  Created {res.get('created_count', 0)} plants (empty slots: {res.get('empty_slots_found', 0)})")
        else:
            print(f"  Failed: {r.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

    # Check current EM effects
    print("\n[4] Checking current EM effects on grid...")
    try:
        r = requests.get(f"{API_BASE}/effects", timeout=5)
        if r.ok:
            effects_data = r.json()
            grid = effects_data.get('effects', [])
            
            ac_count = sum(1 for row in grid for e in row if e == 'AC')
            dc_count = sum(1 for row in grid for e in row if e == 'DC')
            amf_count = sum(1 for row in grid for e in row if e == 'AMF')
            cmf_count = sum(1 for row in grid for e in row if e == 'CMF')
            
            print(f"  AC: {ac_count}, DC: {dc_count}, AMF: {amf_count}, CMF: {cmf_count}")
            
            # Show AC frequencies on grid
            ac_freqs_on_grid = []
            for row_idx, row in enumerate(grid):
                for col_idx, effect in enumerate(row):
                    if effect == 'AC' and col_idx >= 8:  # EM zone
                        # Try to get properties
                        try:
                            r2 = requests.get(f"{API_BASE}/em-config/intelligent?row={row_idx}&col={col_idx}", timeout=2)
                            if r2.ok:
                                config = r2.json()
                                freq = config.get('properties', {}).get('frequency', 0)
                                if freq > 0:
                                    ac_freqs_on_grid.append(freq)
                        except:
                            pass
            
            if ac_freqs_on_grid:
                print(f"  AC frequencies on grid: {sorted(set(ac_freqs_on_grid))}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Start simulation at ultra-high speed
    print("\n[5] Starting simulation and setting speed to 500x...")
    try:
        r = requests.post(f"{API_BASE}/simulation/start", timeout=5)
        if r.ok:
            # Set speed via dedicated endpoint
            requests.put(f"{API_BASE}/simulation/speed", json={"speed": 500}, timeout=5)
            print("  Simulation started at 500x!")
            print("  Waiting 15 seconds for data collection...")

            state_before = check_server() or {}
            start_tick = state_before.get('tick', 0)
            time.sleep(15)

            # Check again
            state_after = check_server() or {}
            end_tick = state_after.get('tick', 0)
            ticks_elapsed = (end_tick or 0) - (start_tick or 0)
            print(f"  Ticks elapsed: {ticks_elapsed}")

            # Check parameter diversity again
            r2 = requests.get(f"{API_BASE}/plant-growth/unified", timeout=5)
            if r2.ok:
                data2 = r2.json()
                points2 = data2.get('data_points', [])
                ac_freqs2 = sorted(set([p.get('ac_frequency', 0) for p in points2 if p.get('ac_frequency', 0) > 0]))

                print(f"\n  After 15s:")
                print(f"    Total data points: {len(points2)}")
                print(f"    AC frequencies: {len(ac_freqs2)} values - {ac_freqs2}")
                if len(points2) == 0:
                    print("    ⚠️  Still no datapoints. Backend may need a restart to apply fixes.")
        else:
            print(f"  Failed to start: {r.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    main()
