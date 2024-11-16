# Ansible Infrastructure

## Setup
1. Clone this repository
2. Install requirements: `ansible-galaxy install -r requirements.yml`
3. Update inventory files with your server IPs
4. Run playbooks: `ansible-playbook playbooks/site.yml`

## Structure
- `inventory/`: Server definitions for different environments
- `group_vars/`: Variables applied to groups of servers
- `host_vars/`: Variables applied to specific hosts
- `roles/`: Reusable configuration components
- `playbooks/`: Playbook definitions