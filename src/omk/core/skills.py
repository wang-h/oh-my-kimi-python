"""
Python-native Skill System for oh-my-kimi.
Dynamically loads and executes Python-based skills from the skills directory.
"""

import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional
from omk.utils import paths

class SkillManager:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.user_skills_dir = paths.provider_user_skills_dir()
        self.project_skills_dir = paths.project_provider_skills_dir(self.project_root)

    def list_skills(self) -> List[Dict[str, Any]]:
        """List all available skills (both MD-based and PY-based)."""
        skills = []
        search_dirs = [self.project_skills_dir, self.user_skills_dir]
        
        seen_names = set()
        for d in search_dirs:
            if not d.exists():
                continue
            for skill_dir in d.iterdir():
                if skill_dir.is_dir() and skill_dir.name not in seen_names:
                    # Check for SKILL.md or main.py
                    has_md = (skill_dir / "SKILL.md").exists()
                    has_py = (skill_dir / "main.py").exists()
                    if has_md or has_py:
                        skills.append({
                            "name": skill_dir.name,
                            "path": skill_dir,
                            "type": "python" if has_py else "markdown"
                        })
                        seen_names.add(skill_dir.name)
        return skills

    def run_python_skill(self, skill_name: str, args: List[str]):
        """Load and run a skill defined in a Python file."""
        # Search in project then user dirs
        for d in [self.project_skills_dir, self.user_skills_dir]:
            py_path = d / skill_name / "main.py"
            if py_path.exists():
                # Dynamic import
                spec = importlib.util.spec_from_file_location(f"omk_skill_{skill_name}", py_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[f"omk_skill_{skill_name}"] = module
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, "run"):
                        return module.run(args)
                    else:
                        print(f"Error: Skill '{skill_name}' does not have a run() function.")
                        return
        print(f"Error: Python skill '{skill_name}' not found.")

if __name__ == "__main__":
    sm = SkillManager()
    print(f"Detected skills: {[s['name'] for s in sm.list_skills()]}")
