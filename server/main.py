import sys
import os
import argparse
import controller
import platform
from filelock import Timeout, FileLock

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


def func_update(args: argparse.Namespace) -> None:
    controller.update(args.dir)


def func_add(args: argparse.Namespace) -> None:
    controller.add(args.src, args.dst)


def func_transform(args: argparse.Namespace) -> None:
    controller.transform(args.dir, args.entry, args.m, args.s, args.d)


def func_commit(args: argparse.Namespace) -> None:
    controller.commit(args.m)


def func_checkout(args: argparse.Namespace) -> None:
    if (args.v == None) and (args.b == None):
        raise ValueError("You should give -v or -b, not neither of them!")
    if (args.v != None) and (args.b != None):
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


def main():
    parser = argparse.ArgumentParser(prog="datagit")
    subparsers = parser.add_subparsers(help="subcommands")

    parser_init = subparsers.add_parser('init', help='initialize a repo')
    parser_init.set_defaults(func=func_init)

    parser_update = subparsers.add_parser('update', help='update a directory')
    parser_update.add_argument('dir', type=str, help='dir to update')
    parser_update.set_defaults(func=func_update)

    parser_update = subparsers.add_parser('add', help='add a directory')
    parser_update.add_argument('src', type=str, help='from src')
    parser_update.add_argument('dst', type=str, help='copy to dst')
    parser_update.set_defaults(func=func_add)

    parser_transform = subparsers.add_parser('transform', help='transform the dataset')
    parser_transform.add_argument('dir', type=str, help='dir of the promgramme')
    parser_transform.add_argument('entry', type=str, help='dir of the entry promgramme')
    parser_transform.add_argument('-m', type=str, required=True, help='message of the promgramme')
    parser_transform.add_argument('-s', action='store_true', help='if one to one ')
    parser_transform.add_argument('-d', default='.', type=str, help='the dir that will be transformed')
    parser_transform.set_defaults(func=func_transform)

    parser_commit = subparsers.add_parser('commit', help='commit the dataset')
    parser_commit.add_argument('-m', type=str, required=True, help='commit message')
    parser_commit.set_defaults(func=func_commit)

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
