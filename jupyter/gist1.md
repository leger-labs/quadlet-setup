Ansible playbook for installing Jupyter with miniconda and notebook_intelligence
gistfile1.txt
---
- name: Provision JupyterLab on a VM
  hosts: all
  become: yes
  vars_files:
    - vars/main.yml

  pre_tasks:
    - name: Install system dependencies
      import_tasks: tasks/system_deps.yml

  tasks:

    - name: Install Tailscale
      import_tasks: tasks/tailscale_setup.yml

    - name: Install Miniconda
      import_tasks: tasks/miniconda_setup.yml

    - name: Install JupyterLab as Vagrant
      block:
        - name: Set conda config
          command: "{{ miniconda_path }}/bin/conda config --set auto_activate_base false"
          changed_when: false

        - name: Add conda-forge channel
          command: "{{ miniconda_path }}/bin/conda config --add channels conda-forge"
          changed_when: false

        - name: Initialize conda for shells
          shell: "{{ item }}"
          loop:
            - "{{ miniconda_path }}/bin/conda init bash"
            - "{{ miniconda_path }}/bin/conda init zsh"
          args:
            creates: "{{ ansible_env.HOME }}/.{{ item | regex_replace('^.*conda init ([a-z]+).*$', '\\1') }}rc"

        - name: Create conda environment with base packages
          command: "{{ miniconda_path }}/bin/conda create -n {{ jupyterlab_conda_env }} python=3.11 jupyterlab nb_conda_kernels -y"
          register: conda_create
          changed_when: conda_create.rc == 0
          failed_when: conda_create.rc != 0 and 'already exists' not in conda_create.stderr

        - name: Install additional packages via pip
          shell: |
            source {{ miniconda_path }}/bin/activate {{ jupyterlab_conda_env }}
            pip install notebook_intelligence jupyterlab-github
          args:
            executable: /bin/bash

        - name: Create Jupyter config directory
          file:
            path: "/home/{{ jupyterlab_user }}/.jupyter"
            state: directory
            owner: "{{ jupyterlab_user }}"
            mode: '0755'

        - name: Copy Jupyter configuration file
          template:
            src: jupyter_lab_config.py.j2
            dest: "{{ jupyterlab_config_path }}"
            owner: "{{ jupyterlab_user }}"
            mode: '0644'

      become_user: "{{ jupyterlab_user }}"

    # --- JupyterLab Systemd Service ---
    - name: Create JupyterLab systemd service file
      template:
        src: jupyterlab.service.j2
        dest: /etc/systemd/system/jupyterlab.service
        owner: root
        group: root
        mode: 0644

    - name: Reload systemd manager configuration
      systemd:
        daemon_reload: yes

    - name: Enable and start JupyterLab service
      systemd:
        name: jupyterlab
        enabled: yes
        state: started
      
    # --- Papertrail Log Forwarding Service ---
    - name: Create Papertrail systemd service file
      template:
        src: papertrail.service.j2
        dest: /etc/systemd/system/papertrail.service
        owner: root
        group: root
        mode: 0644

    - name: Reload systemd manager configuration (again for Papertrail)
      systemd:
        daemon_reload: yes

    - name: Enable and start Papertrail log forwarding service
      systemd:
        name: papertrail
        enabled: yes
        state: started

    - name: Set tailscale serve of open
      ansible.builtin.command: tailscale serve --bg --https 443 localhost:8888
      become: true
jupyter_lab_config.py.j2
c = get_config()

# Disable authentication token
c.NotebookApp.token = ""

# Disable password change
c.NotebookApp.allow_password_change = False

# Listen on all interfaces
c.NotebookApp.ip = "0.0.0.0"

# Allow remote access
c.NotebookApp.allow_remote_access = True

# Allow all origins
c.NotebookApp.allow_origin = '*'

# allow cross-site requests (required for openwebui)
c.NotebookApp.disable_check_xsrf = True 

# Additional recommended settings
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8888
c.NotebookApp.notebook_dir = "/home/{{ jupyterlab_user }}" 
jupyterlab.service.j2
[Unit]
Description=JupyterLab Server
After=network.target

[Service]
User={{ jupyterlab_user }}
ExecStart=/home/vagrant/miniconda/envs/jupyterlab/bin/jupyter lab --config {{ jupyterlab_config_path }}
WorkingDirectory=/home/{{ jupyterlab_user }}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
