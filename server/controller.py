import os
from typing import List

from core.types import VersionID
from server.storage import storage
from server.repo import Repo
from server.version import Version


def trans_path(dir: str) -> str:
    res = ''
    if os.path.isabs(dir):
        res = os.path.normpath(dir)
    else:
        res = os.path.normpath(os.path.join(os.getcwd(), dir))
    while res[:-1] == '.' or res[:-1] == '/':
        res = res[:-1]
    return res


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
        repo = storage.load_repo(name)
        repo_info = repo.get_info()
        return repo_info


def create(name: str, key_path: str) -> None:
    if storage.exist_repo(name):
        raise ValueError("repository already exists")
    repo = Repo()
    storage.create_repo(name)
    storage.save_repo(name, repo)
    storage.save_public_key(name, key_path)


def fork(old_name: str, new_name: str, key_path: str) -> None:
    if not storage.exist_repo(old_name):
        raise ValueError("src repository doesn't exist")
    if storage.exist_repo(new_name):
        raise ValueError("dst repository already exists")
    storage.copy_repo(old_name, new_name)
    repo = storage.load_repo(new_name)
    repo.parent_id_init(old_name)
    storage.save_repo(new_name, repo)
    storage.save_public_key(new_name, key_path)


def diff_version(repo_name:str, version_list:str) -> List[VersionID]:
    repo = storage.load_repo(repo_name)
    return repo.comp(version_list)


def diff_files(hash_list: List[str]) -> List[str]:
    return list(filter(lambda x: not storage.exist_file(x), set(hash_list)))


def diff_programs(repo_name: str, program_list: List[str]) -> List[str]:
    repo = storage.load_repo(repo_name)
    return repo.comp_program(program_list)

# def add_version(repo_name: str, version: Version):
#     repo = storage.load_repo(repo_name)
#     repo.add_version(version)

def update_repo(repo_name: str, branch_name: str, version_list: List[Version]):
    repo = storage.load_repo(repo_name)
    for version in version_list:
        repo.add_version(version)
    repo.move_branch(branch_name, version_list[-1].id)
    storage.save_repo(repo)