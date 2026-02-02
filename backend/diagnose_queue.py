#!/usr/bin/env python3
"""
Diagnostic tool to check test queue and parameter diversity.
"""
import requests
import json

API_BASE = "http://localhost:5000/api"

def get_queue():
    """Get current test queue"""
    try:
        r = requests.get(f"{API_BASE}/test-queue", timeout=5)
        return r.json() if r.ok else None
    except Exception as e:
        print(f"Error getting queue: {e}")
        return None

def get_growth_data():
    """Get unified growth data"""
    try:
        r = requests.get(f"{API_BASE}/plant-growth/unified", timeout=5)
        return r.json() if r.ok else None
    except Exception as e:
        print(f"Error getting growth data: {e}")
        return None

def get_effects():
    """Get current EM effects"""
    try:
        r = requests.get(f"{API_BASE}/effects", timeout=5)
        return r.json() if r.ok else None
    except Exception as e:
        print(f"Error getting effects: {e}")
        return None

def analyze_parameter_diversity():
    """Analyze what parameter values are actually being tested"""
    data = get_growth_data()
    if not data or 'data_points' not in data:
        print("No growth data available")
        return
    
    points = data['data_points']
    
    # Group by effect type and parameter
    by_effect_param = {}
    
    for point in points:
        effect = point.get('effect_type', 'Control')
        if effect == 'Control':
            continue
        
        if effect not in by_effect_param:
            by_effect_param[effect] = {}
        
        # Extract parameter values
        if effect == 'AC':
            freq = point.get('ac_frequency', 0)
            volt = point.get('ac_voltage', 0)
            if freq > 0:
                if 'frequency' not in by_effect_param[effect]:
                    by_effect_param[effect]['frequency'] = set()
                by_effect_param[effect]['frequency'].add(freq)
            if volt > 0:
                if 'voltage' not in by_effect_param[effect]:
                    by_effect_param[effect]['voltage'] = set()
                by_effect_param[effect]['voltage'].add(volt)
        elif effect == 'DC':
            volt = point.get('dc_voltage', 0)
            curr = point.get('dc_current', 0)
            if volt > 0:
                if 'voltage' not in by_effect_param[effect]:
                    by_effect_param[effect]['voltage'] = set()
                by_effect_param[effect]['voltage'].add(volt)
            if curr > 0:
                if 'current' not in by_effect_param[effect]:
                    by_effect_param[effect]['current'] = set()
                by_effect_param[effect]['current'].add(curr)
        elif effect == 'AMF':
            freq = point.get('amf_frequency', 0)
            amp = point.get('amf_amplitude', 0)
            if freq > 0:
                if 'frequency' not in by_effect_param[effect]:
                    by_effect_param[effect]['frequency'] = set()
                by_effect_param[effect]['frequency'].add(freq)
            if amp > 0:
                if 'amplitude' not in by_effect_param[effect]:
                    by_effect_param[effect]['amplitude'] = set()
                by_effect_param[effect]['amplitude'].add(amp)
        elif effect == 'CMF':
            strength = point.get('cmf_strength', 0)
            if strength > 0:
                if 'strength' not in by_effect_param[effect]:
                    by_effect_param[effect]['strength'] = set()
                by_effect_param[effect]['strength'].add(strength)
    
    print("\n" + "=" * 80)
    print("PARAMETER DIVERSITY ANALYSIS")
    print("=" * 80)
    
    for effect, params in by_effect_param.items():
        print(f"\n{effect} Effect:")
        for param_name, values in params.items():
            sorted_vals = sorted(values)
            print(f"  {param_name}: {len(sorted_vals)} unique values")
            print(f"    Values: {sorted_vals}")
            
            # Check for gaps
            if len(sorted_vals) >= 2:
                gaps = []
                for i in range(len(sorted_vals) - 1):
                    gap = sorted_vals[i+1] - sorted_vals[i]
                    relative_gap = gap / sorted_vals[i] if sorted_vals[i] > 0 else gap
                    if relative_gap > 0.05:  # >5% gap
                        gaps.append({
                            'lower': sorted_vals[i],
                            'upper': sorted_vals[i+1],
                            'gap': gap,
                            'relative': relative_gap
                        })
                
                if gaps:
                    print(f"    Gaps detected: {len(gaps)}")
                    for gap in gaps[:5]:
                        print(f"      {gap['lower']} -> {gap['upper']} (gap: {gap['gap']:.2f}, {gap['relative']*100:.1f}%)")
                else:
                    print(f"    No significant gaps (>5%)")

