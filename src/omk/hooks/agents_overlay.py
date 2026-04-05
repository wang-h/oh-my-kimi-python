"""
Enhanced AGENTS.md Runtime Overlay for oh-my-kimi (Python version).
Now features a robust codebase map generator and unified instruction injection.
"""

import os
import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from omk.utils import paths

START_MARKER = "<!-- OMK:RUNTIME:START -->"
END_MARKER = "<!-- OMK:RUNTIME:END -->"

class AgentsOverlayManager:
    def __init__(self, cwd: Optional[Path] = None, session_id: Optional[str] = None):
        self.cwd = cwd or Path.cwd()
        self.session_id = session_id or "unknown"
        self.state_dir = paths.omk_state_dir(self.cwd)
        self.lock_path = self.state_dir / "agents-md.lock"

    def _acquire_lock(self, timeout_ms: int = 5000):
        self.state_dir.mkdir(parents=True, exist_ok=True)
        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout_ms:
            try:
                self.lock_path.mkdir(exist_ok=False)
                with open(self.lock_path / "owner.json", "w") as f:
                    json.dump({"pid": os.getpid(), "ts": time.time()}, f)
                return True
            except FileExistsError:
                try:
                    with open(self.lock_path / "owner.json", "r") as f:
                        data = json.load(f)
                    try:
                        os.kill(data["pid"], 0)
                    except OSError:
                        import shutil
                        shutil.rmtree(self.lock_path, ignore_errors=True)
                        continue
                except:
                    pass
                time.sleep(0.1)
        raise TimeoutError("Failed to acquire AGENTS.md lock")

    def _release_lock(self):
        import shutil
        shutil.rmtree(self.lock_path, ignore_errors=True)

    def strip_overlay(self, content: str) -> str:
        pattern = re.compile(f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", re.DOTALL)
        return pattern.sub("", content).strip()

    def generate_codebase_map(self, max_depth: int = 2) -> str:
        """Generates a structured file tree map for token-efficient exploration."""
        ignore_dirs = {".git", "node_modules", "__pycache__", "venv", ".omk", ".kimi", ".codex", "dist", "build"}
        lines = []
        
        def _walk(directory: Path, current_depth: int):
            if current_depth > max_depth:
                return
            
            try:
                # Sort: directories first, then files
                items = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name))
                for item in items:
                    if item.name in ignore_dirs or item.name.startswith("."):
                        continue
                    
                    indent = "  " * current_depth
                    if item.is_dir():
                        lines.append(f"{indent}├── {item.name}/")
                        _walk(item, current_depth + 1)
                    else:
                        lines.append(f"{indent}└── {item.name}")
            except PermissionError:
                pass

        lines.append(f"{self.cwd.name}/")
        _walk(self.cwd, 0)
        return "\n".join(lines[:50]) # Cap at 50 lines for token safety

    async def get_overlay_content(self) -> str:
        sections = []
        sections.append(f"**Session:** {self.session_id} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        cmap = self.generate_codebase_map()
        if cmap:
            sections.append(f"**Project Structure:**\n```text\n{cmap}\n```")
            
        sections.append("**Compaction Protocol:**\n- Prioritize `state_write` for critical milestones.\n- Preserve key architectural decisions in `.omk/notepad.md`.")

        body = "\n\n".join(sections)
        return f"{START_MARKER}\n<session_context>\n{body}\n</session_context>\n{END_MARKER}"

    async def write_session_scoped_agents(self) -> Path:
        """Combines all instruction sources into a single file."""
        session_dir = self.state_dir / "sessions" / self.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        session_agents_path = session_dir / "AGENTS.md"
        
        combined_parts = []
        # 1. Global (~/.kimi/AGENTS.md)
        global_agents = paths.provider_home() / "AGENTS.md"
        if global_agents.exists():
            with open(global_agents, "r", encoding="utf-8") as f:
                combined_parts.append(f"# Global Instructions\n{self.strip_overlay(f.read())}")
                
        # 2. Local (./AGENTS.md)
        local_agents = self.cwd / "AGENTS.md"
        if local_agents.exists():
            with open(local_agents, "r", encoding="utf-8") as f:
                combined_parts.append(f"# Project Instructions\n{self.strip_overlay(f.read())}")
                
        # 3. Dynamic Overlay
        overlay = await self.get_overlay_content()
        combined_parts.append(overlay)
        
        with open(session_agents_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(combined_parts))
            
        return session_agents_path
