#!/usr/bin/env python3
import runpod
import os
from datetime import datetime

def list_pods():
    # Get API key from environment
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("Error: RUNPOD_API_KEY environment variable not set")
        return

    runpod.api_key = api_key

    try:
        # Get all pods
        print("Fetching pods...")
        pods = runpod.get_pods()
        if not pods:
            print("No pods found")
            return

        # Sort pods by name
        pods = sorted(pods, key=lambda x: x['name'])

        # Print header for pod list
        print("\n" + "="*120)
        print(f"{'IP':<16} {'SSH Port':<10} {'Cost/hr':<10} {'Last Status Change'} {'Name':<15} {'Status':<12} {'GPU':<8} ")
        print("="*120)

        # Print each pod's information
        for pod in pods:
            try:
                # Get the public IP and port for SSH (type 'tcp')
                ssh_port = next((str(p['publicPort']) for p in pod['runtime']['ports']
                               if p['type'] == 'tcp' and p['isIpPublic']), 'N/A')
                public_ip = next((p['ip'] for p in pod['runtime']['ports']
                                if p['type'] == 'tcp' and p['isIpPublic']), 'N/A')

                # Format the status time
                status_time = pod['lastStatusChange']
                if ': ' in status_time:
                    status_time = status_time.split(': ')[1].split(' GMT')[0]

                # Get the status (first part before the colon)
                status = pod['lastStatusChange'].split(': ')[0] if ': ' in pod['lastStatusChange'] else pod['lastStatusChange']

                # Format cost with dollar sign
                cost = f"${pod['costPerHr']}"

                print(f"{public_ip:<16} {ssh_port:<10} {cost:<10} {status_time} {pod['name']:<15} {status:<12} {pod['machine']['gpuDisplayName']:<8}")
            except:
                print(pod)

        print("="*120 + "\n")

        # Generate Nginx configuration
        print("\n# Nginx Configuration")
        print("# -----------------\n")

        # NATO phonetic alphabet for pod names
        nato_alphabet = [
            "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
            "india", "juliett", "kilo", "lima", "mike", "november", "oscar", "papa",
            "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey",
            "xray", "yankee", "zulu"
        ]

        # Map for storing found pods
        found_pods = {}

        # Find pods that match the NATO naming pattern
        for pod in pods:
            for i, nato in enumerate(nato_alphabet):
                if pod['name'] == f"arena5-{nato}":
                    try:
                        # Get IP and port
                        ssh_port = next((str(p['publicPort']) for p in pod['runtime']['ports']
                                      if p['type'] == 'tcp' and p['isIpPublic']), None)
                        public_ip = next((p['ip'] for p in pod['runtime']['ports']
                                       if p['type'] == 'tcp' and p['isIpPublic']), None)

                        if public_ip and ssh_port:
                            found_pods[nato] = {
                                "ip": public_ip,
                                "port": ssh_port,
                                "listen_port": 12000 + i  # 12000 + index for consistent port numbering
                            }
                    except:
                        pass

        # Generate Nginx configuration for found pods
        for nato, data in found_pods.items():
            print(f"upstream {nato} {{ server {data['ip']}:{data['port']}; }}")
            print(f"server {{ listen {data['listen_port']}; proxy_pass {nato}; }}\n")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    list_pods()
