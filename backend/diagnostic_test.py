#!/usr/bin/env python3
"""
Diagnostic test for sequencer simulation.
Runs 1000 ticks and traces all plant/robot movements to find issues.
"""
import requests
import time
import json
from collections import defaultdict

API_BASE = "http://localhost:5000/api"

def get_state():
    """Get current simulation state"""
    try:
        r = requests.get(f"{API_BASE}/simulation/state", timeout=5)
        return r.json() if r.ok else None
    except:
        return None

def get_grid():
    """Get sequencer grid"""
    try:
        r = requests.get(f"{API_BASE}/sequencer", timeout=5)
        return r.json() if r.ok else None
    except:
        return None

def count_plants(grid):
    """Count plants in grid by zone"""
    storage = 0
    em_zone = 0
    total = 0
    plants = []
    
    # API returns {'sequencer': grid} not {'grid': grid}
    if not grid:
        return {'storage': 0, 'em_zone': 0, 'total': 0, 'plants': []}
    
    g = grid.get('sequencer') or grid.get('grid')
    if not g:
        return {'storage': 0, 'em_zone': 0, 'total': 0, 'plants': []}
    for row in range(len(g)):
        for col in range(len(g[row])):
            if g[row][col]:
                total += 1
                plants.append({'id': g[row][col][:20], 'row': row, 'col': col})
                if col < 8:
                    storage += 1
                else:
                    em_zone += 1
    
    return {'storage': storage, 'em_zone': em_zone, 'total': total, 'plants': plants}

def analyze_robots(state):
    """Analyze robot states"""
    if not state or 'robots' not in state:
        return []
    
    robots = []
    for r in state['robots']:
        robots.append({
            'id': r.get('id'),
            'state': r.get('state'),
            'holding': r.get('holding_plant', '')[:20] if r.get('holding_plant') else None,
            'col': r.get('col'),
            'target': r.get('target_col')
        })
    return robots

