#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Nop Phoomthaisong (aka @MaYaSeVeN)'
__version__ = 'Wmap version 1.1 ( http://mayaseven.com )'

import sys

import wmap


class Log:
    def __init__(self, log):
        self.log = log

    def run(self):
        print self.log
        with open(wmap.Wmap.foldername + "/log.txt", "a") as log_file:
            old_stdout = sys.stdout
            sys.stdout = log_file
            print self.log
            sys.stdout = old_stdout
        log_file.close()