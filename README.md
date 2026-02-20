# 系统资源监控器 (System Monitor)

一个基于 Python 的 Windows 系统资源监控工具，采用现代化深色主题 GUI，实时显示 CPU、内存、GPU 和网络使用情况。

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 功能特性

- **CPU 监控** - 实时显示 CPU 使用率
- **内存监控** - 显示内存使用量、总量和使用百分比
- **GPU 监控** - 支持 NVIDIA GPU 使用率和显存监控
- **网络延迟** - 实时测试网络延迟（ping 值）
- **网络速度** - 实时下载/上传速度，带可视化进度条
- **流量统计** - 累计流量和历史最高网速记录
- **自动刷新** - 每秒自动更新数据
- **深色主题** - 现代化深色界面，护眼舒适

## 系统要求

- Windows 10 或更高版本
- Python 3.7 或更高版本
- NVIDIA GPU（可选，用于 GPU 监控）

## 安装

### 1. 克隆或下载项目

```bash
git clone https://github.com/Ayazuki85/SystemMonitor.git
cd SystemMonitor
```

### 2. 安装依赖

```bash
pip install psutil customtkinter pynvml pyinstaller darkdetect
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

### 直接运行

```bash
python system_monitor_gui.py
```

### 界面布局

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
└─────────────────────────────────────────────┘
```

### 监控指标说明

| 指标 | 说明 | 更新频率 |
|---|---|---|
| CPU | 处理器使用率百分比 | 1 秒 |
| 内存 | 已用/总量 GB + 百分比 | 1 秒 |
| GPU | 显卡使用率 + 显存占用 | 1 秒 |
| 网络延迟 | Ping 百度服务器的延迟 | 1 秒 |
| 下载速度 | 实时网络下载速率 | 1 秒 |
| 上传速度 | 实时网络上传速率 | 1 秒 |
| 历史最高网速 |  session 内最高速度记录 | 实时更新 |
| 累计流量 | 网卡启动至今的总流量 | 实时更新 |

## 构建可执行文件

使用 PyInstaller 将程序打包为独立的 Windows 可执行文件：

```bash
python -m PyInstaller SystemMonitor.spec --clean --noconfirm
```

构建完成后，可执行文件位于 `dist\SystemMonitor.exe`

### 打包配置说明

`SystemMonitor.spec` 配置要点：
- 入口文件：`system_monitor_gui.py`
- 隐藏导入：`psutil`, `customtkinter`, `darkdetect`
- 排除模块：`matplotlib`, `numpy`, `scipy`, `pandas`, `PIL`（减小体积）
- 窗口模式：无控制台窗口
- 图标：`mouse_icon.ico`

### 更换图标

1. 准备 `.ico` 文件（建议包含多尺寸：16x16, 32x32, 64x64, 128x128, 256x256）
2. 修改 `SystemMonitor.spec` 中的 `icon='xxx.ico'`
3. 重新打包

## 项目结构

```
SystemMonitor/
├── system_monitor_gui.py    # GUI 主程序
├── SystemMonitor.spec       # PyInstaller 打包配置
├── mouse_icon.ico           # 程序图标
├── .gitignore              # Git 忽略规则
├── AGENTS.md               # 开发指南
├── README.md               # 项目说明
├── build/                  # 构建临时文件（已忽略）
└── dist/                   # 编译输出（已忽略）
    └── SystemMonitor.exe   # 可执行文件
```

## 技术实现

### 核心组件

1. **NetworkSpeedMonitor 类** - 网络速度监控
   - 实时计算下载/上传速度
   - 记录历史最高速度
   - 统计累计流量

2. **MetricCard 类** - 指标卡片组件
   - 显示 CPU、内存、网络延迟、GPU 信息
   - 统一样式和布局（宽 145px，高 50px）

3. **SpeedBar 类** - 速度条组件
   - 可视化显示网络速度
   - 动态调整进度条宽度
   - 下载绿色（#66BB6A）/上传橙色（#FF7043）

4. **SystemMonitorApp 类** - 主应用程序
   - 界面布局和组件管理
   - 自动刷新循环（1 秒间隔）
   - 多线程数据获取（避免阻塞 UI）

### 数据采集方式

| 指标 | 来源 | 方法 |
|---|---|---|
| CPU 使用率 | psutil | `cpu_percent(interval=1)` |
| 内存使用 | psutil | `virtual_memory()` |
| GPU 使用 | pynvml | `nvmlDeviceGetUtilizationRates()` |
| 网络延迟 | subprocess | `ping` 命令 |
| 网络速度 | psutil | `net_io_counters()` |

### 界面颜色方案

| 元素 | 颜色代码 | 说明 |
|---|---|---|
| 卡片背景 | #2a2a2a | 深灰色 |
| 进度条背景 | #3a3a3a | 中灰色 |
| 下载进度条 | #66BB6A | 绿色 |
| 上传进度条 | #FF7043 | 橙色 |
| 标题文字 | #aaaaaa | 浅灰色 |
| 数值文字 | #ffffff | 白色 |
| 小字 | #999999 | 深灰色 |

## 常见问题

### GPU 监控不工作

1. 确认已安装 NVIDIA 显卡驱动
2. 验证 pynvml 已安装：`pip install pynvml`
3. 测试命令：`nvidia-smi`
4. 如使用 AMD/Intel 显卡，当前版本会显示提示信息

### 打包后可执行文件无法运行

1. 确保所有依赖已安装
2. 检查 `SystemMonitor.spec` 中的 `hiddenimports`
3. 查看 `build/SystemMonitor/warn-*.txt` 获取缺失模块
4. 尝试使用 `--clean` 参数重新打包

### 中文显示乱码

确保系统已安装中文字体：
- SimHei（黑体）- 标题
- SimSun（宋体）- 正文

### 网络延迟显示"无法解析"

1. 检查网络连接是否正常
2. 确认防火墙未阻止 ping 命令
3. 可修改代码中的测试主机（默认 www.baidu.com）

## 开发指南

详见 [AGENTS.md](AGENTS.md)，包含：
- 代码风格规范
- 导入和命名约定
- 错误处理模式
- 线程使用规范
- GUI 组件约定

## 版本历史

- 当前版本：1.0
- 主要功能：CPU、内存、GPU、网络监控
- 打包优化：排除不必要的库以减小体积

## 许可证

MIT License

## 致谢

- [psutil](https://github.com/giampaolo/psutil) 
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) 
- [PyInstaller](https://github.com/pyinstaller/pyinstaller) 
- [PyNVML](https://github.com/gpuopenanalytics/pynvml)
- [opencode](https://github.com/anomalyco/opencode)