def main():
    print("=" * 80)
    print("SEQUENCER DIAGNOSTIC TEST - 1000 TICKS")
    print("=" * 80)
    
    # Check server
    state = get_state()
    if not state:
        print("ERROR: Cannot connect to server at localhost:5000")
        return
    
    print(f"Initial tick: {state.get('tick')}")
    
    # Stop any running simulation
    print("\n[1] Stopping current simulation...")
    requests.post(f"{API_BASE}/simulation/stop")
    time.sleep(1)
    
    # Auto-populate plants
    print("\n[2] Auto-populating plants...")
    r = requests.post(f"{API_BASE}/sequencer/auto-populate")
    if r.ok:
        result = r.json()
        print(f"  Created {result.get('created_count', 0)} plants")
    
    # Auto-set EM effects
    print("\n[2b] Auto-setting EM effects...")
    r = requests.post(f"{API_BASE}/em-effects/auto-set")
    if r.ok:
        result = r.json()
        print(f"  Set {result.get('count', 0)} EM effects")
        for u in result.get('updated', [])[:4]:
            print(f"    R{u['row']}C{u['col']}: {u['effect']} {u['properties']}")
    
    # Get initial state
    grid = get_grid()
    initial_count = count_plants(grid)
    print(f"\n[3] Initial plant count:")
    print(f"  Storage: {initial_count['storage']}")
    print(f"  EM Zone: {initial_count['em_zone']}")
    print(f"  Total: {initial_count['total']}")
    
    # Start simulation at high speed
    print("\n[4] Starting simulation at 100x speed...")
    r = requests.post(f"{API_BASE}/simulation/start", json={"speed": 100})
    if not r.ok:
        print(f"ERROR: Failed to start simulation: {r.text}")
        return
    
    # Track changes
    snapshots = []
    events = []
    last_plants = set(p['id'] for p in initial_count['plants'])
    
    print("\n[5] Running simulation for 1000 ticks...")
    print("    Sampling every 50 ticks...")
    
    start_time = time.time()
    tick_target = state.get('tick', 0) + 1000
    
    sample_interval = 50
    last_sample_tick = 0
    
    while True:
        state = get_state()
        if not state:
            print("ERROR: Lost connection to server")
            break
        
        current_tick = state.get('tick', 0)
        
        # Sample at intervals
        if current_tick >= last_sample_tick + sample_interval or current_tick >= tick_target:
            grid = get_grid()
            plant_count = count_plants(grid)
            robots = analyze_robots(state)
            
            current_plants = set(p['id'] for p in plant_count['plants'])
            
            # Check for disappeared plants
            disappeared = last_plants - current_plants
            appeared = current_plants - last_plants
            
            if disappeared:
                events.append({
                    'tick': current_tick,
                    'type': 'PLANT_DISAPPEARED',
                    'plants': list(disappeared)
                })
            
            if appeared:
                events.append({
                    'tick': current_tick,
                    'type': 'PLANT_APPEARED',
                    'plants': list(appeared)
                })
            
            snapshot = {
                'tick': current_tick,
                'storage': plant_count['storage'],
                'em_zone': plant_count['em_zone'],
                'total': plant_count['total'],
                'robots': robots,
                'observed': len(state.get('plants_observed', []))
            }
            snapshots.append(snapshot)
            
            # Print progress
            held_plants = [r['holding'] for r in robots if r['holding']]
            robot_states = [r['state'] for r in robots]
            print(f"  Tick {current_tick:4d}: storage={plant_count['storage']:2d} em={plant_count['em_zone']:2d} "
                  f"total={plant_count['total']:2d} obs={snapshot['observed']:3d} "
                  f"robots={robot_states} held={len(held_plants)}")
            
            last_plants = current_plants
            last_sample_tick = current_tick
            
            if current_tick >= tick_target:
                break
        
        time.sleep(0.1)  # Poll every 100ms
    
    elapsed = time.time() - start_time
    
    # Stop simulation
    requests.post(f"{API_BASE}/simulation/stop")
    
    # Final analysis
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    
    print(f"\nTime elapsed: {elapsed:.1f}s")
    
    final_state = get_state()
    final_grid = get_grid()
    final_count = count_plants(final_grid)
    
    print(f"\nPlant count change:")
    print(f"  Initial: {initial_count['total']} (storage: {initial_count['storage']}, em: {initial_count['em_zone']})")
    print(f"  Final:   {final_count['total']} (storage: {final_count['storage']}, em: {final_count['em_zone']})")
    print(f"  Lost:    {initial_count['total'] - final_count['total']}")
    
    print(f"\nObservations made: {final_state.get('plants_observed', [])[:10]}...")
    print(f"Total observations: {len(final_state.get('plants_observed', []))}")
    
    if events:
        print(f"\n{'='*40}")
        print("EVENTS LOG:")
        print(f"{'='*40}")
        for event in events[:50]:  # First 50 events
            print(f"  Tick {event['tick']}: {event['type']} - {event['plants'][:3]}...")
    
    # Check for issues
    print(f"\n{'='*40}")
    print("ISSUE DETECTION:")
    print(f"{'='*40}")
    
    issues = []
    
    # Check plant loss
    total_lost = initial_count['total'] - final_count['total']
    if total_lost > 5:
        issues.append(f"SEVERE: Lost {total_lost} plants during simulation")
    
    # Check if robots got stuck
    final_robots = analyze_robots(final_state)
    stuck_robots = [r for r in final_robots if r['holding']]
    if stuck_robots:
        issues.append(f"WARNING: {len(stuck_robots)} robots holding plants at end")
        for r in stuck_robots:
            issues.append(f"  Robot {r['id']}: state={r['state']} holding={r['holding']}")
    
    # Check for observation rate
    if len(final_state.get('plants_observed', [])) < 10:
        issues.append(f"WARNING: Very few observations ({len(final_state.get('plants_observed', []))})")
    
    # Print snapshot summary
    print(f"\n{'='*40}")
    print("SNAPSHOT SUMMARY (first and last 5):")
    print(f"{'='*40}")
    for s in snapshots[:5] + snapshots[-5:]:
        robot_info = ', '.join([f"{r['id']}:{r['state']}" for r in s['robots']])
        print(f"  T{s['tick']:4d}: total={s['total']:2d} obs={s['observed']:3d} [{robot_info}]")
    
    if issues:
        print(f"\n{'='*40}")
        print("ISSUES FOUND:")
        print(f"{'='*40}")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nNo major issues detected.")
    
    # Return summary for programmatic use
    return {
        'initial_total': initial_count['total'],
        'final_total': final_count['total'],
        'observations': len(final_state.get('plants_observed', [])),
        'events': events,
        'issues': issues
    }

if __name__ == "__main__":
    main()
