#!/bin/bash

# Set the SSH key path - update this with your actual key path
SSH_KEY="$HOME/.ssh/arena5_key"

# User for SSH connection
SSH_USER="root"  # Change this if you use a different user

# Max number of parallel processes
MAX_PARALLEL=10

# NATO phonetic alphabet array
NATO=(
  "alpha" "bravo" "charlie" "delta" "echo" "foxtrot" "golf" "hotel"
  "india" "juliett" "kilo" "lima" "mike" "november" "oscar" "papa"
  "quebec" "romeo" "sierra" "tango" "uniform" "victor" "whiskey"
  "xray" "yankee" "zulu"
)

# Files
FILE_KEY_LOCAL  = "./keys/arena5_key"
FILE_KEY_REMOTE = "~/.ssh/id_rsa"

# Command to run on each machine
CMD_INIT    = 'wget link.nicky.pro/init.sh && bash init.sh'
CMD_INSTALL = "bash -l -c 'source /opt/conda/etc/profile.d/conda.sh && conda activate arena-env && pip install -r /root/ARENA_3.0/requirements.txt'"
CMD_CHSH    = "chsh -s \$(which zsh)" # change shell to zsh
CMD_COPY    = "chmod 600 $KEY_REMOTE"

# Function to process a single host
process_host() {
  local nato_name="$1" # e.g., "alpha"
  local host="arena5-$1"
  local logfile="./logs/init-$1.log"
  
  echo "=== Connecting to $host (First run) ===" > "$logfile"
  
  # Test if the host is in the SSH config and can be reached
  if ssh -q -o BatchMode=yes -o ConnectTimeout=5 -i "$SSH_KEY" "$SSH_USER@$host" exit; then

    # 0. Add machine name
    #####################
    echo "" >> "$logfile"
    echo "=== Connecting to $host (Second run) ===" >> "$logfile"
    echo "Running initialization on $host (Second run)..." >> "$logfile"
    ssh -i "$SSH_KEY" "$SSH_USER@$host" "echo 'export MACHINE_NAME=$nato_name' > ~/.name" >> "$logfile" 2>&1
    echo "Added MACHINE_NAME=$nato_name to .name file" >> "$logfile"

    # 1. Copy over key
    ##################
    echo "Copying '$FILE_KEY_LOCAL' to $host:$FILE_KEY_REMOTE_KEY..." >> "$logfile"
    scp -i "$SSH_KEY" "$FILE_KEY_LOCAL" "$SSH_USER@$host:$FILE_KEY_REMOTE" >> "$logfile" 2>&1 \
      && ssh -i "$SSH_KEY" "$SSH_USER@$host" "chmod 600 $FILE_KEY_REMOTE" >> "$logfile" 2>&1
    if [ $? -ne 0 ]; then
        echo "Failed to copy '$FILE_KEY_LOCAL' to $host." >> "$logfile"
        echo "[FAIL] $host (scp key)"
    fi
    echo "Key file copied successfully." >> "$logfile"

    # 2. First run, Install main things
    ###################################
    echo "Running initialization on $host (First run)..." >> "$logfile"
    ssh -i "$SSH_KEY" "$SSH_USER@$host" "$CMD_INIT" >> "$logfile" 2>&1
    echo "First initialization completed for $host" >> "$logfile"
    
    # Wait a few seconds between runs
    sleep 3

    # 3. Second run, install packages in conda
    ##########################################
    echo "" >> "$logfile"
    echo "=== Connecting to $host (Second run) ===" >> "$logfile"
    echo "Running initialization on $host (Second run)..." >> "$logfile"
    ssh -i "$SSH_KEY" "$SSH_USER@$host" "$CMD_INSTALL" >> "$logfile" 2>&1
    echo "Second initialization completed for $host" >> "$logfile"

    # 4. Change default shell to zsh
    ################################
    echo "Attempting to change shell to zsh on $host..." >> "$logfile"
    echo "Executing chsh: $CMD_CHSH" >> "$logfile" # Log the command

    ssh -i "$SSH_KEY" "$SSH_USER@$host" "$chsh_command" >> "$logfile" 2>&1

    if [ $? -eq 0 ]; then
      echo "Shell changed successfully (or already set) on $host." >> "$logfile"
      echo "[DONE] $host" # Mark as done if both parts (or at least setup) worked
    else
      # Log failure but don't necessarily mark the whole host as failed if setup worked
      echo "Warning: Failed to change shell on $host. Zsh might not be installed or chsh failed." >> "$logfile"
      echo "[WARN] $host (chsh failed)" # Indicate a warning state
    fi


    echo "[DONE] $host"
  else
    echo "Could not connect to $host - skipping" >> "$logfile"
    echo "[SKIP] $host"
  fi
}

# Array to keep track of background processes
pids=()

# Process hosts in parallel, but limit to MAX_PARALLEL at a time
for name in "${NATO[@]}"; do
  # If we've reached the maximum number of parallel processes, wait for one to finish
  if [ ${#pids[@]} -ge $MAX_PARALLEL ]; then
    wait -n  # Wait for any process to finish
    # Remove completed processes from the array
    for i in "${!pids[@]}"; do
      if ! kill -0 ${pids[$i]} 2>/dev/null; then
        unset pids[$i]
      fi
    done
    pids=("${pids[@]}")  # Reindex array
  fi
  
  # Process this host in the background
  process_host "$name" &
  pids+=($!)
done

# Wait for all remaining processes to complete
wait

echo "All hosts processed!"
echo "Log files are in logs/init-*.log"

# Optional: Combine all logs into one file
cat ./logs/init-*.log > ./logs/init-all.log
echo "Combined log saved to init-all.log"
