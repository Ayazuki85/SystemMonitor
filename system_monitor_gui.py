import psutil
import platform
import subprocess
import re
import threading
import time
import sys
import os

import customtkinter as ctk

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = os.path.dirname(sys.executable) + os.pathsep + os.environ['PATH']

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FONT_TITLE = ("SimHei", 13, "bold")
FONT_BODY = ("SimSun", 13, "bold")
FONT_ENGLISH = ("Times New Roman", 12)
FONT_SMALL = ("SimSun", 10)


class NetworkSpeedMonitor:
    def __init__(self):
        self.last_net = psutil.net_io_counters()
        self.last_time = time.time()
        self.max_download = 0
        self.max_upload = 0
    
    def get_speed(self):
        current_net = psutil.net_io_counters()
        current_time = time.time()
        
        time_diff = current_time - self.last_time
        if time_diff == 0:
            time_diff = 0.1
        
        bytes_sent = (current_net.bytes_sent - self.last_net.bytes_sent) / time_diff
        bytes_recv = (current_net.bytes_recv - self.last_net.bytes_recv) / time_diff
        
        if bytes_recv > self.max_download:
            self.max_download = bytes_recv
        if bytes_sent > self.max_upload:
            self.max_upload = bytes_sent
        
        def format_size(size):
            if size >= 1024 ** 3:
                return f"{size / (1024 ** 3):.2f} GB/s"
            elif size >= 1024 ** 2:
                return f"{size / (1024 ** 2):.2f} MB/s"
            elif size >= 1024:
                return f"{size / 1024:.2f} KB/s"
            return f"{size:.0f} B/s"
        
        self.last_net = current_net
        self.last_time = current_time
        
        return {
            'download_speed': format_size(bytes_recv),
            'upload_speed': format_size(bytes_sent),
            'total_download': format_size(current_net.bytes_recv).replace('/s', ''),
            'total_upload': format_size(current_net.bytes_sent).replace('/s', ''),
            'max_download': format_size(self.max_download).replace('/s', ''),
            'max_upload': format_size(self.max_upload).replace('/s', '')
        }
    
    def reset_max(self):
        self.max_download = 0
        self.max_upload = 0

network_monitor = NetworkSpeedMonitor()

def get_network_speed():
    return network_monitor.get_speed()


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    mem = psutil.virtual_memory()
    return {
        'total': round(mem.total / (1024 ** 3), 2),
        'used': round(mem.used / (1024 ** 3), 2),
        'percent': mem.percent
    }


def get_gpu_usage():
    try:
        import pynvml
        import warnings
        warnings.filterwarnings('ignore', category=FutureWarning)
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        gpus = []
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            mem_total = int(memory.total)
            mem_used = int(memory.used)
            gpus.append({
                'name': name,
                'gpu_percent': utilization.gpu,
                'memory_total': round(mem_total / (1024 ** 3), 2),
                'memory_used': round(mem_used / (1024 ** 3), 2),
                'memory_percent': round(mem_used / mem_total * 100, 2) if mem_total > 0 else 0
            })
        pynvml.nvmlShutdown()
        return gpus
    except ImportError:
        return "pynvml 未安装"
    except Exception as e:
        return f"获取失败：{str(e)}"


def get_network_latency(host="www.baidu.com"):
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', host]
        if platform.system().lower() == 'windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.run(command, capture_output=True, text=True, timeout=5, 
                                   encoding='gbk', errors='ignore', 
                                   startupinfo=startupinfo, 
                                   creationflags=subprocess.CREATE_NO_WINDOW).stdout
        else:
            output = subprocess.run(command, capture_output=True, text=True, timeout=5).stdout
        match = re.search(r'(?:Average|平均)\s*=\s*(\d+)ms', output, re.IGNORECASE)
        if not match:
            match = re.search(r'time[=<](\d+)ms', output, re.IGNORECASE)
        if match:
            return f"{match.group(1)} ms"
        return "无法解析"
    except Exception as e:
        return f"失败：{str(e)}"


class MetricCard(ctk.CTkFrame):
    def __init__(self, parent, title, width=145, height=55):
        super().__init__(parent, fg_color="#2a2a2a", corner_radius=4, width=width, height=height)
        self.pack_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            self, 
            text=title, 
            font=FONT_TITLE,
            text_color="#aaaaaa",
            anchor="w"
        )
        self.title_label.place(x=6, y=2)
        
        self.value_label = ctk.CTkLabel(
            self,
            text="--",
            font=FONT_BODY,
            text_color="#ffffff",
            anchor="w",
            justify="left"
        )
        self.value_label.place(x=6, y=24)
    
    def update_value(self, value):
        self.value_label.configure(text=value)


