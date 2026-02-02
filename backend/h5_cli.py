#!/usr/bin/env python3
"""CLI tool to inspect and manage the HDF5 data file"""
import h5py
import argparse
import json
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
data_file_path = project_root / "data" / "data.h5"

def inspect(args):
    """Show structure of h5 file"""
    with h5py.File(str(data_file_path), "r") as f:
        def print_item(name, obj):
            indent = "  " * name.count("/")
            if isinstance(obj, h5py.Dataset):
                print(f"{indent}{name}: Dataset shape={obj.shape}, dtype={obj.dtype}")
                if args.verbose and obj.shape[0] > 0 and obj.shape[0] < 10:
                    try:
                        data = list(obj[:])
                        if data and isinstance(data[0], bytes):
                            data = [x.decode("utf-8") if x else "" for x in data]
                        print(f"{indent}  Data: {data}")
                    except Exception as e:
                        print(f"{indent}  Error reading: {e}")
            else:
                print(f"{indent}{name}: Group")
                if args.verbose and obj.attrs:
                    for k, v in obj.attrs.items():
                        val = v.item() if hasattr(v, "item") else v
                        print(f"{indent}  @{k}: {val}")
        
        print(f"=== H5 File: {data_file_path} ===")
        print(f"Root keys: {list(f.keys())}\n")
        f.visititems(print_item)

def growth(args):
    """Show plant growth data"""
    with h5py.File(str(data_file_path), "r") as f:
        if "plant_growth_data" not in f:
            print("No plant_growth_data in file")
            return
        
        growth_group = f["plant_growth_data"]
        print(f"=== Plant Growth Data ({len(growth_group)} plants) ===\n")
        
        for plant_id in growth_group.keys():
            pg = growth_group[plant_id]
            ticks = list(pg["ticks"][:]) if "ticks" in pg else []
            growth = list(pg["growth"][:]) if "growth" in pg else []
            em_effect = pg.attrs.get("em_effect", "None")
            
            print(f"Plant: {plant_id}")
            print(f"  EM Effect: {em_effect}")
            print(f"  Data points: {len(ticks)}")
            if ticks:
                print(f"  Ticks: {ticks[:10]}{'...' if len(ticks) > 10 else ''}")
                print(f"  Growth: {[round(g, 3) for g in growth[:10]]}{'...' if len(growth) > 10 else ''}")
            
            # Show EM properties
            em_props = {}
            for key in pg.attrs.keys():
                if key.startswith("em_prop_"):
                    em_props[key[8:]] = pg.attrs[key]
            if em_props:
                print(f"  EM Props: {em_props}")
            print()

def plants(args):
    """Show plants in sequencer"""
    with h5py.File(str(data_file_path), "r") as f:
        if "sequencer" not in f:
            print("No sequencer in file")
            return
        
        seq = f["sequencer"]
        print(f"=== Sequencer Grid ===")
        print(f"Shape: {seq.shape}")
        
        if len(seq.shape) == 3 and seq.shape[2] > 0:
            for row in range(seq.shape[0]):
                row_data = seq[row, :, 0]
                row_data = [x.decode("utf-8") if isinstance(x, bytes) else x for x in row_data]
                print(f"Row {row}:")
                for col, plant in enumerate(row_data):
                    if plant:
                        zone = "STORAGE" if col < 8 else "EM" if col < 11 else "OBS"
                        print(f"  [{col}] ({zone}): {plant}")

def effects(args):
    """Show EM effects in sequencer"""
    with h5py.File(str(data_file_path), "r") as f:
        if "sequencer_effects" not in f:
            print("No sequencer_effects in file")
            return
        
        seq = f["sequencer_effects"]
        print(f"=== Sequencer Effects ===")
        print(f"Shape: {seq.shape}")
        
        if "sequencer_effects_properties" in f:
            props = f["sequencer_effects_properties"]
            print(f"\nEffect Properties ({len(props)} effects):")
            for uuid in props.keys():
                effect = props[uuid]
                effect_type = effect.attrs.get("effect_type", "?")
                row = effect.attrs.get("sequencer_row", "?")
                col = effect.attrs.get("sequencer_col", "?")
                print(f"  [{row},{col}] {effect_type}: {uuid[:30]}...")
                
                # Show properties
                for key in effect.attrs.keys():
                    if key.startswith("prop_"):
                        print(f"    {key[5:]}: {effect.attrs[key]}")

def clear_growth(args):
    """Clear plant growth data"""
    with h5py.File(str(data_file_path), "a") as f:
        if "plant_growth_data" in f:
            if args.plant_id:
                if args.plant_id in f["plant_growth_data"]:
                    del f["plant_growth_data"][args.plant_id]
                    print(f"Deleted growth data for: {args.plant_id}")
                else:
                    print(f"Plant not found: {args.plant_id}")
            else:
                del f["plant_growth_data"]
                print("Cleared all plant growth data")
        else:
            print("No plant_growth_data to clear")

def main():
    parser = argparse.ArgumentParser(description="HDF5 Data File CLI")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed info")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # inspect command
    inspect_parser = subparsers.add_parser("inspect", help="Show h5 file structure")
    
    # growth command
    growth_parser = subparsers.add_parser("growth", help="Show plant growth data")
    
    # plants command
    plants_parser = subparsers.add_parser("plants", help="Show plants in sequencer")
    
    # effects command
    effects_parser = subparsers.add_parser("effects", help="Show EM effects")
    
    # clear-growth command
    clear_parser = subparsers.add_parser("clear-growth", help="Clear growth data")
    clear_parser.add_argument("--plant-id", help="Specific plant ID to clear (or all if not specified)")
    
    args = parser.parse_args()
    
    if args.command == "inspect":
        inspect(args)
    elif args.command == "growth":
        growth(args)
    elif args.command == "plants":
        plants(args)
    elif args.command == "effects":
        effects(args)
    elif args.command == "clear-growth":
        clear_growth(args)
    else:
        # Default: show all
        args.verbose = True
        inspect(args)

if __name__ == "__main__":
    main()
