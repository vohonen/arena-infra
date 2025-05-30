#!/usr/bin/env python3
import runpod
import os
import sys
import time
import random
import string
import json

# load config.env environment variables
from mydotenv import load_env
load_env()

def create_specific_pods(
        pods_to_create: list[str],
        gpu_type_id: str = "NVIDIA RTX A4000",
        gpu_count: int = 1,
        runpod_cloud_type: str = "COMMUNITY",
        disk_space_in_gb: int = 100,
        volume_space_in_gb: int = 0,
        docker_image: str = "nickypro/arena-env:5.2",
        ports: str = "8888/http,22/tcp",
        volume_mount_path: str = "/workspace"
    ):
    """
    Creates specified RunPod pods if they don't already exist.

    Args:
        pods_to_create (list): A list of pod names to attempt to create.
    """
    # Get API key from environment
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("Error: RUNPOD_API_KEY environment variable not set")
        sys.exit(1) # Exit if API key is missing

    runpod.api_key = api_key

    print("Starting pod check process...")

    try:
        # --- Check for existing pods ---
        print("Fetching existing pods...")
        existing_pods = runpod.get_pods()
        existing_pod_names = {pod["name"] for pod in existing_pods}
        print(f"Found {len(existing_pod_names)} existing pods.")
        # --- End check ---

        # Separate pods into existing and new
        existing = [p for p in pods_to_create if p in existing_pod_names]
        to_create = [p for p in pods_to_create if p not in existing_pod_names]

        if existing:
            print("\nThe following pods already exist:")
            for pod in existing:
                print(f"  - {pod}")

        if not to_create:
            print("\nNo new pods to create.")
            return

        print("\nThe following pods will be created:")
        for pod in to_create:
            print(f"  - {pod}")

        # Ask for confirmation
        response = input("\nWould you like to proceed with creation? (y/N): ").lower()
        if response != 'y':
            print("Aborting pod creation.")
            return

        print("\nProceeding with pod creation...")
        created_count = 0
        error_count = 0

        for pod_name in to_create:
            try:
                print(f"\nAttempting to create pod '{pod_name}' with configuration:")
                print(f"  Image: {docker_image}")
                print(f"  GPU Type: {gpu_type_id}")
                print(f"  GPU Count: {gpu_count}")

                # Generate a random Jupyter password (though not used in create_pod)
                jupyter_password = "".join(
                    random.choices(string.ascii_lowercase + string.digits, k=20)
                )

                print("Making API call to create pod...")
                result = runpod.create_pod(
                    name=pod_name,
                    image_name=docker_image,
                    gpu_count=gpu_count,
                    volume_in_gb=volume_space_in_gb,
                    container_disk_in_gb=disk_space_in_gb,
                    ports=ports,
                    volume_mount_path=volume_mount_path,
                    gpu_type_id=gpu_type_id,
                    cloud_type=runpod_cloud_type,
                )

                print(f"✓ Successfully initiated creation for '{pod_name}'")
                print(f"  Pod Info: {result}")
                created_count += 1

                # Wait between creations to potentially avoid rate limiting
                time.sleep(2)

            except Exception as e:
                print(f"\nError creating pod '{pod_name}': {str(e)}")
                error_count += 1
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
    import argparse
    import ast

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Create RunPod instances')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-n', '--num-machines', type=int,
                      help='Number of machines to create from default list')
    group.add_argument('machine_names', nargs='*', default=[],
                      help='Specific machine names to create')

    # Add GPU and cloud configuration options
    parser.add_argument('--gpu-type',
                      help='GPU type to use (overrides RUNPOD_GPU_TYPE env var)')
    parser.add_argument('--gpu-count', type=int,
                      help='Number of GPUs per machine (overrides RUNPOD_NUM_GPUS env var)')
    parser.add_argument('--cloud-type', choices=['COMMUNITY', 'SECURE'],
                      help='RunPod cloud type (overrides RUNPOD_CLOUD_TYPE env var)')
    parser.add_argument('--docker-image', default="nickypro/arena-env:5.2",
                      help='Docker image to use (overrides RUNPOD_DOCKER_IMAGE env var)')
    parser.add_argument('--disk-space-in-gb', type=int, default=100,
                      help='Disk space in GB (overrides RUNPOD_DISK_SPACE_IN_GB env var)')
    parser.add_argument('--volume-space-in-gb', type=int, default=0,
                      help='Volume space in GB (overrides RUNPOD_VOLUME_SPACE_IN_GB env var)')

    # Get environment variables with defaults
    machine_prefix = os.environ["MACHINE_NAME_PREFIX"]
    machine_name_list = ast.literal_eval(os.environ["MACHINE_NAME_LIST"])

    # Parse arguments
    args = parser.parse_args()

    # Set configuration, preferring command line arguments over environment variables
    gpu_type_id = args.gpu_type or os.environ["RUNPOD_GPU_TYPE"]
    gpu_count = args.gpu_count or int(os.environ["RUNPOD_NUM_GPUS"])
    runpod_cloud_type = args.cloud_type or os.environ["RUNPOD_CLOUD_TYPE"]
    docker_image = args.docker_image or os.environ["RUNPOD_DOCKER_IMAGE"]
    disk_space_in_gb = args.disk_space_in_gb or int(os.environ["RUNPOD_DISK_SPACE_IN_GB"])
    volume_space_in_gb = args.volume_space_in_gb or int(os.environ["RUNPOD_VOLUME_SPACE_IN_GB"])

    # Determine which machines to create
    if args.machine_names:
        machine_name_list = args.machine_names
    elif args.num_machines:
        machine_name_list = machine_name_list[:args.num_machines]
    else:
        print(f"Using default list with {len(machine_name_list)} machines")

    print(f"Configuration:")
    print(f"  GPU Type: {gpu_type_id}")
    print(f"  GPU Count: {gpu_count}")
    print(f"  Cloud Type: {runpod_cloud_type}")

    pods_to_create = [f"{machine_prefix}-{name}" for name in machine_name_list]
    create_specific_pods(
        pods_to_create,
        gpu_type_id,
        gpu_count,
        runpod_cloud_type,
        disk_space_in_gb,
        volume_space_in_gb,
        docker_image,
    )
