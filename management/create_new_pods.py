#!/usr/bin/env python3
import runpod
import os
import sys
import time
import random
import string

def create_specific_pods(pods_to_create):
    """
    Creates specified RunPod pods if they don't already exist.

    Args:
        pods_to_create (list): A list of pod names to attempt to create.
    """
    # Standard configuration for all pods
    base_config = {
        "image_name": "nickypro/arena-env:5.2",
        "gpu_count": 1,
        "volume_in_gb": 20,
        "container_disk_in_gb": 100,
        "ports": "8888/http,22/tcp",
        "volume_mount_path": "/workspace",
        "gpu_type_id": "NVIDIA RTX A4000",
        "cloud_type": "COMMUNITY",
    }

    # Get API key from environment
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("Error: RUNPOD_API_KEY environment variable not set")
        sys.exit(1) # Exit if API key is missing

    runpod.api_key = api_key

    print("Starting pod creation process...")

    try:
        # --- Check for existing pods ---
        print("Fetching existing pods...")
        existing_pods = runpod.get_pods()
        existing_pod_names = {pod["name"] for pod in existing_pods}
        print(f"Found {len(existing_pod_names)} existing pods.")
        # --- End check ---

        created_count = 0
        skipped_count = 0
        error_count = 0

        for pod_name in pods_to_create:
            # --- Check if pod already exists ---
            if pod_name in existing_pod_names:
                print(f"\nSkipping '{pod_name}': Pod with this name already exists.")
                skipped_count += 1
                continue
            # --- End check ---

            try:
                print(f"\nAttempting to create pod '{pod_name}' with configuration:")
                print(f"  Image: {base_config['image_name']}")
                print(f"  GPU Type: {base_config['gpu_type_id']}")
                print(f"  GPU Count: {base_config['gpu_count']}")
                # Add other config details if needed for logging

                # Generate a random Jupyter password (though not used in create_pod)
                # If you need to set env vars like JUPYTER_PASSWORD,
                # you'll need to add the 'env' parameter to create_pod
                jupyter_password = "".join(
                    random.choices(string.ascii_lowercase + string.digits, k=20)
                )

                print("Making API call to create pod...")
                # Note: The 'env' parameter can be used to set environment variables
                # Example: env={"JUPYTER_PASSWORD": jupyter_password}
                result = runpod.create_pod(
                    name=pod_name,
                    image_name=base_config["image_name"],
                    gpu_count=base_config["gpu_count"],
                    volume_in_gb=base_config["volume_in_gb"],
                    container_disk_in_gb=base_config["container_disk_in_gb"],
                    ports=base_config["ports"],
                    volume_mount_path=base_config["volume_mount_path"],
                    gpu_type_id=base_config["gpu_type_id"],
                    cloud_type=base_config["cloud_type"],
                    # Add env parameter here if needed:
                    # env={"EXAMPLE_VAR": "value"}
                )

                print(f"✓ Successfully initiated creation for '{pod_name}'")
                print(f"  Pod Info: {result}")
                # You might want to store/use this password if you configure Jupyter
                # print(f"  (Generated Jupyter Password: {jupyter_password})")
                created_count += 1

                # Wait between creations to potentially avoid rate limiting
                time.sleep(2)

            except Exception as e:
                print(f"\nError creating pod '{pod_name}': {str(e)}")
                error_count += 1
                # Decide if you want to continue or stop on error
                continue

    except Exception as e:
        # Catch errors during the initial get_pods call
        print(f"\nAn error occurred during initial setup: {str(e)}")
        sys.exit(1)

    print("\n--- Pod Creation Summary ---")
    print(f"Pods requested: {len(pods_to_create)}")
    print(f"Pods skipped (already existed): {skipped_count}")
    print(f"Pods creation initiated: {created_count}")
    print(f"Errors during creation: {error_count}")
    print("\nPod creation process completed!")
    print("Note: Pods may take a few minutes to fully start up and become ready.")


if __name__ == "__main__":
    pods_to_create = [
        "arena5-alpha",
        "arena5-bravo",
        "arena5-charlie",
        "arena5-delta",
        "arena5-echo",
        "arena5-foxtrot",
        "arena5-golf",
        "arena5-hotel",
        "arena5-india",
        "arena5-juliett",
        "arena5-kilo",
        "arena5-lima",
        "arena5-mike",
        "arena5-november",
        "arena5-oscar",
        "arena5-papa",
        "arena5-quebec",
        "arena5-romeo",
        "arena5-sierra",
        "arena5-tango",
	    "arena5-uniform",
        # "arena5-victor",
        # "arena5-whiskey",
        # "arena5-xray",
        # "arena5-yankee",
        # "arena5-zulu",
    ]
    create_specific_pods(pods_to_create)
