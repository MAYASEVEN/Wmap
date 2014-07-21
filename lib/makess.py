#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Nop Phoomthaisong (aka @MaYaSeVeN)'
__version__ = 'Wmap version 1.5 ( http://mayaseven.com )'

# Requirement
# sudo pip install selenium
# sudo apt-get install phantomjs #phantomjs version 1.4 not work  #install lasted version

import urllib2

from selenium import webdriver


class Makess:
    def __init__(self, targets, foldername, timeout_second):
        self.targets = targets
        self.hosts = targets.keys()
        self.foldername = foldername
        self.cms_dict = {}
        self.header_dict = {}
        self.desc_dict = {}
        self.log = self.stdout
        self.logall = ""
        self.prepare_body1 = ""
        self.prepare_body2 = ""
        self.prepare_body3 = ""
        self.prepare_body_temp = ""
        self.banner = "<h1> Wmap (\"Web Mapper\") </h1>"
        self.prepare_header1 = ""
        self.prepare_header2 = ""
        self.prepare_header3 = ""
        self.html_footer = ""
        self.count = 0
        self.all = 0
        self.firsttime = True
        self.timeout_second = timeout_second

    def run(self):
        hosts = self.targets.keys()
        while hosts:
            host = hosts.pop()
            self.all += len(self.targets[host])
        self.log("\n[*] Web Mapping " + str(self.all) + " domains\n")
        while self.hosts:
            host = self.hosts.pop()
            self.screenshot(host)

    def screenshot(self, host):
        self.prepare_html_header1()
        self.prepare_html_header2(host)
        self.prepare_html_body1(host)
        for domain in self.targets[host]:
            self.count += 1
            self.prepare_header2 += "<li><a href=\"#" + ''.join(domain) + "\">" + ''.join(domain) + "</a></li>\n"
            self.log("[" + str(self.count) + "] Making screenshot of " + ''.join(domain).encode('utf8'))
            try:
                driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
            except:
                self.log("[-] " + ''.join(domain).encode('utf8') + " Cannot connect GhostDriver")
                continue
            # driver = webdriver.PhantomJS()
            # driver.set_window_size(1366, 768)
            driver.set_window_size(1280, 800)
            driver.set_page_load_timeout(self.timeout_second)
            try:
                driver.get(domain[0] + domain[1].encode("idna") + domain[2])
            except:
                self.log("[-] Timeout Error")
                self.prepare_html_body_timeout(domain)
                self.prepare_body3 = self.prepare_body_temp + self.prepare_body1 + self.prepare_body2
                self.prepare_body_temp = self.prepare_body3
                self.prepare_body2 = ""
                self.make_html_result()
                continue
            try:
                cms = driver.find_element_by_xpath("//meta[@name='Generator']")
                cms = cms.get_attribute('content')
            except:
                cms = None
            if not cms:
                try:
                    cms = driver.find_element_by_xpath("//meta[@name='generator']")
                    cms = cms.get_attribute('content')
                except:
                    cms = None
            try:
                desc = driver.find_element_by_xpath("//meta[@name='Description']")
                desc = desc.get_attribute('content')
            except:
                desc = None
            if not desc:
                try:
                    desc = driver.find_element_by_xpath("//meta[@name='description']")
                    desc = desc.get_attribute('content')
                except:
                    desc = None
            request = urllib2.Request(domain[0] + domain[1].encode("idna") + domain[2])
            request.add_header('User-Agent',
                               'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)')
            request.add_header('Referer', 'http://google.com')
            try:
                response = urllib2.urlopen(request, timeout=7).info()
            except:
                response = None
            self.desc_dict.update({''.join(domain).encode('utf8'): desc})
            self.header_dict.update({''.join(domain).encode('utf8'): response})
            self.cms_dict.update({''.join(domain).encode('utf8'): cms})
            driver.save_screenshot(
                self.foldername + '/img/' + domain[1].encode('utf8') + domain[2].encode('utf8') + ".png")
            self.prepare_html_body2(domain)
            self.prepare_body3 = self.prepare_body_temp + self.prepare_body1 + self.prepare_body2
            self.prepare_body_temp = self.prepare_body3
            self.prepare_body2 = ""
            self.make_html_result()

    def prepare_html_body1(self, host):
        self.prepare_body1 = """
        <br><hr>
         <h1><a href="http://whois.domaintools.com/""" + host + """\" id=\"""" + host + """\"
         style="padding-top: 80px; margin-top: -80px;">""" + host + """</a></h1>
         <hr><br>"""

    def prepare_html_body2(self, domain):
        self.prepare_body2 += '<table border="1" bordercolor=GREEN>\n'
        self.prepare_body2 += "<tr><td><h2><center><a href=\"" + ''.join(domain) + "\" id=\"" + ''.join(
            domain) + "\" style=\"padding-top: 80px; margin-top: -80px;\">" + ''.join(
            domain) + "</a></center></h2></td></tr>\n"
        try:
            self.prepare_body2 += "<tr><td><h3><b>CMS:</b> " + str(self.cms_dict[''.join(domain)])[0:100] + "</h3>\n"
        except:
            self.prepare_body2 += "<tr><td><h3><b>CMS:</b> Cannot identify CMS, recheck it by hand. </h3>\n"
        try:
            self.prepare_body2 += "<br> Description: " + str(self.desc_dict[''.join(domain)])[0:100] + "<br>\n"
        except:
            self.prepare_body2 += "<br> Description: None <br>\n"
        try:
            # header = str(self.header_dict[''.join(domain)]).replace("\n", "\n<br>")
            # self.prepare_result += "<br>" + header2 + "</td></tr>\n"
            header = str(self.header_dict[''.join(domain)]).split('\n')
            for i in header:
                if len(i) >= 150:
                    w = []
                    n = len(i)
                    for j in range(0, n, 100):
                        w.append(i[j:j + 100])
                    self.prepare_body2 += '<br> '.join(w)
                    continue
                self.prepare_body2 += "<br> " + i
            self.prepare_body2 += "</td></tr>\n"
        except:
            self.prepare_body2 += "<br> None</td></tr>\n"
        self.prepare_body2 += "<tr><td><a href=\"" + ''.join(domain) + "\"><img src=\"img/" + domain[
            1] + domain[2] + ".png" + "\"></a></td></tr>\n"
        self.prepare_body2 += "</table><br>\n"

    def prepare_html_body_timeout(self, domain):
        self.prepare_body2 += '<table border="1" bordercolor=GREEN>\n'
        self.prepare_body2 += "<tr><td><h2><center><a href=\"" + ''.join(domain) + "\" id=\"" + ''.join(
            domain) + "\" style=\"padding-top: 80px; margin-top: -80px;\">" + ''.join(
            domain) + "</a></center></h2></td></tr>\n"
        self.prepare_body2 += "<tr><td><h3><b>It's time out, try to open it by hands</b></h3>\n"
        self.prepare_body2 += "<br></td></tr>\n"
        self.prepare_body2 += "<tr><td><a href=\"" + ''.join(
            domain) + "\"><img src=\"../../dist/timeout.png" + "\"></a></td></tr>\n"
        self.prepare_body2 += "</table><br>\n"

    def prepare_html_header1(self):
        hosts = self.targets.keys()
        self.prepare_header1 = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Web Mapper">
    <meta name="author" content="MaYaSeVeN">
    <meta name="generator" content="Web Mapper(wmap)" />
    <link rel="shortcut icon" href="../../dist/fav.png">

    <title>""" + __version__ + """</title>

    <!-- Bootstrap core CSS -->
    <link href="../../dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="../../dist/template.css" rel="stylesheet">

    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="../../dist/js/ie10-viewport-bug-workaround.js"></script>

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>

  <body>

    <div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="#">Wmap</a>
        </div>
        <div class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
             <li class="dropdown">
                <a href="#" class="dropdown-toggle" data-toggle="dropdown">Results
                <span class=badge> """ + str(len(hosts)) + """</span><span class=caret></span></a>
         <ul class="dropdown-menu" role="menu">
