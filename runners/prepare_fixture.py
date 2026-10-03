"""Prepare a fresh fixture only; no Claude call and no issue submission."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('destination', help='A new, empty/nonexistent destination outside the tracked fixture')
    args = p.parse_args()
    dest = Path(args.destination).resolve()
    if dest.exists(): p.error('Destination already exists; refusing to overwrite')
    fixture = ROOT/'fixtures/verification-ledger'
    if dest == fixture or fixture in dest.parents: p.error('Destination must not be inside the tracked fixture')
    shutil.copytree(fixture, dest, ignore=shutil.ignore_patterns('__pycache__', '.audit'))
    print('Fixture prepared. Expected baseline: 10 tests, 4 failures. Run python verify.py there.')

if __name__ == '__main__': main()
