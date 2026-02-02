#!/usr/bin/env python3
"""
Diagnostic tool to find missing plants
"""
import requests
import json

API_BASE = "http://localhost:5000/api"

def main():
    print("=" * 80)
    print("PLANT DISAPPEARANCE DIAGNOSTIC")
    print("=" * 80)
    
    # Get all plants
    try:
        r = requests.get(f"{API_BASE}/plants", timeout=5)
        if r.ok:
            plants_data = r.json()
            all_plants = plants_data.get('plants', [])
            print(f"\n[1] Total plants in system: {len(all_plants)}")
        else:
            print(f"[1] ERROR: Failed to get plants: {r.status_code}")
            return
    except Exception as e:
        print(f"[1] ERROR: {e}")
        return
    
    # Get sequencer grid
    try:
        r = requests.get(f"{API_BASE}/sequencer", timeout=5)
        if r.ok:
            seq_data = r.json()
            grid = seq_data.get('sequencer', [])
            
            plants_in_grid = []
            for row_idx, row in enumerate(grid):
                for col_idx, plant_id in enumerate(row):
                    if plant_id:
                        plants_in_grid.append(plant_id)
            
            print(f"[2] Plants in sequencer grid: {len(plants_in_grid)}")
            print(f"    Missing from grid: {len(all_plants) - len(plants_in_grid)}")
            
            if len(plants_in_grid) < len(all_plants):
                print(f"\n[3] MISSING PLANTS:")
                grid_set = set(plants_in_grid)
                missing = [p['id'] for p in all_plants if p['id'] not in grid_set]
                for plant_id in missing[:20]:
                    print(f"    {plant_id}")
                if len(missing) > 20:
                    print(f"    ... and {len(missing) - 20} more")
        else:
            print(f"[2] ERROR: Failed to get sequencer: {r.status_code}")
    except Exception as e:
        print(f"[2] ERROR: {e}")
    
    # Get robot states
    try:
        r = requests.get(f"{API_BASE}/simulation/state", timeout=5)
        if r.ok:
            state = r.json()
            robots = state.get('robots', [])
            
            print(f"\n[4] ROBOTS HOLDING PLANTS:")
            holding_count = 0
            for robot in robots:
                if robot.get('holding_plant'):
                    holding_count += 1
                    print(f"    Robot {robot['id']}: holding {robot['holding_plant'][:50]}...")
                    print(f"      State: {robot.get('state')}, Position: R{robot.get('row')}C{robot.get('col')}")
            
            if holding_count == 0:
                print("    No robots holding plants")
            
            total_accounted = len(plants_in_grid) + holding_count
            print(f"\n[5] SUMMARY:")
            print(f"    Plants in grid: {len(plants_in_grid)}")
            print(f"    Plants held by robots: {holding_count}")
            print(f"    Total accounted for: {total_accounted}")
            print(f"    Total plants in system: {len(all_plants)}")
            print(f"    UNACCOUNTED PLANTS: {len(all_plants) - total_accounted}")
            
            if len(all_plants) > total_accounted:
                print(f"\n⚠️  WARNING: {len(all_plants) - total_accounted} plants are missing!")
                print(f"    They exist in the system but are not in the grid or held by robots.")
                print(f"    This indicates a bug where plants are being lost.")
        else:
            print(f"[4] ERROR: Failed to get simulation state: {r.status_code}")
    except Exception as e:
        print(f"[4] ERROR: {e}")

if __name__ == "__main__":
    main()
