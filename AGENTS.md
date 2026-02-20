# SystemMonitor 开发指南

## 项目概述
Windows 系统资源监控工具，使用 customtkinter 构建 GUI，实时显示 CPU、内存、GPU、网络延迟和网络速度等信息。

## 构建命令

### 运行程序
```bash
python system_monitor_gui.py
```

### 打包为 EXE
```bash
python -m PyInstaller SystemMonitor.spec --clean --noconfirm
```
输出文件位于 `dist\SystemMonitor.exe`

### 更换图标
1. 准备 `.ico` 文件（建议包含多尺寸：16x16, 32x32, 64x64, 128x128, 256x256）
2. 修改 `SystemMonitor.spec` 中的 `icon='xxx.ico'`
3. 重新打包

## 依赖管理

### 主要依赖
- `customtkinter` - GUI 框架
- `psutil` - 系统信息获取
- `pynvml` - NVIDIA GPU 监控（可选）

### 安装依赖
```bash
pip install customtkinter psutil pynvml
```

### 打包依赖
- `pyinstaller` - EXE 打包工具

## 代码风格规范

### 导入顺序
1. 标准库（按字母顺序排列）
2. 第三方库
3. 本地模块

组间用空行分隔：
```python
import psutil
import threading
import time

import customtkinter as ctk
```

### 命名约定
| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 常量 | 全大写，下划线分隔 | `FONT_TITLE`, `MAX_WIDTH` |
| 类 | 大驼峰命名 | `SystemMonitorApp`, `MetricCard` |
| 函数/方法 | 小写 + 下划线 | `get_cpu_usage()`, `update_data()` |
| 变量 | 小写 + 下划线 | `network_speed`, `bytes_per_sec` |
| 私有方法 | 下划线前缀 | `_format_speed()`, `_get_unit_multiplier()` |

### 格式化规则
- **缩进**: 4 个空格（禁止使用 Tab）
- **行宽**: 建议不超过 100 字符
- **运算符**: 两侧加空格 `a = b + c`
- **函数定义**: 后空一行
- **类定义**: 类内方法间空一行

### 类型注解
当前项目未强制使用类型注解，建议在复杂函数中添加：
```python
def get_memory_usage() -> dict:
    return {'total': 16.0, 'used': 8.5, 'percent': 53.1}
```

### 错误处理
- 使用 `try-except` 捕获特定异常
- 提供友好的中文错误信息
- 禁止静默失败

```python
try:
    import pynvml
    pynvml.nvmlInit()
except ImportError:
    return "pynvml 未安装"
except Exception as e:
    return f"获取失败：{str(e)}"
```

### 字符串格式化
统一使用 f-string：
```python
return f"{cpu:.1f}%"
return f"下载速度：{speed:.2f} MB/s"
```

### 中文字体
GUI 使用中文字体时需明确指定：
```python
FONT_TITLE = ("SimHei", 13, "bold")    # 黑体 - 标题
FONT_BODY = ("SimSun", 13, "bold")     # 宋体 - 正文
FONT_ENGLISH = ("Times New Roman", 12) # 英文/数字
FONT_SMALL = ("SimSun", 10)            # 小字
```

## 架构模式

### 分层结构
```
┌─────────────────────────────────┐
│         GUI 层                   │
│  SystemMonitorApp (主应用)       │
│  MetricCard (指标卡片组件)       │
│  SpeedBar (速度条组件)           │
├─────────────────────────────────┤
│       数据获取层                  │
│  get_cpu_usage()                │
│  get_memory_usage()             │
│  get_gpu_usage()                │
│  get_network_latency()          │
│  NetworkSpeedMonitor (类)       │
└─────────────────────────────────┘
```

### 刷新机制
```python
def auto_refresh_loop(self):
    self.update_data()
    self.root.after(1000, self.auto_refresh_loop)
```
- 使用 `threading.Thread` 异步获取数据，避免阻塞 UI
- 通过 `root.after(0, ...)` 将数据更新调度到主线程

## 测试

### 自动化测试
项目无自动化测试框架。

### 手动测试要点
1. **启动测试**: 启动程序，检查各指标是否正常显示
2. **负载测试**: 运行高负载程序，验证 CPU/GPU 使用率更新
3. **网络测试**: 下载文件，验证网络速度显示
4. **布局测试**: 调整窗口大小，检查布局响应

## 注意事项

### 版本控制
**不要提交**以下目录到版本控制：
- `build/`
- `dist/`
- `__pycache__/`
- `*.pyc`
- `*.exe`

### 布局修改
- 修改布局后需测试不同分辨率下的显示效果
- 确保窗口最小尺寸 (`minsize`) 合理设置

### GPU 监控
- GPU 监控依赖 NVIDIA 驱动和 `pynvml`
- AMD/Intel 显卡需单独处理（当前返回提示信息）

### 打包优化
- 打包时排除不必要的库（见 spec 文件的 `excludes`）
- 当前排除：`matplotlib`, `numpy`, `scipy`, `pandas`, `PIL`

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 中文乱码 | 确保字体支持中文（SimHei/SimSun） |
| GPU 检测失败 | 检查 pynvml 是否安装，驱动是否正常 |
| 打包后图标不显示 | 确认 icon 路径正确，重新清理打包 |
| 窗口显示异常 | 检查 customtkinter 版本兼容性 |

## 文件结构
```
SystemMonitor/
├── system_monitor_gui.py   # 主程序
├── SystemMonitor.spec      # PyInstaller 配置
├── mouse_icon.ico          # 程序图标
├── AGENTS.md               # 开发指南
├── README.md               # 项目说明
├── build/                  # 打包临时文件（不提交）
└── dist/                   # 打包输出（不提交）
    └── SystemMonitor.exe   # 可执行文件
```
