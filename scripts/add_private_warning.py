# Add copyright text to the front of source files

from __future__ import annotations

import os
import sys
import argparse
import re


def main():
    parser = argparse.ArgumentParser(
        description="Add copyright text to the front of source files")
    parser.add_argument("--src", metavar="<path>",
                        help="Source directory.", type=str, required=True)
    parser.add_argument("--name", metavar="<name>",
                        help="Library name.", type=str, required=True)
    parser.add_argument(
        "--verbose", help="Show progress.", action="store_true")
    args = parser.parse_args()

    src_dir: str = args.src
    if not os.path.isabs(src_dir):
        src_dir = os.path.abspath(src_dir)

    if not os.path.isdir(src_dir):
        print("Source directory doesn't exist.")
        sys.exit(-1)

    comment = f"""//
//  W A R N I N G !!!
//  -----------------
//
// This file is not part of the {args.name} API. It is used purely as an
// implementation detail. This header file may change from version to
// version without notice, or may even be removed.
//
"""

    # Collect files
    header_files: list[str] = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(("_p.h", "_p.hpp")):
                header_files.append(os.path.join(root, file))

    i = 0
    count = len(header_files)
    for file in header_files:
        i += 1
        if args.verbose:
            print(f"[{i}/{count}] Process {file}")

        with open(file, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()

        # Find header guard and append the comment after
        header_guard_index: int = -1
        for i in range(0, len(lines)):
            line = lines[i].lstrip().rstrip()

            # Header guard
            if line.startswith("#ifndef"):
                if i+1 >= len(lines):
                    break
                next_line = lines[i+1].lstrip().rstrip()
                if not next_line.startswith("#define"):
                    break
                if line[7:].lstrip().rstrip() != next_line[7:].lstrip().rstrip():
                    break
                header_guard_index = i
                break
            elif line.startswith("#pragma once"):
                header_guard_index = i
                break

        if header_guard_index < 0:
            continue

        has_space: bool = False
        for i in range(header_guard_index + 1, len(lines)):
            line = lines[i].lstrip().rstrip()

            if line.startswith("#"):
                continue

            if line == "":
                has_space = True

            header_guard_index = i
            break

        warning_index: int = -1
        warning_pattern: str = r"This file is not part of the (\w+) API"
        for i in range(header_guard_index + 1, len(lines)):
            line = lines[i].lstrip().rstrip()

            if line == "":
                continue

            if line.startswith("//"):
                if re.search(warning_pattern, line):
                    warning_index = i
                    break
                continue

            break

        with open(file, "w", encoding="utf-8") as f:
            if warning_index >= 0:
                f.writelines(lines[0:warning_index])
                f.writelines([re.sub(warning_pattern,
                                     rf"This file is not part of the {args.name} API", lines[warning_index])])
                f.writelines(lines[warning_index + 1:])
            else:
                f.writelines(lines[0:header_guard_index])
                f.write("\n")
                f.write(comment)
                if not has_space:
                    f.write("\n")
                f.writelines(lines[header_guard_index:])


if __name__ == "__main__":
    main()
