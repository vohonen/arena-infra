#!/bin/bash
# Setup script for VM scheduler on proxy server

set -e

echo "Setting up VM scheduler on proxy server..."

# Create directories
sudo mkdir -p /etc/vm_scheduler
sudo mkdir -p /var/log

# Create Python virtual environment
python3 -m venv ~/vm_scheduler_venv
source ~/vm_scheduler_venv/bin/activate

# Install required packages
pip install runpod

# Copy schedule configuration
sudo cp schedule_example.json /etc/vm_scheduler/schedule.json
echo "Edit /etc/vm_scheduler/schedule.json to customize your schedule"

# Make scheduler script executable
chmod +x vm_scheduler.py

# Create cron job (runs every minute, but scheduler only acts on matching times)
(crontab -l 2>/dev/null; echo "* * * * * cd $(pwd) && ~/vm_scheduler_venv/bin/python3 vm_scheduler.py >> /var/log/vm_scheduler.log 2>&1") | crontab -

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit /etc/vm_scheduler/schedule.json with your desired schedule"
echo "2. Test with: ~/vm_scheduler_venv/bin/python3 vm_scheduler.py --dry-run"
echo "3. View logs: tail -f /var/log/vm_scheduler.log"
echo "4. Disable with: crontab -r"
