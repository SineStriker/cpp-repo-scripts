# Generate include files from source directory into a new directory tiledly

from __future__ import annotations

import argparse
import os
import sys
import shutil


def main():
    parser = argparse.ArgumentParser(
        description="Deploy ChorusKit Application on Windows")
    parser.add_argument("--src", metavar="<path>",
                        help="Source directory.", type=str, required=True)
    parser.add_argument("--dest", metavar="<path>",
                        help="Destination directory.", type=str, required=True)
    parser.add_argument(
        "--copy", help="Copy files.", action="store_true")
    parser.add_argument(
        "--rm", help="Remove destination directory first.", action="store_true")
    parser.add_argument(
        "--verbose", help="Show deploy progress.", action="store_true")
    args = parser.parse_args()

    src_dir: str = args.src
    if os.path.isabs(src_dir):
        src_dir = os.path.abspath(src_dir)

    dest_dir: str = args.dest
    if os.path.isabs(dest_dir):
        src_dir = os.path.abspath(dest_dir)

    if not os.path.isdir(src_dir):
        print("Source directory doesn't exist.")
        sys.exit(-1)

    # Collect files
    header_files: list[str] = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith((".h", ".hpp")):
                header_files.append(os.path.join(root, file))

    # Remove destination directory if required
    if args.rm and os.path.exists(dest_dir):
        if os.path.isdir(dest_dir):
            shutil.rmtree(dest_dir)
        else:
            os.remove(dest_dir)

    for file in header_files:
        name, _ = os.path.splitext(os.path.basename(file))

        # Determine if it's a private header
        if name.endswith("_p"):
            dir = os.path.join(dest_dir, "private")
        else:
            dir = dest_dir

        # Make destination directory
        if not os.path.exists(dir):
            os.makedirs(dir)

        new_file = os.path.join(dir, os.path.basename(file))

        if args.copy:
            shutil.copyfile(file, new_file)
        else:
            # Write relative path
            rel_path = os.path.relpath(file, dir).replace('\\', '/')
            with open(new_file, "w") as f:
                f.write(f"#include \"{rel_path}\"\n")


if __name__ == "__main__":
    main()
