"""
Head-Up Display (HUD) for oh-my-kimi (Python version).
Uses rich.live to provide a real-time monitoring dashboard in the terminal.
"""

import time
import json
from pathlib import Path
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from omk.utils import paths

class HUD:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.state_dir = paths.omk_state_dir(self.project_root)

    def generate_status_table(self) -> Table:
        table = Table(expand=True, box=None)
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Task", style="magenta")
        table.add_column("Progress", style="yellow")

        # Mock data for now - will read from self.state_dir in future
        table.add_row("Leader", "Thinking...", "Overall Orchestration", "45%")
        table.add_row("Worker-1", "Idle", "Code Review", "Done")
        table.add_row("Worker-2", "Running", "Unit Testing", "12%")
        
        return table

    def make_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=1),
            Layout(name="body"),
            Layout(name="footer", size=1)
        )
        
        layout["header"].update(Text(" OMK Head-Up Display (v0.1.0) ", style="bold white on blue", justify="center"))
        layout["body"].update(Panel(self.generate_status_table(), title="Active Agents", border_style="bright_blue"))
        layout["footer"].update(Text(f" Project: {self.project_root}  |  Press Ctrl+C to exit", style="dim", justify="center"))
        
        return layout

    def start(self, watch: bool = False):
        """Start the HUD loop."""
        layout = self.make_layout()
        
        with Live(layout, refresh_per_second=4, screen=watch) as live:
            try:
                while True:
                    # In watch mode, we refresh from state files
                    if watch:
                        layout["body"].update(Panel(self.generate_status_table(), title="Active Agents", border_style="bright_blue"))
                    time.sleep(0.5)
            except KeyboardInterrupt:
                pass

if __name__ == "__main__":
    import sys
    from typing import Optional
    hud = HUD()
    hud.start(watch="--watch" in sys.argv)
