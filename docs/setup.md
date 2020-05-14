# Install virtual environment (one time)

tested for <insert version number>

```
python -m pip install --user virtualenv
python -m virtualenv --help
```

# Setup virtual env

`virtualenv -p python3.7 .`

#### Activate the env

`source bin/activate`

#### Install pip-tools and requirements

```
pip install pip-tools
pip install -r requirements.txt
```

#### Run local server

`python application.py`
