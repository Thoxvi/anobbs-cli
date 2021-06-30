# AnoBBS Cli

The command line interface of AnoBBS HTTP module.

## Usage

### 0x01 Install

```shell
# Install
git clone https://github.com/Thoxvi/AnoBBS-Cli.git anobbs
cd anobbs
python3 -m venv venv
source ./venv/bin/activate
pip3 install -e .

# Upgrade
cd anobbs
git pull
source ./venv/bin/activate
pip3 install -e .
```

### 0x02 Config

```shell
vim ~/.config/anobbs_cli/config.json
# Replace `address` with the real address, like `http://localhost:8080`
```

### 0x03 Find an invitation code

```shell
# Register
anobbs register [Find an invitation code]

# Check if the registration is successful
anobbs config
```

### 0x04 Have fun!

```shell
anobbs --help
# anobbs post 'Hello, AnoBBS!'
```
