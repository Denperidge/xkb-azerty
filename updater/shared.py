from subprocess import run, CompletedProcess
from pathlib import Path
from json import dumps

DIR_DATA_OUT = Path("data/")

def write_json(to_write: object, filename: str):
    _ = DIR_DATA_OUT.joinpath(f"{filename}.min.json").write_text(dumps(to_write))
    _ = DIR_DATA_OUT.joinpath(f"{filename}.json").write_text(dumps(to_write, indent=4))
            
def clone_or_pull_repo(repo: str, path: Path) -> CompletedProcess[bytes]:
    if not path.exists():
        cwd = path.parent
        return run(["git", "clone", repo], cwd=cwd)
    else:
        return run(["git", "pull"], cwd=path)

