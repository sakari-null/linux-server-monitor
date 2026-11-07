
# Linux Server Monitor

A Python-based system monitoring tool for Linux servers.

The application monitors:
- Disk usage
- Memory (RAM) usage
- CPU usage

It reports resource usage and assigns a status:
- NORMAL
- WARNING
- CRITICAL


## Requirements

- Linux operating system with `/proc` filesystem
- Python 3.13 or newer
- pytest (for running automated tests)


## Installation

Clone the repository:

```bash
git clone https://github.com/sakari-null/linux-server-monitor.git
cd linux-server-monitor
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Usage

Run the monitoring tool:

```bash
python src/monitor.py
```


## Testing

The project uses pytest for automated testing.

Install pytest:

```bash
python -m pip install -r requirements.txt
```

Run the tests:

```bash
python -m pytest -v
```

## Logging

The application records monitoring events and errors in:

```text
logs/monitor.log
```

Log files are automatically rotated to prevent unlimited log growth.
