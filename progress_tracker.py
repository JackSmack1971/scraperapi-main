from time import time
from typing import Any, Dict, Optional

from kivy.clock import mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar

from utils import sanitize_url


class ScrapingProgressTracker(BoxLayout):
    """Thread-safe progress tracker for URL scraping."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(orientation="vertical", **kwargs)
        self.url_widgets: Dict[str, Dict[str, Any]] = {}
        self.total_urls = 0
        self.completed_urls = 0
        self.start_time = time()
        # Overall stats widgets
        self.progress_bar = ProgressBar(max=100)
        self.stats_label = Label(text="Progress: 0% | Speed: 0 URL/min | ETA: --")
        self.add_widget(self.progress_bar)
        self.add_widget(self.stats_label)

    @mainthread
    def add_url(self, url: str) -> None:
        """Register a new URL for tracking."""
        sanitized = sanitize_url(url)  # Security: remove control chars from URL
        if sanitized in self.url_widgets:
            return
        layout = BoxLayout(orientation="horizontal")
        status_label = Label(text="Queued")
        progress_label = Label(text="0%")
        layout.add_widget(Label(text=sanitized))
        layout.add_widget(status_label)
        layout.add_widget(progress_label)
        self.add_widget(layout)
        self.url_widgets[sanitized] = {
            "layout": layout,
            "status": status_label,
            "progress": progress_label,
            "start_time": time(),
            "finished": False,
        }
        self.total_urls += 1
        self._update_overall_display()

    @mainthread
    def update_url_progress(
        self, url: str, status: str, message: str = "", data_size: Optional[int] = None
    ) -> None:
        """Update UI for a specific URL."""
        sanitized = sanitize_url(url)
        if sanitized not in self.url_widgets:
            return  # Unknown URL; ignore silently
        widgets = self.url_widgets[sanitized]
        widgets["status"].text = status
        if data_size is not None:
            widgets["progress"].text = f"{data_size}B"
        if status in {"completed", "failed"} and not widgets["finished"]:
            widgets["finished"] = True
            self.completed_urls += 1
        if message:
            widgets["progress"].text = sanitize_url(message)
        self._update_overall_display()

    @mainthread
    def _update_overall_display(self) -> None:
        """Recompute and update global statistics."""
        if self.total_urls == 0:
            return
        completion_pct = int((self.completed_urls / self.total_urls) * 100)
        elapsed = max(time() - self.start_time, 1)
        speed = (self.completed_urls / elapsed) * 60  # URLs per minute
        remaining = self.total_urls - self.completed_urls
        eta = (remaining / speed) if speed else float("inf")
        self.progress_bar.value = completion_pct
        eta_text = f"{eta:.1f} sec" if speed else "--"
        self.stats_label.text = (
            f"Progress: {completion_pct}% | "
            f"Speed: {speed:.1f} URL/min | "
            f"ETA: {eta_text}"
        )
