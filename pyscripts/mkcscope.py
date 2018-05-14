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
	def __init__(self, source_path, obj_path, cs_out_path) :
		self.source_files = collections.OrderedDict()
		self.source_path = source_path if source_path is not None else '.'
		self.obj_path = obj_path if obj_path is not None else self.source_path
		self.cs_out_path = cs_out_path

	def _wildcard(self, file) :
		if len(file) > 0 and file[0] == '/' :
			afile = os.path.abspath(file)
		else :
			afile = os.path.join(self.source_path, file)
			if not os.path.exists(afile) :
				afile = os.path.join(self.obj_path, file)
		return afile if os.path.exists(afile) else None

	def _parse_cmd_file(self, cmdfile) :
		fd = open(cmdfile, "r")
		mode = 0
		prefix_source = 'source_'
		for line in fd :
			file = None
			if mode :
				fx = line.split()
				if len(fx) == 3 and fx[0] == "$(wildcard" :
					fx = fx[1].split(')')
					file = self._wildcard(fx[0])
				elif len(fx) == 2 :
					file = self._wildcard(fx[0])
					if file is None :
						print >>sys.stderr, '**** "%s" not exists' % fx[0]
				else :
					if len(fx) == 0 :
						mode = 0
					continue
			elif line.find('deps_') == 0 :
				mode = 1
				continue
			elif line.find(prefix_source) == 0 :
				fx = line.split()
				a = fx[0][len(prefix_source):]
				file = self._wildcard(fx[2])
				if file is None :
					print >>sys.stderr, '**** "%s" not exists' % fx[0]

			if file is not None :
#               print file
				if file not in self.source_files :
					self.source_files[file] = 1

	def _get_file_list(self) :
		if self.source_path and self.source_path != '.' :
			os.chdir(self.source_path)
		filelist = []
		for root, dirs, files in os.walk(self.obj_path, topdown=False):
			for name in files:
				if name.endswith('.o.cmd') and name != '.built-in.o.cmd' :
					filelist.append(os.path.join(root,name))
		return filelist

	def do_cscope(self) :
		cwd = os.getcwd()
		filelist = self._get_file_list()
		print >>sys.stderr, "%u files found" % (len(filelist))
		for file in filelist :
			self._parse_cmd_file(file)

		os.chdir(cwd)
		sp = subprocess.Popen(['cscope', '-bq', '-i-'], stdin=subprocess.PIPE, cwd=self.cs_out_path)
		for file in self.source_files :
			sp.stdin.write("%s\n" % file)
		sp.stdin.close()
		sp.wait()

		fh = open('a-filelist.txt', 'w')
		for file in self.source_files :
			print >>fh, file
		fh.close()

#=====================================================================
#  The main process
#=====================================================================
def mkcscope_main() :
	print >>sys.stderr, sys.argv
	oparser = optparse.OptionParser()

#oparser.add_option("-d", '', action='store_true', dest='act_download', default=False)
#oparser.add_option("-m", '', action='store_true', dest='act_merge', default=False)
#oparser.add_option("-f", '', action='store', dest='ilist', default='urls.txt')
	oparser.add_option("-K", '', action='store', dest='source_path',  default=None)
	oparser.add_option("-O", '', action='store', dest='obj_path',  default=None)
	oparser.add_option("-o", '', action='store', dest='cs_out_path',  default=None)

	(options, args) = oparser.parse_args()
	p = Parser(options.source_path, options.obj_path, options.cs_out_path);
	p.do_cscope()

if __name__ == '__main__' :
	mkcscope_main()
