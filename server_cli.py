import os
import sys
import argparse
import platform

from filelock import Timeout, FileLock

from server import controller


def acquire_lock() -> FileLock:
    lockdir = "C:\\tmp"
    if platform.system() == 'Linux':
        lockdir = '/tmp'
    if not os.path.isdir(lockdir):
        lockdir = "C:\\Temp"
    if not os.path.isdir(lockdir):
        os.mkdir(lockdir)
    try:
        lock = FileLock(os.path.join(lockdir, "lock.txt"), timeout=1)
        return lock
    except Timeout:
        raise ValueError("Another datagit is running")


def func_init(args: argparse.Namespace) -> None:
    controller.init()


def func_checkout(args: argparse.Namespace) -> None:
    if (args.v == None) and (args.b == False):
        raise ValueError("You should give -v or -b, not neither of them!")
    if (args.v != None) and (args.b != True):
        raise ValueError("You should give -v or -b, not both of them!")
    if args.v != None:
        controller.checkout_v(args.v)
        return
    if args.b != None:
        controller.checkout_b(args.b)
        return


def func_save(args: argparse.Namespace) -> None:
    controller.save(args.v)


def func_unsave(args: argparse.Namespace) -> None:
    controller.unsave(args.v)


def func_adjust(args: argparse.Namespace) -> None:
    controller.adjust()


def func_log(args: argparse.Namespace) -> None:
    print(controller.log())


def func_status(args: argparse.Namespace) -> None:
    print(controller.status())


def func_branch(args: argparse.Namespace):
    controller.branch(args.name)


def func_get_repo(args: argparse.Namespace) -> None:
    if (args.a == False) and (args.v == None):
        raise ValueError("You should give one of [-a] or [-r repo_name], not none of them")
    if (args.a == True) and (args.v != None):
        raise ValueError("You should give one of [-a] or [-r repo_name], not both of them")
    print(controller.get_repo(args.a, args.v))


def func_create(args: argparse.Namespace) -> None:
    controller.create(args.name)


def func_fork(args: argparse.Namespace) -> None:
    controller.fork(args.old_name, args.new_name)


def main():
    parser = argparse.ArgumentParser(prog="datagit")
    subparsers = parser.add_subparsers(help="subcommands")

    parser_init = subparsers.add_parser('init', help='initialize a repo')
    parser_init.set_defaults(func=func_init)

    parser_checkout = subparsers.add_parser('checkout', help='checkout the dataset')
    parser_checkout.add_argument('-v', type=int, help='checkout dataset of the version ID')
    parser_checkout.add_argument('-b', type=str, help='checkout dataset on the branch')
    parser_checkout.set_defaults(func=func_checkout)

    parser_save = subparsers.add_parser('save', help='save the dataset')
    parser_save.add_argument('-v', type=int, required=True, help='save dataset of the version ID')
    parser_save.set_defaults(func=func_save)

    parser_unsave = subparsers.add_parser('unsave', help='unsave the dataset')
    parser_unsave.add_argument('-v', type=int, required=True, help='unsave dataset of the version ID')
    parser_unsave.set_defaults(func=func_unsave)

    parser_adjust = subparsers.add_parser('adjust', help='adjust the storage of dataset')
    parser_adjust.set_defaults(func=func_adjust)

    parser_log = subparsers.add_parser('log', help='print the log')
    parser_log.set_defaults(func=func_log)

    parser_log = subparsers.add_parser('status', help='print the status')
    parser_log.set_defaults(func=func_status)

    parser_branch = subparsers.add_parser('branch', help='create a new branch')
    parser_branch.add_argument('name', type=str, help='name of the branch')
    parser_branch.set_defaults(func=func_branch)

    parser_get_repo = subparsers.add_parser('get_repo', help='get information of repos')
    parser_get_repo.add_argument('-a', action='store_true', help='if all')
    parser_get_repo.add_argument('-r', type=str, help='name of the repo that you need to learn')
    parser_get_repo.set_defaults(func=func_get_repo)

    parser_create = subparsers.add_parser('create', help='create a new repo')
    parser_create.add_argument('name', type=str, help='name of the repo that you create')
    parser_create.set_defaults(func=func_create)

    parser_fork = subparsers.add_parser('fork', help='fork a repo');
    parser_fork.add_argument('old_name', type=str, help='name of the old repo')
    parser_fork.add_argument('new_name', type=str, help='name of the new repo')
    parser_fork.set_defaults(func=func_fork)


    args = parser.parse_args(sys.argv[1:])  # the first argument is main.py
    if not 'func' in args:
        parser.print_help()
        sys.exit(1)

    try:
        with acquire_lock():
            args.func(args)
    except (ValueError, RuntimeError) as e:
        print("Error:", e)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Terminated")
        sys.exit(1)


if __name__ == "__main__":
    main()
