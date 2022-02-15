# scheduled_clicker

Quick and dirty autoclicker on a schedule

## Setup

Required: Python, Pip

```bash
git clone https://github.com/svandriessel/scheduled_clicker.git
python -m pip install -r requirements.txt
```

## Run

```bash
python main.py
```

### How it works

It will ask for time to start clicking. Options:
- 'default'
- datetime_format = "%Y-%m-%d %H:%M:%S"
- time_format = "%H:%M:%S"

It will run the scheduler and start autoclicking on the given time.

Meanwhile it will listen to keyboard input:
- Escape key to exit
- Caps Lock to start/stop clicking
