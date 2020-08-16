#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from baduk.main import Main


def main():
    try:
        Main()
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    main()
