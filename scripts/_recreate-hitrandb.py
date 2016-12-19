#!/usr/bin/env python3

from pyfant import hitrandb as db
import astroapi as aa
import os
import sys


if __name__ == "__main__":
    path_ = aa.get_path_to_db("hitrandb")
    if os.path.isfile(path_):
        while True:
            ans = input("File '{}' already exists, overwrite it (Y/n)? ".format(path_)).upper()
            if ans in ("N", "NO"):
                sys.exit()
            if ans in ("Y", "YES", ""):
                break
        os.unlink(path_)

    db.create_db()
    db.populate_db()
    aa.get_python_logger().info("Successfully created file '{}'".format(path_))