#!/usr/bin/env python3
import argparse, os, sys, yaml

# Always prefer local src/ for imports
here = os.path.dirname(__file__)
sys.path.insert(0, os.path.normpath(os.path.join(here, "..", "src")))

from priceradar.cli import main as cli_main

def expand_env_vars_in_dict(d):
    if isinstance(d, dict):
        return {k: expand_env_vars_in_dict(v) for k, v in d.items()}
    if isinstance(d, list):
        return [expand_env_vars_in_dict(v) for v in d]
    if isinstance(d, str):
        return os.path.expandvars(d)
    return d

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="Path to YAML config")
    args = ap.parse_args()
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)
    cfg = expand_env_vars_in_dict(cfg)
    cli_main(cfg)
