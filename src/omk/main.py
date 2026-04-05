import typer
import asyncio
from rich.console import Console
from rich.table import Table
from omk.utils import paths
from omk.core.launch import launch_kimi

app = typer.Typer(
    help="oh-my-kimi Python: The Orchestrator for Kimi Code CLI",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

@app.command()
def info():
    """Display OMK environment information."""
    table = Table(title="oh-my-kimi (Python) Environment")
    table.add_column("Property", style="cyan")
    table.add_column("Path", style="magenta")

    table.add_row("Provider Home", str(paths.provider_home()))
    table.add_row("Config Path", str(paths.provider_config_path()))
    table.add_row("User Skills", str(paths.provider_user_skills_dir()))
    table.add_row("Project Root", str(paths.project_provider_root_dir()))
    table.add_row("OMK State", str(paths.omk_state_dir()))

    console.print(table)

@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def ask(
    ctx: typer.Context,
    prompt: str = typer.Argument(None, help="The prompt to ask Kimi")
):
    """Start a single-turn or interactive session with Kimi."""
    args = []
    if prompt:
        args.append(prompt)
    args.extend(ctx.args)
    
    asyncio.run(launch_kimi(args))

@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def exec(
    ctx: typer.Context,
    cmd: str = typer.Argument(..., help="The command to execute via Kimi")
):
    """Run kimi/codex-compatible exec non-interactively with OMK AGENTS/overlay injection."""
    args = ["exec", cmd]
    args.extend(ctx.args)
    
    asyncio.run(launch_kimi(args))

@app.command()
def team(
    workers: int = typer.Option(3, "--workers", "-w", help="Number of worker agents"),
    task: str = typer.Argument(..., help="Task for the team")
):
    """Launch a multi-agent team in tmux."""
    from omk.utils.tmux_manager import TmuxManager
    
    try:
        mgr = TmuxManager()
        mgr.ensure_in_tmux()
        
        console.print(f"[bold blue]OMK Team[/bold blue] Orchestrating {workers} workers for: [italic]'{task}'[/italic]")
        
        # This will now correctly initialize panes with 'omk ask'
        mgr.create_team_layout(worker_count=workers, task=task)
        
        console.print("[bold green]Success:[/bold green] Team environment is live. Check the other panes!")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def hud(
    watch: bool = typer.Option(False, "--watch", help="Enable continuous monitoring mode")
):
    """Launch the Head-Up Display monitoring terminal."""
    from omk.core.hud import HUD
    hud_obj = HUD()
    hud_obj.start(watch=watch)

@app.command()
def setup():
    """Automated installation and scope configuration."""
    console.print("[bold yellow]Setup:[/bold yellow] Your Python OMK is already configured to use ~/.kimi")
    console.print("Run 'omk info' to verify paths.")

if __name__ == "__main__":
    app()
