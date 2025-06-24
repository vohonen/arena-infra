#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

def should_run(schedule):
    now = datetime.now(timezone.utc)
    time_match = schedule.get("time") == now.strftime("%H:%M")
    day_match = now.strftime("%A").lower() in [d.lower() for d in schedule.get("days", [])]
    return time_match and day_match and schedule.get("enabled", True)

def run_command(cmd, dry_run):
    if dry_run:
        print(f"[DRY RUN] {cmd}")
        return
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, cwd=Path(__file__).parent)

def update_nginx(dry_run):
    if dry_run:
        print("[DRY RUN] Would update nginx config")
        return
    script = Path(__file__).parent.parent / "proxy/nginx_pods.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, cwd=script.parent)
    if result.returncode == 0:
        with open("/etc/nginx/streams-enabled/proxy.conf", "w") as f:
            f.write(result.stdout)
        subprocess.run(["sudo", "systemctl", "restart", "nginx"])
        print("Nginx updated")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="/etc/vm_scheduler/schedule.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    try:
        with open(args.config) as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Config file {args.config} not found")
        return
    
    executed = 0
    needs_nginx_update = False
    
    for schedule in config.get("schedules", []):
        if should_run(schedule):
            print(f"Executing: {schedule['name']}")
            run_command(schedule["command"], args.dry_run)
            executed += 1
            if any(x in schedule["command"] for x in ["create_new_pods", "stop_pods", "delete_pods"]):
                needs_nginx_update = True
    
    if needs_nginx_update:
        update_nginx(args.dry_run)
    
    print(f"Executed {executed} tasks")

if __name__ == "__main__":
    main()