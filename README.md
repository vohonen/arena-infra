# Infrastructure for ARENA 5.0

## TLDR steps.
1. **Generate a ssh key**: `ssh-keygen -t ed25519 -C "shared_infra_key_name"`, (change `shared_infra_key_name` to something meaningful for your program. We will use that for the rest of the discussion here). This will make two files:
- the private key `cat ~/.ssh/shared_infra_key_name`
- the public key `cat ~/.ssh/shared_infra_key_name.pub`

2. **Setting up the machines**: [Setup an account with RunPod](https://link.nicky.pro/runpod) or another GPU provider. You can then either setup each machine manually, or use a script to set them up. We currently mostly use RunPod Community Cloud A4000s for most of the program. You can either:

- a. Set them up manually (if only a few machines):
    - Go to [https://link.nicky.pro/runpod](https://link.nicky.pro/runpod) and click on "Create Instance".
    - Use our template [https://link.nicky.pro/runpod-arena-env](https://link.nicky.pro/runpod-arena-env), or create your own template by going My Templates > New Template, and create one called something like `arena-env` that uses the docker image [`nickypro/arena-env:5.2`](https://hub.docker.com/r/nickypro/arena-env), and increase the volume size to 100GB.
    - Create a pod with the template for each pair of participants.

- b. Set them up automatically using a script (if you have a lot of machines):
    - Create an API key for RunPod, by going Settings > API Keys > Create API Key with "all" permissions.
    - Add `export RUNPOD_API_KEY=<your_api_key>` to your `~/.bashrc` or `~/.zshrc` and reload the shell.
    - Run the script [./management/create_new_pods.py](./management/create_new_pods.py) with `python3 ./management/create_new_pods.py`
    - You can list all the machines you have created with `python3 ./management/nginx_pods.py`

3. **Connecting to the Machines - Get the SSH config**:
- a. Manually (must be updated if a new machine is added):
    - Get the ip address of the machine you set up (either from the RunPod dashboard or by running `python3 ./management/nginx_pods.py`).
    - set up a ssh config file to forward packets through the proxy machine. This is done in the file `~/.ssh/config` by adding lines of the form:
    ```
    Host arena-*
        User root
        IdentityFile ~/.ssh/shared_infra_key_name
        UserKnownHostsFile=/dev/null
        StrictHostKeyChecking=no

    Host arena-<machine_name>
        HostName <machine_ip>
        Port <port>
    ```
    - You should then be able to ssh into the machine with `ssh arena-<machine_name>`.

- b. Automatic Forwarding (best if you have a lot of machines):
    - I reccomend to set up a proxy machine (I use [hetzner](https://link.nicky.pro/hetzner), but you can use whatever you want). **This should NOT use the `shared_infra_key_name` key**, but instead your own ssh key (if you don't already have one, you can generate one with `ssh-keygen -t ed25519 -C "proxy_key_name"`).
    - You will need to create a machine (I use the `CAX21` VPS template on hetzner with the latest version of ubuntu.)
    - ssh into the new machine `ssh root@<proxy_machine_ip>`, as described by hetzner or whatever service you use.
    - Install nginx with stream module and setup a config file to forward packets to the machines. Easiest way to do this is to run this command on the proxy machine:
    - `git clone https://github.com/nickypro/.arena_dotfiles.git && cd .arena_dotfiles/proxy && sudo bash setup_nginx.sh && cd ~`
    - Next, you need to add a config that maps each of cloud machines to a port on the proxy machine. If using runpod, this can be generated automatically with `python3 ./management/nginx_pods.py`. This is done in the file `~/proxy.conf` by adding lines of the form:
    ```
    upstream <machine_name> { server <machine_ip>:<port>; }
    server { listen <port>; proxy_pass <machine_name>; }
    ```
    - You can add as many of these as you want, just make sure the ports don't conflict. By default we use ports 12000-12099.
    - You then need an ssh config to share the machines. This is done in the file `~/.ssh/config` by adding lines of the form. This can be generated automatically with `python3 ./management/ssh_config.py`:
    ```
    Host arena-*
        User root
        HostName <proxy_machine_ip>
        IdentityFile ~/.ssh/shared_infra_key_name
        UserKnownHostsFile=/dev/null
        StrictHostKeyChecking=no

    Host arena-alpha
        Port <proxy_port>
    ```
    - You should then be able to ssh into the machine with `ssh arena-<machine_name>`.

4. **Set up for users**:
- give the participants the ssh private key `cat ~/.ssh/shared_infra_key_name`, get them to save it in `~/.ssh/shared_infra_key_name`.
- If the participant is on MacOS/Linux, they will additionally need run `chmod 600 ~/.ssh/shared_infra_key_name` to make sure the key is not world readable.
- give the participants the ssh config file `cat ~/.ssh/config` from step 4. They should add the lines to their own `~/.ssh/config` file.

5. **Test the setup**:
- ssh into the machine with `ssh arena-<machine_name>`, then run `python3 -c "import torch; print(torch.__version__)"` to make sure the environment is set up correctly.
- run `bash ~/management/test_em.sh` to easily check pytorch is installed on all the machines.
- try that you can connect to the machine using `Remote-SSH: Connect to Host...` in VSCode.

6. **(optional) adding details and credentials to the machines**:
- you can make it so that the users can push to a branch of the arena repo, by automatically deploying the branch to the machine when it is pushed to. This is done by adding a deploy key to the repo, and copying the ssh key to the machines, most easily done with the script `python3 ./management/setup_em.py`.
- You can also automatically push all changes, by running `python3 ./management/sync_git.sh`



## Setting up machines

We use Runpod for the ARENA 5.0 infrastructure, as they are relatively affordable and have a good API for setting up machines, but if you want to do things manually or only have a few machines, you can use another service like Vast.ai or whetever else.

The runpod template is available here: [https://link.nicky.pro/runpod-arena-env](https://link.nicky.pro/runpod-arena-env), but the actual images are available on docker hub as [nickypro/arena-env](https://hub.docker.com/r/nickypro/arena-env).

The template is set to automatically clone the ARENA 5.0 repository and install the dependencies with conda and cuda.