"""

    def prepare_html_header2(self, host):
        if self.firsttime:
            self.prepare_header2 += """
        <li class="dropdown-submenu">
        <a tabindex="-1" href="#""" + host + """\">
        """ + host + """
        <span class="badge"> """ + str(len(self.targets[host])) + """</span></a>
        <ul class="dropdown-menu">
        """
            self.firsttime = False
        else:
            self.prepare_header2 += """</ul>
        <li class="dropdown-submenu">
        <a tabindex="-1" href="#""" + host + """\">
        """ + host + """
        <span class="badge"> """ + str(len(self.targets[host])) + """</span></a>
        <ul class="dropdown-menu">
        """

    def make_html_result(self):
        self.prepare_header3 = """</ul>
              </li></ul>
            <li><a href="log.txt">Log</a></li>
            <li><a href="https://github.com/MaYaSeVeN/Wmap">About</a></li>

          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </div>
<center><br>
"""
        self.html_footer = """</center>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
<script src="../../dist/js/bootstrap.min.js"></script>
</body></html>
        """
        result = self.prepare_header1 + self.prepare_header2 + self.prepare_header3 + self.banner + self.prepare_body3 + self.html_footer
        with open(self.foldername + '/index.html', 'w') as index:
            index.write(result.encode('utf8'))

    def stdout(self, log):
        print log
        self.logall += log