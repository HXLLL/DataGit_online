import os
from storage import storage
from repo import Repo
from stage import Stage
from version import Version


def trans_path(dir: str) -> str:
    res = ''
    if os.path.isabs(dir):
        res = os.path.normpath(dir)
    else:
        res = os.path.normpath(os.path.join(os.getcwd(), dir))
    while res[:-1] == '.' or res[:-1] == '/':
        res = res[:-1]
    return res


def init() -> None:
    repo = Repo()
    repo.init()
    storage.save_repo(repo)

    stage = Stage()
    storage.save_stage(stage)


def update(dir: str) -> None:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")

    dir = trans_path(dir)
    if not os.path.exists(dir):
        raise ValueError("datagit update <dir>: <dir> should exist")
    if not os.path.isdir(dir):
        raise ValueError("datagit update <dir>: <dir> should lead to a dir")
    if repo.is_detached_head():
        raise ValueError("Cannot update in detatched HEAD mode")
    stage.update(dir)

    storage.save_repo(repo)
    storage.save_stage(stage)


def add(src: str, dst: str) -> None:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")

    src = trans_path(src)
    dst = trans_path(dst)
    if not os.path.exists(src):
        raise ValueError("datagit add <src> <dst>: <src> should exist")
    if not os.path.isdir(src):
        raise ValueError("datagit add <src> <dst>: <src> should lead to dir")
    if repo.is_detached_head():
        raise ValueError("Cannot update in detatched HEAD mode")
    stage.add(src, dst)

    storage.save_repo(repo)
    storage.save_stage(stage)


def transform(dir1: str, entry: str, msg: str, is_map: bool, dir2: str) -> None:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")

    dir1 = trans_path(dir1)
    dir2 = trans_path(dir2)
    if not (os.path.exists(dir1) and os.path.exists(dir2)):
        raise ValueError("datagit transform <dir1> <entry> -m <msg> [-s] [-d <dir2>]: <dir1> <dir2> should exist")
    if not (os.path.isdir(dir1) and os.path.isdir(dir2)):
        raise ValueError(
            "datagit transform <dir1> <entry> -m <msg> [-s] [-d <dir2>]: <dir1> <dir2> should lead to a dir")
    if os.path.isabs(entry):
        raise ValueError("datagit transform <dir1> <entry> -m <msg> [-s] [-d <dir2>]: <entry> should be relative path")

    entry_file = os.path.join(dir1, entry)

    if not os.path.exists(entry_file):
        raise ValueError("datagit transform <dir1> <entry> -m <msg> [-s] [-d <dir2>]: <entry> should exist")
    if not os.path.isfile(entry_file):
        raise ValueError("datagit transform <dir1> <entry> -m <msg> [-s] [-d <dir2>]: <entry> should lead to a file")

    if repo.is_detached_head():
        raise ValueError("Cannot transform in detatched HEAD mode")

    stage.transform(dir1, entry, is_map, dir2, msg)

    storage.save_repo(repo)
    storage.save_stage(stage)


def commit(msg: str) -> None:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")

    if stage.empty():
        raise ValueError("Nothing to commit")

    repo.commit(stage, msg)

    storage.save_repo(repo)
    storage.save_stage(stage)


def checkout_v(obj: int) -> None:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")

    repo.checkout(obj, False)
    stage.reset()

    storage.save_repo(repo)
    storage.save_stage(stage)


def checkout_b(obj: str) -> None:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")

    repo.checkout(obj, True)
    stage.reset()

    storage.save_repo(repo)
    storage.save_stage(stage)


def save(obj: int) -> None:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")

    repo.save(obj)

    storage.save_repo(repo)
    storage.save_stage(stage)


def unsave(obj: int) -> None:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")

    repo.unsave(obj)

    storage.save_repo(repo)
    storage.save_stage(stage)


def adjust() -> None:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")

    repo.adjust()

    storage.save_repo(repo)
    storage.save_stage(stage)


def log() -> str:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")

    log_info = repo.log()

    storage.save_repo(repo)
    storage.save_stage(stage)
    return log_info


def status() -> str:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")

    status_info = repo.status()

    storage.save_repo(repo)
    storage.save_stage(stage)
    return status_info


def branch(name: str) -> None:
    repo = storage.load_repo()
    stage = storage.load_stage()

    if repo is None or stage is None:
        raise ValueError("Not in a valid repository")
    if len(name) > 255:
        raise ValueError("Branch name too long")

    repo.branch(name)

    storage.save_repo(repo)
    storage.save_stage(stage)
