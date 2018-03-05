#!/usr/bin/env python
# -*- coding: ascii -*-
#=====================================================================
# Create cscope databases for uboot/linux only including those
#   source and header files being compiled
# Usage: mkcscope.py [-C DIR]
#=====================================================================
import os, sys, subprocess, re, collections
import optparse

class Parser :
    def __init__(self) :
        self.source_files = collections.OrderedDict()

    @staticmethod
    def _wildcard(cwd, file) :
        if len(file) > 0 and file[0] == '/' :
            afile = os.path.abspath(file)
        else :
            afile = os.path.join(cwd, file)
        return afile if os.path.exists(afile) else None

    def _parse_cmd_file(self, cmdfile) :
        fd = open(cmdfile, "r")
        mode = 0
        for line in fd :
            file = None
            if mode :
                fx = line.split()
                if len(fx) == 3 and fx[0] == "$(_wildcard" :
                    fx = fx[1].split(')')
                    file = self._wildcard('.', fx[0])
                elif len(fx) == 2 :
                    file = fx[0]
                else :
                    if len(fx) == 0 :
                        mode = 0
                    continue
            elif line.find('deps_') == 0 :
                mode = 1
                continue
            elif line.find('source_') == 0 :
                fx = line.split()
                file = fx[2]

            if file is not None :
#               print file
                if file not in self.source_files :
                    self.source_files[file] = 1

    def _get_file_list(self) :
        if options.cwd and options.cwd != '.' :
            os.chdir(options.cwd)
        filelist = []
        for root, dirs, files in os.walk('.', topdown=False):
            for name in files:
                if name.endswith('.o.cmd') and name != '.built-in.o.cmd' :
                    filelist.append(os.path.join(root,name))
        return filelist

    def do_cscope(self) :
        filelist = self._get_file_list()
        for file in filelist :
            self._parse_cmd_file(file)

        sp = subprocess.Popen(['cscope', '-bq', '-i-'], stdin=subprocess.PIPE)
        for file in self.source_files :
            sp.stdin.write("%s\n" % file)
        sp.stdin.close()
        sp.wait()

#=====================================================================
#  The main process
#=====================================================================
oparser = optparse.OptionParser()

#oparser.add_option("-d", '', action='store_true', dest='act_download', default=False)
#oparser.add_option("-m", '', action='store_true', dest='act_merge', default=False)
#oparser.add_option("-f", '', action='store', dest='ilist', default='urls.txt')
oparser.add_option("-C", '', action='store', dest='cwd',  default='')

(options, args) = oparser.parse_args()

p = Parser();
p.do_cscope()