def analyze_queue():
    """Analyze test queue state"""
    queue_data = get_queue()
    if not queue_data:
        print("Could not get queue data")
        return
    
    print("\n" + "=" * 80)
    print("TEST QUEUE ANALYSIS")
    print("=" * 80)
    
    queue_size = queue_data.get('queue_size', 0)
    queue_items = queue_data.get('queue', [])
    
    print(f"\nQueue size: {queue_size}")
    print(f"Queue items shown: {len(queue_items)}")
    
    if queue_size == 0:
        print("\n⚠️  WARNING: Queue is EMPTY!")
        print("   This means no new tests are being generated.")
        return
    
    # Group by effect type
    by_effect = {}
    by_reason = {'std_reduction': 0, 'gap_filling': 0, 'exploration': 0}
    
    for item in queue_items:
        effect = item.get('effect_type', 'Unknown')
        reason = item.get('reason', 'unknown')
        test_count = item.get('test_count', 0)
        priority = item.get('priority', 0)
        
        if effect not in by_effect:
            by_effect[effect] = []
        by_effect[effect].append({
            'properties': item.get('properties', {}),
            'reason': reason,
            'test_count': test_count,
            'priority': priority
        })
        
        by_reason[reason] = by_reason.get(reason, 0) + 1
    
    print(f"\nQueue breakdown by reason:")
    for reason, count in by_reason.items():
        print(f"  {reason}: {count}")
    
    print(f"\nQueue breakdown by effect type:")
    for effect, items in by_effect.items():
        print(f"\n  {effect} ({len(items)} items):")
        
        # Show parameter values
        if effect == 'AC':
            freqs = sorted(set([item['properties'].get('frequency', 0) for item in items if item['properties'].get('frequency', 0) > 0]))
            volts = sorted(set([item['properties'].get('voltage', 0) for item in items if item['properties'].get('voltage', 0) > 0]))
            print(f"    Frequencies in queue: {freqs}")
            print(f"    Voltages in queue: {volts}")
        elif effect == 'DC':
            volts = sorted(set([item['properties'].get('voltage', 0) for item in items if item['properties'].get('voltage', 0) > 0]))
            currs = sorted(set([item['properties'].get('current', 0) for item in items if item['properties'].get('current', 0) > 0]))
            print(f"    Voltages in queue: {volts}")
            print(f"    Currents in queue: {currs}")
        elif effect == 'AMF':
            freqs = sorted(set([item['properties'].get('frequency', 0) for item in items if item['properties'].get('frequency', 0) > 0]))
            amps = sorted(set([item['properties'].get('amplitude', 0) for item in items if item['properties'].get('amplitude', 0) > 0]))
            print(f"    Frequencies in queue: {freqs}")
            print(f"    Amplitudes in queue: {amps}")
        elif effect == 'CMF':
            strengths = sorted(set([item['properties'].get('strength', 0) for item in items if item['properties'].get('strength', 0) > 0]))
            print(f"    Strengths in queue: {strengths}")
        
        # Show test counts
        test_counts = [item['test_count'] for item in items]
        max_tested = max(test_counts) if test_counts else 0
        print(f"    Max test count: {max_tested} (limit: 8)")
        
        # Show top priorities
        top_items = sorted(items, key=lambda x: x['priority'], reverse=True)[:3]
        print(f"    Top priorities:")
        for item in top_items:
            props_str = ', '.join([f"{k}={v}" for k, v in item['properties'].items()])
            print(f"      Priority {item['priority']}: {props_str} (tested {item['test_count']}x, reason: {item['reason']})")

def check_current_effects():
    """Check what effects are currently set"""
    effects_data = get_effects()
    if not effects_data or 'effects' not in effects_data:
        print("Could not get effects data")
        return
    
    print("\n" + "=" * 80)
    print("CURRENT EM EFFECTS ON GRID")
    print("=" * 80)
    
    grid = effects_data['effects']
    effects_set = {}
    
    for row_idx, row in enumerate(grid):
        for col_idx, effect in enumerate(row):
            if effect:
                if effect not in effects_set:
                    effects_set[effect] = []
                effects_set[effect].append((row_idx, col_idx))
    
    print(f"\nEffects currently set: {len([e for row in grid for e in row if e])}")
    for effect, positions in effects_set.items():
        print(f"  {effect}: {len(positions)} tiles - {positions}")

def check_simulation_state():
    """Check simulation state"""
    try:
        r = requests.get(f"{API_BASE}/simulation/state", timeout=5)
        if r.ok:
            state = r.json()
            print(f"\nSimulation State:")
            print(f"  Running: {state.get('running')}")
            print(f"  Tick: {state.get('tick')}")
            print(f"  Observations: {len(state.get('plants_observed', []))}")
    except:
        pass

def main():
    print("=" * 80)
    print("QUEUE AND PARAMETER DIVERSITY DIAGNOSTIC")
    print("=" * 80)
    
    # Check simulation state
    check_simulation_state()
    
    # Check current effects
    check_current_effects()
    
    # Analyze parameter diversity
    analyze_parameter_diversity()
    
    # Analyze queue (if endpoints exist)
    try:
        analyze_queue()
    except:
        print("\n⚠️  Queue endpoints not available (server may need restart)")
    
    # Try to update queue and see what happens
    print("\n" + "=" * 80)
    print("MANUAL QUEUE UPDATE TEST")
    print("=" * 80)
    
    try:
        r = requests.post(f"{API_BASE}/test-queue/update", timeout=10)
        if r.ok:
            result = r.json()
            print(f"\nQueue update successful!")
            print(f"  New queue size: {result.get('queue_size', 0)}")
            print(f"  Top 10 items:")
            for i, item in enumerate(result.get('queue', [])[:10]):
                props = item.get('properties', {})
                print(f"    {i+1}. {item.get('effect_type')} {props} (priority: {item.get('priority')}, reason: {item.get('reason')}, tested: {item.get('test_count')}x)")
        else:
            err = r.text
            print(f"\nQueue update failed: {err}")
            print("  (This is OK if endpoints aren't loaded yet)")
    except Exception as e:
        print(f"\nError updating queue: {e}")
        print("  (This is OK if endpoints aren't loaded yet)")
    
    # Re-analyze queue after update
    try:
        print("\n" + "=" * 80)
        print("QUEUE AFTER UPDATE")
        print("=" * 80)
        analyze_queue()
    except:
        pass
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("1. Restart server to load new queue endpoints")
    print("2. Check server logs for [QUEUE] messages")
    print("3. Manually trigger queue update: POST /api/test-queue/update")
    print("4. Check if auto-assignment is working every 25 ticks")

if __name__ == "__main__":
    main()
