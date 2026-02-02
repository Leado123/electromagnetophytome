#!/usr/bin/env python3
"""Test script for growth data persistence"""
import h5py
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
data_file_path = project_root / "data" / "data.h5"

def test_h5_write():
    """Test writing to h5 file"""
    print(f"Testing h5 file at: {data_file_path}")
    
    try:
        with h5py.File(str(data_file_path), "a") as f:
            # Test creating plant_growth_data group
            growth_group = f.require_group("plant_growth_data")
            print(f"✓ Created/accessed plant_growth_data group")
            
            # Test creating a test plant
            test_plant_id = "test-plant-12345"
            plant_group = growth_group.require_group(test_plant_id)
            print(f"✓ Created/accessed plant group: {test_plant_id}")
            
            # Test creating datasets
            if "ticks" not in plant_group:
                plant_group.create_dataset("ticks", data=[1, 2, 3], maxshape=(None,), dtype='i4')
                plant_group.create_dataset("growth", data=[1.0, 1.1, 0.95], maxshape=(None,), dtype='f8')
                print(f"✓ Created ticks and growth datasets")
            else:
                # Append test data
                ticks_ds = plant_group["ticks"]
                growth_ds = plant_group["growth"]
                old_size = ticks_ds.shape[0]
                new_size = old_size + 1
                ticks_ds.resize((new_size,))
                growth_ds.resize((new_size,))
                ticks_ds[-1] = old_size + 100
                growth_ds[-1] = 1.05
                print(f"✓ Appended to existing datasets, new size: {new_size}")
            
            # Set attributes
            plant_group.attrs["em_effect"] = "AC"
            plant_group.attrs["em_prop_frequency"] = 60
            print(f"✓ Set attributes")
            
        print("\n✓ H5 write test PASSED")
        return True
    except Exception as e:
        print(f"\n✗ H5 write test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_h5_read():
    """Test reading from h5 file"""
    print(f"\nReading h5 file...")
    
    try:
        with h5py.File(str(data_file_path), "r") as f:
            if "plant_growth_data" in f:
                print(f"✓ plant_growth_data exists")
                growth_group = f["plant_growth_data"]
                for plant_id in growth_group.keys():
                    pg = growth_group[plant_id]
                    ticks = list(pg["ticks"][:]) if "ticks" in pg else []
                    growth = list(pg["growth"][:]) if "growth" in pg else []
                    em_effect = pg.attrs.get("em_effect", None)
                    print(f"  Plant {plant_id}: ticks={ticks[:5]}..., growth={growth[:5]}..., em_effect={em_effect}")
            else:
                print(f"✗ plant_growth_data does NOT exist")
        return True
    except Exception as e:
        print(f"✗ H5 read test FAILED: {e}")
        return False

def test_api_endpoint():
    """Test the API endpoint"""
    import requests
    
    print(f"\nTesting API endpoint...")
    try:
        resp = requests.get("http://localhost:5000/api/plant-growth/all", timeout=5)
        data = resp.json()
        print(f"✓ API returned {len(data)} plants")
        for plant_id, plant_data in list(data.items())[:3]:
            print(f"  {plant_id}: ticks={plant_data.get('ticks', [])[:3]}, em_effect={plant_data.get('em_effect')}")
        return True
    except Exception as e:
        print(f"✗ API test FAILED: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Growth Data Test Suite")
    print("=" * 50)
    
    test_h5_write()
    test_h5_read()
    test_api_endpoint()
