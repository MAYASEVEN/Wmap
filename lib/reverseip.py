#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Nop Phoomthaisong (aka @MaYaSeVeN)'
__version__ = 'Wmap version 1.0 ( http://mayaseven.com )'

# Requirement
# sudo pip install selenium
# sudo apt-get install phantomjs #phantomjs version 1.4 not work  #install lasted version

import json
import re
import socket
import urllib
import urllib2


class Revereip:
    def __init__(self, args, key, recheck, file):
        self.domains = []
        self.domain_numbers = 0
        self.final_result = {}
        self.ips_or_domains = set(args)
        self.api_key = key
        self.count = 0
        self.log = stdout
        self.recheck = recheck
        self.file = file
        self.http = "http://"
        self.https = "https://"

    def run(self):

        if self.file:
            self.ips_or_domains = self.file_opener()
        while self.ips_or_domains:
            self.domain_numbers = 0
            ip_or_domain = self.ips_or_domains.pop()
            self.reverse_ip(ip_or_domain)
            self.log("[*] You got " + str(self.domain_numbers) + " domains to hack.")
            self.domains = []

    def file_opener(self):
        try:
            file = open(self.file, "r").read()
            find_ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', file)
            ipl = set(find_ip)
            return ipl
        except IOError:
            self.log("[-] Error: File does not appear to exist.")
            exit(1)

    def reverse_ip(self, ip_or_domain):
        raw_domains_temp = []
        name, ip = self.convert_domain_to_ip(ip_or_domain)
        if not ip:
            return
        if self.check_ip_in_cloudflare(ip):
            if name is not "":
                self.log("\n[-] " + name + " hiding behind Cloudflare.")
                return
            self.log("[-] It's Cloudflare IP Address.")
            return

        query = "IP:" + ip
        self.log("\n[*] Host: " + ip + " " + name)

        self.count = 0
        while 1:
            raw_domains = self.bing_call_api(query)
            if raw_domains == raw_domains_temp:
                break
            raw_domains_temp = raw_domains
            if raw_domains == -1:
                break
            self.count += 100
            if self.recheck:
                self.check_domain_name_in_ip(raw_domains, ip)
            else:
                for l in raw_domains:
                    if l[1] not in self.domains:
                        self.log("[+] " + ''.join(l).encode('utf8'))
                        self.domains.append(l)
                self.final_result.update({ip: self.domains})
                self.domain_numbers = len(self.domains)

    def convert_domain_to_ip(self, ip_or_domain):
        name = ""
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_or_domain):
            try:
                name = ip_or_domain
                ip = socket.gethostbyname(ip_or_domain)
                return name, ip
            except socket.gaierror:
                self.log("\n[-] unable to get address for " + ip_or_domain)
                self.domain_numbers = 0
                ip = None
                return name, ip
        return name, ip_or_domain

    def bing_call_api(self, query):
        domains = []
        query = urllib.quote(query)
        user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
        credentials = (':%s' % self.api_key).encode('base64')[:-1]
        auth = 'Basic %s' % credentials
        url = 'https://api.datamarket.azure.com/Bing/SearchWeb/v1/Web?Query=%27' + query + '%27&$format=json' + '&$skip=' + str(
            self.count)
        request = urllib2.Request(url)
        request.add_header('Authorization', auth)
        request.add_header('User-Agent', user_agent)
        request_opener = urllib2.build_opener()
        try:
            response = request_opener.open(request)
        except urllib2.HTTPError, e:
            if e.code == 401:
                self.log('[-] Wrong API Key')
                self.log("""
    You need to..
    1.register or use microsoft account for get Bing API key -> https://datamarket.azure.com/
    2.choose free plan 5,000 Transactions/month -> https://datamarket.azure.com/dataset/bing/searchweb
            """)
                exit(1)
            if e.code == 403:
                self.log('[-] You need to sign up your API Key to use Bing Search API – Web Results Only')
                self.log(
                    '[-] Choose free plan 5,000 Transactions/month -> https://datamarket.azure.com/dataset/bing/searchweb')
                exit(1)
            self.log("[-] Connection problem!!, Cannot connect to Bing API")
            exit(1)

        response_data = response.read()
        json_result = json.loads(response_data)
        result_list = json_result
        if len(result_list['d']['results']) == 0:
            return -1

        for i in range(len(result_list['d']['results'])):
            protocol_domain_port = []
            domain = result_list['d']['results'][i]['DisplayUrl']
            if self.https in domain:
                protocol_domain_port.append("https://")
                port = ':443'
            else:
                protocol_domain_port.append("http://")
                port = ':80'
            domain = domain.replace("http://", "").replace("https://", "")
            rest = domain.split('/', 1)[0]
            if ':' in rest:
                port = rest.split(':', 1)[1]
                rest = rest.split(':', 1)[0]
                port = ':' + port
            protocol_domain_port.append(rest)
            protocol_domain_port.append(port)
            domains.append(protocol_domain_port)
        raw_domains = list()
        map(lambda x: not x in raw_domains and raw_domains.append(x), domains)
        return raw_domains

    def check_domain_name_in_ip(self, raw_domains, ip):
        for l in raw_domains:
            if l[1] in self.domains:
                continue
            try:
                ipc = socket.gethostbyname(l[1].encode("idna"))
            except:
                self.log("[!] " + ''.join(l).encode(
                    'utf8') + " Cannot recheck bacause of hostname encoded, Please recheck it by hand.")
                continue
            if ipc == ip:
                self.log("[+] " + ''.join(l).encode('utf8'))
            else:
                self.log("[!] " + ''.join(l).encode('utf8') + " is on the other IP address, please recheck it by hand.")
                continue
            self.domains.append(l)
        self.final_result.update({ip: self.domains})
        self.domain_numbers = len(self.domains)

    def check_ip_in_cloudflare(self, ip):
        cloudflare_ips = ['199.27.128.0/21', '173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22', '103.31.4.0/22',
                          '141.101.64.0/18', '108.162.192.0/18', '190.93.240.0/20', '188.114.96.0/20',
                          '197.234.240.0/22', '198.41.128.0/17', '162.158.0.0/15', '104.16.0.0/12']
        ipaddr = int(''.join(['%02x' % int(x) for x in ip.split('.')]), 16)
        for net in cloudflare_ips:
            netstr, bits = net.split('/')
            netaddr = int(''.join(['%02x' % int(x) for x in netstr.split('.')]), 16)
            mask = (0xffffffff << (32 - int(bits))) & 0xffffffff
            if (ipaddr & mask) == (netaddr & mask):
                return True
        return False


def stdout(log):
    print log