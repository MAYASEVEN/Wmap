#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Nop Phoomthaisong (aka @MaYaSeVeN)'
__version__ = 'Wmap version 1.2 ( http://mayaseven.com )'

# Requirement
# sudo pip install selenium
# sudo apt-get install phantomjs #phantomjs version 1.4 not work  #install lasted version

import datetime
import optparse
import os
import sys
import timeit
import xml.dom.minidom

from lib import makess, reverseip


def main():
    print "\n" + __version__

    usage = "Usage: python " + sys.argv[
        0] + " -k [Bing API Key] [IP_1] [IP_2] [IP_N] [Domain_1] [Domain_2] [Domain_N]\nUsage: python " + \
            sys.argv[
                0] + " -k [Bing API Key] -l [list file of IP address]\nUsage: python " + sys.argv[
                0] + " -k [Bing API Key] -x [nmap XML file from nmap -oX]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-k", "--key", dest="key", help="Bing API key")
    parser.add_option("-l", "--list", dest="file", metavar="FILE", help="list file of IP address")
    parser.add_option("-x", "--xml", dest="filexml", metavar="XML", help="Parses nmap XML (nmap -oX)")
    parser.add_option("-d", "--disable", action="store_false",
                      help="set this option to disable to recheck is that the domain is in IP address",
                      default=True)
    parser.add_option("-b", "--bing", action="store_false",
                      help="set this option to disable Bing reverse domains",
                      default=True)

    (options, args) = parser.parse_args()
    if not options.key and not options.bing:
        key = options.key
        recheck = options.disable
        file = options.file
        filexml = options.filexml
        bing_reverse = options.bing
        Wmap(args, key, recheck, file, filexml, bing_reverse).run()
        exit(0)
    elif not options.key or (not options.file and not options.filexml and len(args) == 0):
        print parser.format_help()
        print """
you need to..
1.register or use microsoft account for get Bing API key -> https://datamarket.azure.com/
2.choose free plan 5,000 Transactions/month -> https://datamarket.azure.com/dataset/bing/searchweb
        """
        exit(1)
    key = options.key
    recheck = options.disable
    file = options.file
    filexml = options.filexml
    bing_reverse = options.bing
    Wmap(args, key, recheck, file, filexml, bing_reverse).run()


class Wmap:
    def __init__(self, args, key, recheck, file, filexml, bing_reverse):
        self.args = args
        self.key = key
        self.recheck = recheck
        self.file = file
        self.filexml = filexml
        self.foldername = None
        self.dict_target_from_nmap = {}
        self.log = self.stdout
        self.logall = ""
        self.bing_reverse = bing_reverse

    def run(self):
        start = timeit.default_timer()
        self.make_folder_result()
        if self.filexml and not self.bing_reverse:
            self.parse_nmap_xml()
            makeSS = makess.Makess(self.dict_target_from_nmap, self.foldername)
            makeSS.run()
        elif self.filexml:
            self.parse_nmap_xml()
            ip_target_from_nmap = self.dict_target_from_nmap.keys()
            reverseIP = reverseip.Revereip(ip_target_from_nmap, self.key, self.recheck, None)
            reverseIP.run()
            targets_from_reverseIP = reverseIP.final_result
            concat_targets = {}
            for i in targets_from_reverseIP.keys():
                for j in self.dict_target_from_nmap.keys():
                    if i == j:
                        c = targets_from_reverseIP[i] + self.dict_target_from_nmap[j]
                        concat_targets.update({i: c})
            makeSS = makess.Makess(concat_targets, self.foldername)
            makeSS.run()
        else:
            reverseIP = reverseip.Revereip(self.args, self.key, self.recheck, self.file)
            reverseIP.run()
            makeSS = makess.Makess(reverseIP.final_result, self.foldername)
            makeSS.run()
        stop = timeit.default_timer()
        total_time = stop - start
        self.log('[+] Wmap done: Mapped in %.2fs seconds' % total_time)
        with open(self.foldername + "/log.txt", "a") as log_file:
            log_print = "\n" + __version__
            if self.bing_reverse:
                log_print += reverseIP.logall.replace("[", "\n[")
            log_print += makeSS.logall.replace("[", "\n[") + self.logall.replace("[", "\n[")
            log_file.write(log_print)

    def parse_nmap_xml(self):
        input_files = open(self.filexml, 'r')
        doc = xml.dom.minidom.parse(input_files)
        for host in doc.getElementsByTagName("host"):
            addresses = host.getElementsByTagName("address")
            for address in addresses:
                targets_from_nmap = []
                if address.getAttribute("addrtype") == "ipv4":
                    ip = address.getAttribute("addr")
                else:
                    continue
                for port in host.getElementsByTagName("port"):
                    for state in port.getElementsByTagName("state"):
                        if state.getAttribute("state") == "open":
                            for services in port.getElementsByTagName("service"):
                                targets_temp = []
                                if "http" in services.getAttribute("name").lower() or "https" in services.getAttribute(
                                        "name").lower() or port.getAttribute("portid") == "80" or port.getAttribute(
                                        "portid") == "443":
                                    if "http" in services.getAttribute("name").lower():
                                        if "ssl" in services.getAttribute(
                                                "tunnel").lower() or "ssl" in services.getAttribute(
                                                "product").lower():
                                            targets_temp.append("https://")
                                        else:
                                            targets_temp.append("http://")
                                    elif port.getAttribute("portid") == "443":
                                        targets_temp.append("https://")
                                    elif "https" in services.getAttribute(
                                            "name").lower() or "ssl" in services.getAttribute(
                                            "name").lower():
                                        targets_temp.append("https://")
                                    else:
                                        targets_temp.append("http://")
                                    targets_temp.append(ip)
                                    targets_temp.append(":" + port.getAttribute("portid"))
                                    targets_from_nmap.append(targets_temp)
                                    self.dict_target_from_nmap.update({ip: targets_from_nmap})

                        else:
                            continue

    def make_folder_result(self):
        self.foldername = "output"
        if not os.path.exists(self.foldername):
            os.makedirs(self.foldername)
        self.foldername = self.foldername + "/wmap_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if not os.path.exists(self.foldername):
            os.makedirs(self.foldername)
            os.makedirs(self.foldername + "/img")
        else:
            self.log("[-] Cannot make result folder")
            exit(1)

    def stdout(self, log):
        print log
        self.logall += log


if __name__ == "__main__":
    main()