import tkinter as tk
from tkinter import ttk
import matplotlib

matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Dict, Any
import time
from collections import deque


class CrawlerVisualization(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_plots()

        self.timestamps = deque(maxlen=100)
        self.crawl_speeds = deque(maxlen=100)
        self.memory_usage = deque(maxlen=100)
        self.urls_queue = deque(maxlen=100)

        self.start_time = time.time()

    def setup_plots(self):
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.figure.subplots_adjust(hspace=0.4)

        self.speed_plot = self.figure.add_subplot(311)
        self.speed_plot.set_title('Crawl Speed')
        self.speed_plot.set_ylabel('Pages/min')
        self.speed_line, = self.speed_plot.plot([], [])

        self.memory_plot = self.figure.add_subplot(312)
        self.memory_plot.set_title('Memory Usage')
        self.memory_plot.set_ylabel('MB')
        self.memory_line, = self.memory_plot.plot([], [])

        self.queue_plot = self.figure.add_subplot(313)
        self.queue_plot.set_title('URLs in Queue')
        self.queue_plot.set_ylabel('Count')
        self.queue_line, = self.queue_plot.plot([], [])

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_plots(self, stats: Dict[str, Any]) -> None:
        current_time = time.time() - self.start_time
        self.timestamps.append(current_time)

        self.crawl_speeds.append(stats['crawl_speed'])
        self.memory_usage.append(stats['memory_usage'])
        self.urls_queue.append(stats['urls_in_queue'])

        self.speed_line.set_data(list(self.timestamps), list(self.crawl_speeds))
        self.memory_line.set_data(list(self.timestamps), list(self.memory_usage))
        self.queue_line.set_data(list(self.timestamps), list(self.urls_queue))

        for plot in [self.speed_plot, self.memory_plot, self.queue_plot]:
            plot.relim()
            plot.autoscale_view()

        self.canvas.draw()

    def reset(self):
        self.timestamps.clear()
        self.crawl_speeds.clear()
        self.memory_usage.clear()
        self.urls_queue.clear()
        self.start_time = time.time()
