#!/bin/bash

target_dir="/home/nimesh/CICFlowMeter/data/daily"

cd "$target_dir" || { echo "Directory not found: $target_dir"; exit 1; }

echo "Available files:"
select file in *; do
    if [[ -n "$file" && -f "$file" ]]; then
        echo "You selected: $file"
        break
    else
        echo "Invalid selection. Please try again."
    fi
done

read -p "Enter IP Address of Receiver: " ip_receiver
full_ip="$ip_receiver"

pwd

cd /home/nimesh
echo "Running: python3 sender.py \"$target_dir/$file\" $full_ip"
python3 send_to_host.py "$target_dir/$file" "$full_ip"
