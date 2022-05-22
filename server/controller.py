import os
from storage import storage
from repo import Repo
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

def checkout_v(obj: int) -> None:
    repo = storage.load_repo()

    if repo is None:
        raise ValueError("Not in a valid repository")

    repo.checkout(obj, False)

    storage.save_repo(repo)


def checkout_b(obj: str) -> None:
    repo = storage.load_repo()

    if repo is None:
        raise ValueError("Not in a valid repository")

    repo.checkout(obj, True)

    storage.save_repo(repo)


def save(obj: int) -> None:
    repo = storage.load_repo()

    if repo is None:
        raise ValueError("Not in a valid repository")

    repo.save(obj)

    storage.save_repo(repo)


def unsave(obj: int) -> None:
    repo = storage.load_repo()

    if repo is None:
        raise ValueError("Not in a valid repository")

    repo.unsave(obj)

    storage.save_repo(repo)


def adjust() -> None:
    repo = storage.load_repo()

    if repo is None:
        raise ValueError("Not in a valid repository")

    repo.adjust()

    storage.save_repo(repo)


def log() -> str:
    repo = storage.load_repo()

    if repo is None:
        raise ValueError("Not in a valid repository")

    log_info = repo.log()

    storage.save_repo(repo)
    return log_info


def get_repo(a: bool, name: str) -> str:
    if a:
        all_repo = storage.get_repo_name()
        return all_repo
    else:
        repo = storage.find_repo(name)
        repo_info = repo.get_info()
        return repo_info


def create(name: str) -> None:
    repo = Repo()
    storage.create_repo(name)
    storage.save_repo(name, repo)


def fork(old_name: str, new_name: str) -> None:
    storage.copy_repo(old_name, new_name)
    repo = storage.find_repo(new_name)
    repo.parent_id_init(old_name)
    storage.save_repo(new_name, repo)

def diff_version(repo_name:str, version_list:str):
    repo = storage.load_repo(repo_name)
    return repo.comp(version_list)

