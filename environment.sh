#!/bin/zsh

# active virtualenv naming myenv
python3 -m venv myenv 
source myenv/bin/activate

# install requirements
pip install -r requirements.txt

# remain active after end of script
exec zsh
