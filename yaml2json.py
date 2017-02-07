#!/usr/bin/env
"""Convert YAML to JSON.

Usage: yaml2json.py < in.yaml > out.json
"""
import sys
import json
import yaml

if len(sys.argv) != 1:
    sys.exit(__doc__)

doc = yaml.load(sys.stdin)
json.dump(doc, sys.stdout, indent=2)