class SpeedBar(ctk.CTkFrame):
    def __init__(self, parent, label, max_width=120):
        super().__init__(parent, fg_color="transparent")
        
        self.label = ctk.CTkLabel(
            self,
            text=label,
            font=FONT_SMALL,
            text_color="#999999",
            width=30,
            anchor="w"
        )
        self.label.pack(side="left", padx=(0, 3))
        
        self.bar_frame = ctk.CTkFrame(self, fg_color="#3a3a3a", corner_radius=2, height=16, width=max_width)
        self.bar_frame.pack(side="left", fill="x", expand=True)
        
        self.bar = ctk.CTkFrame(self.bar_frame, fg_color="#4CAF50", corner_radius=2, height=14, width=0)
        self.bar.place(y=1, x=1)
        
        self.value_label = ctk.CTkLabel(
            self,
            text="0 B/s",
            font=FONT_ENGLISH,
            text_color="#ffffff",
            width=70,
            anchor="e"
        )
        self.value_label.pack(side="right", padx=(3, 0))
        
        self.max_speed = 1024 * 1024
    
    def update_speed(self, bytes_per_sec, is_upload=False):
        self.value_label.configure(text=self._format_speed(bytes_per_sec))
        
        if bytes_per_sec > self.max_speed:
            self.max_speed = bytes_per_sec * 1.5
        
        if self.max_speed > 0:
            percent = min(bytes_per_sec / self.max_speed, 1.0)
            bar_width = int(120 * percent)
            self.bar.configure(width=max(bar_width, 2))
            
            if is_upload:
                self.bar.configure(fg_color="#FF7043")
            else:
                self.bar.configure(fg_color="#66BB6A")
    
    def _format_speed(self, size):
        if size >= 1024 ** 3:
            return f"{size / (1024 ** 3):.2f} GB/s"
        elif size >= 1024 ** 2:
            return f"{size / (1024 ** 2):.2f} MB/s"
        elif size >= 1024:
            return f"{size / 1024:.2f} KB/s"
        return f"{size:.0f} B/s"
    
    def reset_max(self):
        self.max_speed = 1024 * 1024


class SystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("系统资源监控")
        self.root.geometry("460x280")
        self.root.minsize(440, 260)
        
        main_frame = ctk.CTkFrame(root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=6, pady=4)
        
        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 4))
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure(2, weight=1)
        
        self.cpu_card = MetricCard(top_frame, "CPU", width=145, height=50)
        self.cpu_card.grid(row=0, column=0, padx=(0, 2), sticky="ew")
        
        self.memory_card = MetricCard(top_frame, "内存", width=145, height=50)
        self.memory_card.grid(row=0, column=1, padx=2, sticky="ew")
        
        self.network_card = MetricCard(top_frame, "网络延迟", width=145, height=50)
        self.network_card.grid(row=0, column=2, padx=(2, 0), sticky="ew")
        
        self.gpu_card = MetricCard(main_frame, "GPU", width=452, height=65)
        self.gpu_card.pack(fill="x", pady=(0, 4))
        
        speed_frame = ctk.CTkFrame(main_frame, fg_color="#2a2a2a", corner_radius=4, height=135)
        speed_frame.pack(fill="x", pady=(0, 4))
        speed_frame.pack_propagate(False)
        
        speed_title = ctk.CTkLabel(
            speed_frame,
            text="网络速度",
            font=FONT_TITLE,
            text_color="#aaaaaa",
            anchor="w"
        )
        speed_title.place(x=6, y=4)
        
        self.download_bar = SpeedBar(speed_frame, "下载", max_width=120)
        self.download_bar.place(x=6, y=28)
        
        self.upload_bar = SpeedBar(speed_frame, "上传", max_width=120)
        self.upload_bar.place(x=6, y=54)
        
        self.max_speed_label = ctk.CTkLabel(
            speed_frame,
            text="历史最高网速：↓ --  ↑ --",
            font=FONT_BODY,
            text_color="#999999",
            anchor="w"
        )
        self.max_speed_label.place(x=6, y=82)
        
        self.total_label = ctk.CTkLabel(
            speed_frame,
            text="累计流量：↓ --  ↑ --",
            font=FONT_BODY,
            text_color="#999999",
            anchor="w"
        )
        self.total_label.place(x=6, y=106)
        
        self.update_data()
        self.auto_refresh_loop()
    
    def update_data(self):
        def task():
            cpu = get_cpu_usage()
            memory = get_memory_usage()
            gpu = get_gpu_usage()
            latency = get_network_latency()
            network_speed = get_network_speed()
            
            self.root.after(0, lambda: self.display_data(cpu, memory, gpu, latency, network_speed))
        
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
    
    def display_data(self, cpu, memory, gpu, latency, network_speed):
        self.cpu_card.update_value(f"{cpu:.1f}%")
        self.memory_card.update_value(f"{memory['used']}/{memory['total']} GB\n{memory['percent']:.1f}%")
        self.network_card.update_value(f"{latency}")
        
        if isinstance(gpu, list):
            gpu_texts = []
            for g in gpu:
                gpu_texts.append(f"{g['name']}")
                gpu_texts.append(f"GPU {g['gpu_percent']}%  显存 {g['memory_used']:.2f}/{g['memory_total']:.2f} GB ({g['memory_percent']:.1f}%)")
            self.gpu_card.update_value("\n".join(gpu_texts))
        else:
            self.gpu_card.update_value(gpu)
        
        self.download_bar.update_speed(
            float(network_speed['download_speed'].split()[0]) * self._get_unit_multiplier(network_speed['download_speed']),
            is_upload=False
        )
        self.upload_bar.update_speed(
            float(network_speed['upload_speed'].split()[0]) * self._get_unit_multiplier(network_speed['upload_speed']),
            is_upload=True
        )
        
        self.max_speed_label.configure(
            text=f"历史最高网速：↓ {network_speed['max_download']}  ↑ {network_speed['max_upload']}"
        )
        
        self.total_label.configure(
            text=f"累计流量：↓ {network_speed['total_download']}  ↑ {network_speed['total_upload']}"
        )
    
    def _get_unit_multiplier(self, speed_str):
        if "GB/s" in speed_str:
            return 1024 ** 3
        elif "MB/s" in speed_str:
            return 1024 ** 2
        elif "KB/s" in speed_str:
            return 1024
        return 1
    
    def auto_refresh_loop(self):
        self.update_data()
        self.root.after(1000, self.auto_refresh_loop)


def main():
    root = ctk.CTk()
    app = SystemMonitorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
