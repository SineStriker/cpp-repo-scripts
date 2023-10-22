# Add copyright text to the front of source files

from __future__ import annotations

import os
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Add copyright text to the front of source files")
    parser.add_argument("--src", metavar="<path>",
                        help="Source directory.", type=str, required=True)
    parser.add_argument("--copyright", metavar="<path>",
                        help="Copyright file.", type=str, required=True)
    parser.add_argument(
        "--verbose", help="Show progress.", action="store_true")
    args = parser.parse_args()

    src_dir: str = args.src
    if not os.path.isabs(src_dir):
        src_dir = os.path.abspath(src_dir)

    copyright_file: str = args.copyright

    if not os.path.isdir(src_dir):
        print("Source directory doesn't exist.")
        sys.exit(-1)

    if not os.path.isfile(copyright_file):
        print("Copyright file doesn't exist.")
        sys.exit(-1)

    # Collect files
    source_files: list[str] = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith((".h", ".hpp", ".cpp", ".cc")):
                source_files.append(os.path.join(root, file))

    with open(copyright_file, "r", encoding="utf-8-sig") as f:
        copyright_lines = f.readlines()

    copyright_comments = [
        "/****************************************************************************\n"]
    copyright_comments.append(" *\n")
    for line in copyright_lines:
        if not line.endswith("\n"):
            line += "\n"
        copyright_comments.append(f" * {line}")
    copyright_comments.append(" *\n")
    copyright_comments.append(
        " ****************************************************************************/\n")

    count = 0
    total = len(source_files)
    for file in source_files:
        count += 1
        if args.verbose:
            print(f"[{count}/{total}] Process {file}")

        with open(file, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()

        # Find header guard and prepend the comment in front
        header_guard_found: bool = False
        is_comment: bool = False
        while len(lines) > 0:
            line = lines[0].lstrip().rstrip()

            # End of comment
            if "*/" in line and is_comment:
                is_comment = False
                del (lines[0])
                continue

            # Empty or comment
            if line == "" or is_comment:
                del (lines[0])
                continue

            if line.startswith("/*") and not is_comment:
                is_comment = True
                del (lines[0])
                continue

            if line.startswith("//"):
                del (lines[0])
                continue

            # Header guard
            if line.startswith("#ifndef") or line.startswith("#pragma"):
                header_guard_found = True
            
            break

        if not header_guard_found:
            continue

        with open(file, "w", encoding="utf-8") as f:
            f.writelines(copyright_comments)
            f.write("\n")
            f.writelines(lines)


if __name__ == "__main__":
    main()
