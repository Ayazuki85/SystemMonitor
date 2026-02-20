# 系统资源监控器 (System Monitor)

一个基于 Python 的系统资源监控工具，提供图形化界面实时显示 CPU、内存、GPU 和网络使用情况。

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 功能特性

- **CPU 监控** - 实时显示 CPU 使用率
- **内存监控** - 显示内存使用量、总量和使用百分比
- **GPU 监控** - 支持 NVIDIA GPU 使用率和显存监控（可选）
- **网络延迟** - 实时测试网络延迟
- **网络速度** - 显示实时下载/上传速度
- **流量统计** - 累计流量和历史最高网速记录
- **自动刷新** - 每秒自动更新数据
- **深色主题** - 现代化深色界面，支持自动主题检测

## 系统要求

- Windows 10
- Python 3.7 或更高版本
- NVIDIA GPU（可选，用于 GPU 监控）

## 安装

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd SystemMonitor
```

### 2. 安装依赖

```bash
pip install psutil pynvml pyinstaller customtkinter darkdetect
```

**依赖说明：**
| 包 | 用途 | 必需 |
|---|---|---|
| psutil | 系统信息获取（CPU、内存、网络） | 是 |
| customtkinter | 现代化 GUI 框架 | 是 |
| darkdetect | 自动检测系统深色/浅色主题 | 是 |
| pynvml | NVIDIA GPU 监控 | 否 |
| pyinstaller | 打包为可执行文件 | 否 |

## 使用方法

### 运行 GUI 版本

```bash
python system_monitor_gui.py
```

### 界面说明

```
┌─────────────────────────────────────────────┐
│  [CPU]        [内存]        [网络延迟]       │
│  25.3%       8.2/16 GB      18 ms           │
│                        51.2%                │
├─────────────────────────────────────────────┤
│  [GPU]                                      │
│  NVIDIA GeForce RTX 3060                    │
│  GPU 15%  显存 4.2/12 GB (35.0%)            │
├─────────────────────────────────────────────┤
│  [网络速度]                                 │
│  下载  ████░░░░░░░░░░  2.5 MB/s             │
│  上传  ██░░░░░░░░░░░░  1.2 MB/s             │
│  历史最高网速：↓ 15.3 MB/s  ↑ 8.2 MB/s       │
│  累计流量：↓ 2.5 GB  ↑ 1.2 GB               │
│                         [刷新]              │
└─────────────────────────────────────────────┘
```

### 功能按钮

- **刷新** - 重置历史最高网速记录并立即刷新数据

## 构建可执行文件

使用 PyInstaller 将程序打包为独立的 Windows 可执行文件：

```bash
pyinstaller SystemMonitor.spec
```

构建完成后，可执行文件位于 `dist/SystemMonitor.exe`

### 打包配置说明

`SystemMonitor.spec` 配置要点：
- 入口文件：`system_monitor_gui.py`
- 隐藏导入：`psutil`, `customtkinter`, `darkdetect`
- 排除模块：`matplotlib`, `numpy`, `scipy`, `pandas`, `PIL`（减小体积）
- 窗口模式：无控制台窗口

## 项目结构

```
SystemMonitor/
├── system_monitor_gui.py    # GUI 主程序
├── SystemMonitor.spec       # PyInstaller 打包配置
├── .gitignore              # Git 忽略规则
├── AGENTS.md               # 开发指南
├── README.md               # 项目说明
├── build/                  # 构建临时文件（已忽略）
└── dist/                   # 编译输出（已忽略）
    └── SystemMonitor.exe   # 可执行文件
```

## 技术实现

### 核心模块

1. **NetworkSpeedMonitor 类** - 网络速度监控
   - 实时计算下载/上传速度
   - 记录历史最高速度
   - 统计累计流量

2. **MetricCard 类** - 指标卡片组件
   - 显示 CPU、内存、网络延迟、GPU 信息
   - 统一样式和布局

3. **SpeedBar 类** - 速度条组件
   - 可视化显示网络速度
   - 动态调整进度条宽度
   - 下载/上传分别用绿色/橙色显示

4. **SystemMonitorApp 类** - 主应用程序
   - 界面布局和组件管理
   - 自动刷新循环（1 秒间隔）
   - 多线程数据获取

### 数据采集

| 指标 | 来源 | 方法 |
|---|---|---|
| CPU 使用率 | psutil | `cpu_percent(interval=1)` |
| 内存使用 | psutil | `virtual_memory()` |
| GPU 使用 | pynvml | `nvmlDeviceGetUtilizationRates()` |
| 网络延迟 | subprocess | `ping` 命令 |
| 网络速度 | psutil | `net_io_counters()` |

## 常见问题

### GPU 监控不工作

1. 确认已安装 NVIDIA 显卡驱动
2. 验证 pynvml 已安装：`pip install pynvml`
3. 测试命令：`nvidia-smi`

### 打包后可执行文件无法运行

1. 确保所有依赖已安装
2. 检查 `SystemMonitor.spec` 中的 `hiddenimports`
3. 查看 `build/SystemMonitor/warn-*.txt` 获取缺失模块

### Git 提交时出现 "nul" 错误

```bash
# 删除 nul 文件
powershell -Command "Remove-Item -Path '.\nul' -Force"

# 启用 NTFS 保护
git config --global core.protectNTFS true
```

## 开发指南

详见 [AGENTS.md](AGENTS.md)，包含：
- 代码风格规范
- 导入和命名约定
- 错误处理模式
- 线程使用规范
- GUI 组件约定

## 屏幕截图

程序界面采用深色主题，主要颜色：
- 卡片背景：`#2a2a2a`
- 进度条背景：`#3a3a3a`
- 下载进度条：`#66BB6A`（绿色）
- 上传进度条：`#FF7043`（橙色）

## 许可证

MIT License

## 致谢

- [psutil](https://github.com/giampaolo/psutil) - 跨平台系统信息库
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代化 Tkinter 界面
- [PyInstaller](https://github.com/pyinstaller/pyinstaller) - Python 打包工具
