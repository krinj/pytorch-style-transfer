#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bump the micro-version number of the package.
"""
import os
import re

if __name__ == "__main__":

    with open("version", "r") as f:
        current_version = f.readline()
        versions = current_version.split(".")
        versions[-1] = str(int(versions[-1]) + 1)
        new_version = ".".join(versions)

    with open("version", "w") as f:
        f.write(new_version)

    print("Bumping Version Number: {} -> {}".format(current_version, new_version))

    # Also apply the new version to the README.md.
    with open("README.md", "r") as f:
        lines = f.readlines()

    p = re.compile("!\[Version\]\(.*\)")
    with open("README.md", "w") as f:
        for line in lines:
            line = re.sub(p, "![Version](https://img.shields.io/badge/version-{}-333333.svg)".format(new_version), line)
            f.write(line)

    os.system("git add version")
    os.system("git add README.md")
