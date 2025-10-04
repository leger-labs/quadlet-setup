# Jupyter Lab Container

Jupyter Lab service for OpenWebUI Code Interpreter integration.

## Overview

This container runs Jupyter Lab using the `scipy-notebook` image which includes:
- Python 3.x
- JupyterLab interface
- NumPy, Pandas, Matplotlib, SciPy pre-installed
- Scientific computing libraries

## Configuration

### Ports
- **Internal**: `{{ .ports.jupyter }}` - Container listens on this port
- **Published**: `{{ .services.jupyter.port }}` - Host published port for external/Caddy access
- **Network**: Connected to `llm.network` for container-to-container communication

### Authentication
- **NO AUTHENTICATION** - Configured per CLAUDE.md "NO LOGIN PREFERRED" policy
- Token and password disabled for local-only services
- XSRF checks disabled for OpenWebUI integration
- Allows any origin for API access

### OpenWebUI Integration

#### Access URL
- **From OpenWebUI**: `http://jupyter:{{ .ports.jupyter }}`
- **External (via Tailscale)**: `https://{{ .services.jupyter.subdomain }}.{{ .tailscale.full_hostname }}`

#### Setup in OpenWebUI
1. Go to Admin Panel → Settings → Code Execution
2. Enable "Code Interpreter"
3. Select "Jupyter" as the interpreter
4. Set Jupyter URL: `http://jupyter:{{ .ports.jupyter }}`
5. Authentication: None (or use token if configured)
6. Save settings

#### Features
- **Code Interpreter**: Allows AI to execute Python code for data analysis, visualizations, and computations
- **Session Persistence**: Maintains context between code blocks in a conversation
- **Package Installation**: Can install additional Python packages as needed

## Usage

### Starting the Service
```bash
systemctl --user start jupyter.service
systemctl --user status jupyter.service
```

### Accessing Jupyter Lab
```bash
# Via Tailscale URL (external)
https://{{ .services.jupyter.subdomain }}.{{ .tailscale.full_hostname }}

# From containers on llm.network
http://jupyter:{{ .ports.jupyter }}
```

### Installing Additional Packages
From within a Jupyter notebook:
```python
%conda install package-name
# or
!pip install package-name
```

## Integration Details

### How OpenWebUI Uses Jupyter
1. User asks AI to perform data analysis or create visualizations
2. AI generates Python code
3. Code is sent to Jupyter via API
4. Jupyter executes code in a kernel
5. Results (text output, plots, errors) are returned to OpenWebUI
6. AI interprets results and continues conversation

### Differences from Pyodide
- **Jupyter**: Full Python environment, can install packages, persistent kernel
- **Pyodide**: Browser-based Python, limited packages, runs in sandbox

## References

This implementation was inspired by:
- **Article**: "Jupyter with OpenWebUI code interpreter" by Terse Systems
  - Source: `/jupyter/article1.md`
  - Key insights: Jupyter integration, authentication setup, OpenWebUI configuration
- **Reddit Discussion**: "Don't sleep on the new Jupyter feature"
  - Source: `/jupyter/article2.md`
  - Key insights: Practical use cases, limitations, authentication methods
- **Harbor Reference**: Dockerfile and environment setup
  - Source: `/inspiration/harbor/jupyter/`
  - Key insights: Base image selection, containerization approach

## Troubleshooting

### Kernel Connection Issues
- Ensure Jupyter service is running: `systemctl --user status jupyter.service`
- Check network connectivity: `podman exec openwebui ping jupyter`
- Verify port configuration matches in both services

### Code Execution Failures
- Check Jupyter logs: `journalctl --user -u jupyter.service -f`
- Ensure packages are installed in the kernel
- Verify OpenWebUI settings point to correct URL

### Authentication Errors
- This setup disables authentication for simplicity
- If authentication is needed, configure token in `.chezmoi.yaml.tmpl`
- Update OpenWebUI settings to include token

## Security Notes

- Runs as root user for maximum compatibility with OpenWebUI
- No authentication enabled (local-only service)
- Only accessible via llm.network from other containers
- External access via Tailscale + Caddy (authenticated at network level)
