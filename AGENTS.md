# AGENTS.md - System Monitor Development Guide

## Build & Run Commands

```bash
# Install dependencies
pip install psutil pynvml pyinstaller customtkinter darkdetect

# Run the application
python system_monitor_gui.py

# Build executable (Windows)
pyinstaller SystemMonitor.spec
# Output: dist/SystemMonitor.exe
```

## Testing

This project does not have automated tests. Manual testing steps:
1. Run `python system_monitor_gui.py`
2. Verify CPU, memory, GPU, and network metrics display correctly
3. Click "刷新" button to reset network stats
4. Test on systems with/without NVIDIA GPU

## Code Style Guidelines

### Imports
- Standard library imports first (alphabetically)
- Third-party imports second (alphabetically)
- Blank line between groups
- No trailing whitespace

```python
import psutil
import platform

import customtkinter as ctk
```

### Naming Conventions
- **Classes**: PascalCase (`SystemMonitorApp`, `MetricCard`)
- **Functions**: snake_case (`get_cpu_usage`, `update_data`)
- **Variables**: snake_case (`network_monitor`, `max_download`)
- **Constants**: UPPER_CASE (`FONT_TITLE`, `FONT_BODY`)
- **Private methods**: Leading underscore (`_format_speed`, `_get_unit_multiplier`)

### Formatting
- Indentation: 4 spaces (no tabs)
- Maximum line length: 120 characters
- Blank lines: 2 between top-level functions/classes, 1 between methods
- Trailing commas: Omit for single-line collections

### Type Hints
Type hints are not currently used but encouraged for new functions:
```python
def get_memory_usage() -> dict:
    ...
```

### Error Handling
- Use specific exception types when possible
- Wrap external library calls in try/except
- Return user-friendly error messages for UI display
- Log errors with descriptive messages

```python
def get_gpu_usage():
    try:
        import pynvml
        # ... GPU logic
    except ImportError:
        return "pynvml 未安装"
    except Exception as e:
        return f"获取失败：{str(e)}"
```

### Threading
- Use daemon threads for background data fetching
- Never update GUI from worker threads - use `root.after(0, callback)`
- Keep critical sections minimal

```python
def update_data(self):
    def task():
        cpu = get_cpu_usage()
        self.root.after(0, lambda: self.display_data(cpu))
    thread = threading.Thread(target=task, daemon=True)
    thread.start()
```

### GUI Component Conventions
- **MetricCard**: For displaying single metrics (CPU, memory, etc.)
- **SpeedBar**: For progress bar visualization (network speed)
- **SystemMonitorApp**: Main application class
- Use `place()` for absolute positioning within frames
- Use `grid()` for top-level layout
- Color scheme:
  - Card background: `#2a2a2a`
  - Progress bar background: `#3a3a3a`
  - Download bar: `#66BB6A` (green)
  - Upload bar: `#FF7043` (orange)

### Fonts
```python
FONT_TITLE = ("SimHei", 13, "bold")      # Chinese titles
FONT_BODY = ("SimSun", 13, "bold")       # Main content
FONT_ENGLISH = ("Times New Roman", 12)   # Numbers/units
FONT_SMALL = ("SimSun", 10)              # Labels
```

### PyInstaller Configuration
- Entry point: `system_monitor_gui.py`
- Hidden imports: `psutil`, `customtkinter`, `darkdetect`
- Excluded modules: `matplotlib`, `numpy`, `scipy`, `pandas`, `PIL`
- Console: Disabled (GUI only)

## File Structure
```
SystemMonitor/
├── system_monitor_gui.py    # Main application (single-file)
├── SystemMonitor.spec       # PyInstaller build config
├── README.md                # User documentation
├── AGENTS.md                # This file - developer guide
├── build/                   # Build artifacts (ignored)
└── dist/                    # Output executables (ignored)
```

## Key Classes
| Class | Purpose |
|-------|---------|
| `NetworkSpeedMonitor` | Track network I/O, calculate speeds, track max/total |
| `MetricCard` | Reusable component for displaying metric values |
| `SpeedBar` | Progress bar widget for upload/download visualization |
| `SystemMonitorApp` | Main application, manages layout and refresh loop |

## Data Collection Sources
| Metric | Library | Method |
|--------|---------|--------|
| CPU | psutil | `cpu_percent(interval=1)` |
| Memory | psutil | `virtual_memory()` |
| GPU | pynvml | `nvmlDeviceGet*` APIs |
| Network latency | subprocess | `ping` command |
| Network speed | psutil | `net_io_counters()` |

## Notes
- Windows-only application (uses Windows-specific ping parameters)
- Chinese UI text with SimHei/SimSun fonts
- GPU monitoring requires NVIDIA GPU and pynvml package
- Auto-refresh interval: 1000ms (1 second)
