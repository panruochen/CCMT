#!/usr/bin/env python
# -*- coding: ascii -*-
#=====================================================================
# Find symbols without .o files under specified directory
# Usage: findsym [-C DIR] [-u] -e PATTERN1 -e PATTERN2 ...
#=====================================================================
import os, sys, subprocess, re, collections
import optparse

class FindSymol :
	def __init__(self, prefix, cwd, patterns, find_undef) :
#
#  find_undef:
#     0  - Find symbol definition (default behavior)
#     1  - Find symbol reference
		self.prefix   = prefix
		self.cwd      = cwd if cwd is not None else '.'
		z = '^('
		for x in patterns :
			z += x + '|'
		self.patterns = z.rstrip('|') + ')$'
		self.nm       = 'nm' if prefix is None else os.path.join(prefix,'nm')
		self.find_undef = int(find_undef) if find_undef is not None else 0

	def _check_against_objfile(self, objfile) :
		args = [ self.nm, objfile ]
		sp = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		lines,errors = sp.communicate()

		if sp.returncode != 0 :
			return False

		results = ''
		for i in lines.split('\n') :
			fx = i.rstrip('\n').split()
			if len(fx) < 2 : continue
			if self.find_undef == 0 and fx[1] in ('b', 'B', 't', 'W', 'd', 'D', 'w', 'W') :
				m = re.search(self.patterns, fx[2])
			elif fx[0] in ('u', 'U') :
				m = re.search(self.patterns, fx[1])
			else :
				continue
			if m : return True

		return False

	def do_findsym(self) :
		objlist = []
		for root, dirs, files in os.walk(self.cwd, topdown=False):
		    for name in files:
				a,b = os.path.splitext(name)
				if b == '.o' : objlist.append(os.path.join(root,name))

		for objfile in objlist :
			if self._check_against_objfile(objfile) :
				print objfile

#=====================================================================
#  The main process
#=====================================================================
def findsym_main() :
	oparser = optparse.OptionParser()

	oparser.add_option("-p", '', action='store', dest='prefix',    default=None)
	oparser.add_option("-C", '', action='store', dest='cwd',       default=None)
	oparser.add_option("-e", '', action='append',dest='patterns', default=[])
	oparser.add_option("-u", '', action='store_true', dest='find_undef', default=False)

	(options, args) = oparser.parse_args()
	p = FindSymol(options.prefix, options.cwd, options.patterns, options.find_undef);
	print >>sys.stderr, "find_undef = ", options.find_undef
	print >>sys.stderr, "patterns = ", p.patterns
	p.do_findsym()

if __name__ == '__main__' :
	findsym_main()
