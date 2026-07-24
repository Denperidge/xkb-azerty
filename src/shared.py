from subprocess import run, CompletedProcess
from pathlib import Path

def clone_or_pull_repo(repo: str, path: Path) -> CompletedProcess[bytes]:
    if not path.exists():
        cwd = path.parent
        return run(["git", "clone", repo], cwd=cwd)
    else:
        return run(["git", "pull"], cwd=path)


