# Infrastructure for ARENA 5.0

This is the repository for running the the infrastructure for the [ARENA program](https://arena.education/). These scripts are used to set up cloud machines with GPUS with all necessary dependencies pre-installed for the participants to use and connect to.

We use Runpod for the ARENA 5.0 infrastructure, as they are relatively affordable and have a good API for setting up machines, but if you want to do things manually or only have a few machines, you can use another service like Vast.ai or whetever else.

The runpod template is available here: [https://link.nicky.pro/runpod-arena-env](https://link.nicky.pro/runpod-arena-env), but the actual images are available on docker hub as [nickypro/arena-env](https://hub.docker.com/r/nickypro/arena-env).

The template is set to automatically clone the latest version of the ARENA 3.0 repository and install the dependencies with conda and cuda.

## Steps for Setting up the infrastructure.

1. **Clone the repo on your local machine.**
- Clone this github repo on your local machine:
```git clone https://github.com/nickypro/arena-infra.git```
- install [runpod python api library](https://pypi.org/project/runpod/) on your local machine:
```pip install runpod```

2. **Get the keys**
- get api key from [runpod](https://link.nicky.pro/runpod)
- create a shared ssh key (optionally replace `shared_infra_key_name` with something meaningful for your program):
```ssh-keygen -t ed25519 -N "" -C "shared_infra_key_name" -f ~/.ssh/shared_infra_key_name```

<details>
<summary>What do these do?</summary>

- `RUNPOD_API_KEY`: The api key for runpod. This is optional, and you can use a different service if you prefer, but our scripts are set up to use runpod. Look below for "manual" setup if you don't want to use runpod.

- `SHARED_SSH_KEY_PATH`: This is a special key that allows anyone with it to access the machines. You should generate a new key for each program, and give it to all the participants. This has two components:
    - The private key, which you should save in `~/.ssh/shared_infra_key_name`. This is the key that is used to access the machines.
    - The public key, saved at `~/.ssh/shared_infra_key_name.pub`. This is put on the pods, so that if the users have the private key, they can ssh into the machines.

</details>
<details>
<summary>Why is a single key shared between all participants? Can I make a more secure setup?</summary>

As we don't keep sensitive data on the machines, and our participants have been heavily selected, the flexibility and ease of being able to move machines if there are issues and not needing cusomised workflows for assigning people to pairs outweigh the slightly less secure setup and potential ability for participants to "abuse" the setup.

It would be possible and more secure to have a different key for each participant, but this would make it more difficult to manage and would require a more complex setup. If this is something that you need, feel free to contact [Nicky](https://nicky.pro/), I can see what I can do for you.

</details>


3. **Add details to Config**
- open config.env and add the details for:
- `RUNPOD_API_KEY`, the api key for runpod.
- `SHARED_SSH_KEY_PATH`, the path to the ssh key you created in step 2.
- (optional) `MACHINE_NAME_PREFIX`, the prefix for the machine names for your program (e.g: `arena`).
- (optional) modify any settings like `RUNPOD_GPU_TYPE` or `RUNPOD_TEMPLATE_ID` as desired.
- (optional) modify `ARENA_REPO_OWNER` to the owner of the arena repo you want to use. You can use the default values for this, but if you want to be easily able to sync and save changes, you can change these to your own github fork of this repo.
- (optional) if you are planning to use many machines (>40), you will need to add more name options to the `MACHINE_NAME_LIST` variable in the config.

4. **Run the setup script to set up the machines**
- To create however many machines you need, run `python3 ./management/create_new_pods.py`. It will ask for input before creating each machine.
```python3 ./management/create_new_pods.py```
- (manual option) run `python3 ./management/ssh_config_manual.py` to print out the ssh config for the machines you have created. (this should give `~/.ssh/config` for the machines you have created). Save this file to your local machine.
```python3 ./management/ssh_config_manual.py >> ~/.ssh/config```
- test one of the machines by trying to ssh into them with `ssh arena-<machine_name>`.
- Test all of the machines by running `test_em.sh`:
```bash ~/management/test_em.sh```

<details>
<summary>I don't want to use runpod, or I don't want to run a script to set up the machines. Can I do it manually?</summary>

Yes, you can do it manually.

- a. Set them up manually (if only a few machines):
    - Go to [runpod](https://link.nicky.pro/runpod) and click on "Create Instance".
    - Use our template [https://link.nicky.pro/runpod-arena-env](https://link.nicky.pro/runpod-arena-env), or create your own template by going My Templates > New Template, and create one called something like `arena-env` that uses the docker image [`nickypro/arena-env:5.5`](https://hub.docker.com/r/nickypro/arena-env), and increase the volume size to 100GB.
    - Create a pod with the template for each pair of participants.

- b. VAST.ai
    - Go to [VAST.ai](https://link.nicky.pro/vast) and create an instance.
    - Use the `nickypro/arena-env:5.5` image.
    - Create an instance with desired GPU and reccomended ~100GB of storage.
    - You can then ssh into the machine using command given by VAST.

<details>

5. **Share the machines with the participants**
- give the participants the ssh private key `cat ~/.ssh/shared_infra_key_name`, get them to save it in `~/.ssh/shared_infra_key_name`. (If they are on MacOS/Linux, they will additionally need run `chmod 600 ~/.ssh/shared_infra_key_name` to make sure the key is not world readable.)
- give the participants the ssh config file `cat ~/.ssh/config` from step 4. They should add the lines to their own `~/.ssh/config` file.

6. **(optional) Streamlining the ssh config**
- One issue is that if you ever want to turn off a machine, or you want to change out one of the machines, you need to manually update the ssh config by giving this to each participant. This is a pain.
- set up an ubuntu proxy machine with many ports available. I use [hetzner](https://link.nicky.pro/hetzner), but you can use whatever you want.
- Update the config.env, `SSH_PROXY_HOST` should be the ip address or domain name of the proxy machine. (optionally update `SSH_PROXY_NGINX_CONFIG_PATH` and `SSH_PROXY_STARTING_PORT` if you want to run multiple instances of the proxy on the same machine.)
- clone this repo on the proxy machine:
```git clone https://github.com/nickypro/arena-infra.git && cd arena-infra```
- copy the config.env file to the proxy machine:
```scp config.env root@<proxy_machine_ip>:/home/ubuntu/arena-infra/config.env```
- setup nginx on the proxy machine: `sudo bash ./management/setup_nginx.sh`.
- on the proxy machine, run `python3 ./management/nginx_pods.py` to print out the nginx proxy config for the machines you have created. (this should give `~/proxy.conf` for the machines you have created). Add this to `~/proxy.conf` on the proxy machine. You can do this automatically with:
```python3 ./management/nginx_pods.py > ~/proxy.conf```

- You will also need to then restart nginx: `bash ~/update.sh` (or `sudo systemctl restart nginx`). Note that if there is an error in your config (eg: missing semicolon), nginx will not start. `nginx_pods.py` should directly give a working config, but if things fail, the best way to debug this is to run `journalctl -fu nginx` to see the error.
- On your local machine again now, you can generate the new ssh config file with `python3 ./management/ssh_config_proxy.py`. Now whenever you want to restart or change one of the machines, you only need to update the proxy config file and restart nginx on the proxy machine, no need to update the ssh config for all the participants.


## Detailed steps.
1. **Generate a ssh key**: `ssh-keygen -t ed25519 -N "" -C "shared_infra_key_name" -f ~/.ssh/shared_infra_key_name`, (change `shared_infra_key_name` to something meaningful for your program.

2. **Setting up the machines**: [Setup an account with RunPod](https://link.nicky.pro/runpod) or another GPU provider. You can then either setup each machine manually, or use a script to set them up. We currently mostly use RunPod Community Cloud A4000s for most of the program. You can either:

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

