"""
AGENTS.md Runtime Overlay for oh-my-kimi (Python version).
Dynamically injects session-specific context into AGENTS.md before Kimi launches.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from omk.utils import paths

START_MARKER = "<!-- OMK:RUNTIME:START -->"
END_MARKER = "<!-- OMK:RUNTIME:END -->"
MAX_OVERLAY_SIZE = 3500

class AgentsOverlayManager:
    def __init__(self, cwd: Optional[Path] = None, session_id: Optional[str] = None):
        self.cwd = cwd or Path.cwd()
        self.session_id = session_id or "unknown"
        self.state_dir = paths.omk_state_dir(self.cwd)
        self.lock_path = self.state_dir / "agents-md.lock"

    def _acquire_lock(self, timeout_ms: int = 5000):
        """Simple directory-based lock implementation."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        start_time = time.time()
        while (time.time() - start_time) * 1000 < timeout_ms:
            try:
                self.lock_path.mkdir(exist_ok=False)
                # Write owner info
                with open(self.lock_path / "owner.json", "w") as f:
                    json.dump({"pid": os.getpid(), "ts": time.time()}, f)
                return True
            except FileExistsError:
                # Check if stale
                try:
                    with open(self.lock_path / "owner.json", "r") as f:
                        data = json.load(f)
                    # Simple PID check
                    try:
                        os.kill(data["pid"], 0)
                    except OSError:
                        # Process dead, remove stale lock
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
        """Remove existing overlay content bounded by markers."""
        import re
        pattern = re.compile(f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", re.DOTALL)
        return pattern.sub("", content).strip()

    def generate_codebase_map(self) -> str:
        """WIP: Generate a simple tree-like map of the codebase."""
        # For now, just a placeholder or very shallow list
        try:
            items = [p.name for p in self.cwd.glob("*") if not p.name.startswith(".")][:20]
            return "\n".join([f"- {i}" for i in items])
        except:
            return ""

    async def get_overlay_content(self) -> str:
        """Assemble the actual overlay text."""
        sections = []
        
        # Session Metadata
        sections.append(f"**Session:** {self.session_id} | {datetime.now().isoformat()}")
        
        # Codebase Map
        cmap = self.generate_codebase_map()
        if cmap:
            sections.append(f"**Codebase Map:**\n{cmap}")
            
        # Project Memory (Placeholder)
        sections.append("**Compaction Protocol:**\n1. Checkpoint state via state_write\n2. Save key decisions to notepad")

        body = "\n\n".join(sections)
        prefix = f"{START_MARKER}\n<session_context>\n"
        suffix = f"\n</session_context>\n{END_MARKER}"
        
        return f"{prefix}{body}{suffix}"

    async def apply(self, agents_md_path: Path):
        """Apply overlay to the given AGENTS.md file."""
        self._acquire_lock()
        try:
            content = ""
            if agents_md_path.exists():
                with open(agents_md_path, "r", encoding="utf-8") as f:
                    content = f.read()
            
            clean_content = self.strip_overlay(content)
            overlay = await self.get_overlay_content()
            
            new_content = clean_content + "\n\n" + overlay + "\n"
            with open(agents_md_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        finally:
            self._release_lock()

    async def write_session_scoped_agents(self) -> Path:
        """
        Combines global (~/.kimi/AGENTS.md) and local (./AGENTS.md) 
        into a session-scoped file in .omk/state/sessions/<id>/AGENTS.md
        """
        session_dir = self.state_dir / "sessions" / self.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        session_agents_path = session_dir / "AGENTS.md"
        
        combined_parts = []
        # 1. Global
        global_agents = paths.provider_home() / "AGENTS.md"
        if global_agents.exists():
            with open(global_agents, "r", encoding="utf-8") as f:
                combined_parts.append(self.strip_overlay(f.read()))
                
        # 2. Local
        local_agents = self.cwd / "AGENTS.md"
        if local_agents.exists():
            with open(local_agents, "r", encoding="utf-8") as f:
                combined_parts.append(self.strip_overlay(f.read()))
                
        # 3. Overlay
        overlay = await self.get_overlay_content()
        combined_parts.append(overlay)
        
        with open(session_agents_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(combined_parts))
            
        return session_agents_path
