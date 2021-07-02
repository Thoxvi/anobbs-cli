# AnoBBS Cli

The command line interface of AnoBBS HTTP module.

## Usage

### 0x01 Install

As a user:

```shell
pip3 install --user git+https://github.com/Thoxvi/anobbs-cli@main#egg=Ano-BBS-Cli --upgrade
```

As a developer:

```shell
# Install
git clone https://github.com/Thoxvi/anobbs-cli.git anobbs
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

Add `~/.local/bin` into `PATH` for `Linux` user

```shell
which_shell=$(echo $SHELL|sed 's;^.*/;;g')
echo "export PATH=$HOME/.local/bin:\$PATH" >> $HOME/.${which_shell}rc
source $HOME/.${which_shell}rc
```

Autocomplete for `Linux` and `macOS` user

```shell
which_shell=$(echo $SHELL|sed 's;^.*/;;g')
echo eval \"\$\(_ANOBBS_COMPLETE=source_${which_shell} anobbs\)\" >> $HOME/.${which_shell}rc
source $HOME/.${which_shell}rc
```

### 0x02 Config

```shell
# Create config file
anobbs config
anobbs addr -a [Address]
# Replace `Address` with the real address, like `http://localhost:8080`
```

### 0x03 Find an invitation code or account

#### Register

```shell
# Register
anobbs register [Find an invitation code]
# Check if the registration is successful
anobbs config
```

#### Existing account

```shell
# Set account
anobbs account -a [Account ID]
```

### 0x04 Have fun!

```shell
anobbs --help
# anobbs post 'Hello, AnoBBS!'
anobbs pages | less
```

## Troubleshoot

```shell
anobbs check
```

- Token usually expires after 1 day, you better `anobbs login` every day.
