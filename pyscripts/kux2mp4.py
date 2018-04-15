#!/usr/bin/env python
# vim: set syn=python et :
#============================================================
#
#  Pan Ruochen <ijkxyz@msn.com>
#
#============================================================
import os, sys, re, struct, subprocess, optparse
import platform, locale

class FileDesc() :
	def __init__(self) :
		self.bytes = None
		self.id = None
		self.data = None
		self.name = None

class RuizConverter() :
	CHUNK_SIZE = 0x134

	HEADER1_OFFSET = 0x200
	HEADER2_OFFSET = 0x400200
	VIDEO_DATA_OFFSET = 0xe40000
	ALIGNMENT = 0x40000

	FT_MP4 = 'mp4'
	FT_FLV = 'flv'

	def __init__(self) :
		self.options = None
		self.file_desc = None
		self.encodings = None
		self.encoding  = None

	@staticmethod
	def _decode_file_desc(bytes, fd) :
		fd.id = bytes[0:4].decode('ascii')
		fmt = 'IIIIIIIIIIII'
		fd.data = struct.unpack_from(fmt, bytes, 4)

		for i in xrange(52, len(bytes)) :
			if bytes[i] == 0 :
				break
		fd.name = bytes[52:i].decode('ascii')

	@staticmethod
	def _dump_file_desc(fd) :
		print
		print " ID:   %s" % fd.id
		print " DATA: %08x %08x %08x %08x" % (fd.data[0], fd.data[1], fd.data[2], fd.data[3])
		print "		  %08x %08x %08x %08x" % (fd.data[4], fd.data[5], fd.data[6], fd.data[7])
		print "		  %08x %08x %08x %08x" % (fd.data[8], fd.data[9], fd.data[10],fd.data[11])
		print " NAME: %s" % fd.name

	@staticmethod
	def _is_zeros(bytes) :
		for x in bytes :
			if x != 0 :
				return False
		return True

	@staticmethod
	def _is_eof(bytes) :
		if bytes[0:4].decode('ascii') !=  'TERM' :
			return False
		return RuizConverter._is_zeros(bytes[4:])

	def _get_header2(self, fh) :
		fh.seek(self.HEADER2_OFFSET, 0)

		while True :
			bytes = bytearray(fh.read(self.CHUNK_SIZE))
			if len(bytes) != self.CHUNK_SIZE or RuizConverter._is_eof(bytes) :
				break
			fd = FileDesc()
			RuizConverter._decode_file_desc(bytes, fd)
			self.file_desc.append(fd)

	@staticmethod
	def dump1x(bytes) :
		raw_data=struct.unpack_from('=BI', bytes)

		s = ""
		for x in bytes:
			s += ("%02x " % x)
		print
		print "Raw Bytes: " + s
		print " ID:   %02x %04x" % (raw_data[0], raw_data[1])

	def _get_header1(self, fh) :
		chunksize = 5

		offset = HEADER1_OFFSET
		fp.seek(0x200, 0)

		while True :
			bytes = bytearray(fp.read(chunksize))
			if len(bytes) != chunksize :
				break
			if RuizConverter._is_zeros(bytes) :
				break
			if offset > 0x5200 :
				break
			offset += chunksize
			dump2(bytes)

	def _get_file_type(self, info) :
		for line in info.split('\n') :
			if line.find('Input #') == 0 :
				fx = line.split()
				if fx[2].find(self.FT_FLV) >= 0:
					return self.FT_FLV
				if fx[2].find(self.FT_MP4) >= 0:
					return self.FT_MP4
		return None

	def _copy_media(self, fin, offset, size, ofname) :
		fout = open(ofname, "wb")
		end = offset + size
		fin.seek(offset, 0)
		while offset < end :
			n = min(end - offset, 0x10000)
			fout.write(fin.read(n))
			offset += n
		fout.close()

		st = os.stat(ofname)
		if st.st_size != size :
			raise Exception("%s has size %u, %u expected" %(ofname, st.st_size, size))

	@staticmethod
	def _cleanup(listfile, imfiles, dir) :
		os.remove(listfile) # Remove listfile
		for i in imfiles :	# Remove intermediate files
			os.remove(i)
		try:
			os.rmdir(dir)
		except:
			pass

	@staticmethod
	def _move(src, dst) :
		print '"%s"\t\t"%s"\t\t"%s"' % (os.getcwd(), src, dst)
		if os.path.exists(dst) :
			os.remove(dst)
		os.stat(src)
		os.rename(src, dst)

	def _convert_one(self, kuxfile) :
		self.file_desc = []
		a = kuxfile[0:len(kuxfile)-4]
		tmpdir = self.options.tmpdir if self.options.tmpdir is not None else a
		outdir = os.path.dirname(kuxfile)

		if not os.path.exists(tmpdir) :
			os.mkdir(tmpdir)

		fh = open(kuxfile, "rb")
		self._get_header2(fh)

#		 for fd in self.file_desc :
#			 RuizConverter._dump_file_desc(fd)

		of_list = []
		offset = self.VIDEO_DATA_OFFSET
		i = 1
		ftype = None if not self.options.forcemp4 else self.FT_MP4
		for fd in self.file_desc[2:] :
#			 print "%s" % fd.id
#			 print "  %08x %08x" % (offset, fd.data[2])
#			 print "  %s" % fd.name

			ofname = os.path.join(tmpdir, "%03d-%s%s" % (i, fd.name, '.' + ftype if ftype is not None else ''))
			self._copy_media(fh, offset, fd.data[2], ofname)
			offset = int((offset + fd.data[2] + self.ALIGNMENT - 1) / self.ALIGNMENT) * self.ALIGNMENT

			if i == 1 :
				if not self.options.forcemp4 :
					sp = subprocess.Popen([self.options.ffprobe, '-hide_banner', ofname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					null,info = sp.communicate()
					if sp.returncode :
						raise Exception(info)
					ftype = self._get_file_type(info)
					if ftype is None :
						raise Exception("can not detect file type")
					a = ofname + '.' + ftype
					RuizConverter._move(ofname, a)
					ofname = a
				a = os.path.basename(kuxfile)
				vfile = os.path.join(outdir, a[0:len(a)-4] + '.' + ftype)
				if not self.options.overwrite and os.path.exists(vfile) :
					print "%s exists, skip" % vfile
					return

			i += 1
			of_list.append(ofname)

		fh.close()

		listfile = os.path.join(tmpdir, 'list.txt')
		fh = open(listfile, "w")
		for filename in of_list :
			fh.write('file %s\n' % os.path.basename(filename))
		fh.close()

		a = vfile+'.tmp' if self.options.overwrite else vfile
		args = [self.options.ffmpeg, '-hide_banner', '-f', 'concat', '-i', os.path.basename(listfile), '-c' , 'copy', '-copyts',
			'-f', ftype, os.path.abspath(a)]

		sp = subprocess.Popen(args, cwd=tmpdir)
		o,e = sp.communicate()
		if sp.returncode :
			raise Exception(e)

		if self.options.overwrite :
			RuizConverter._move(a, vfile)
		RuizConverter._cleanup(listfile, of_list, tmpdir)

	def _find_ffx(self, ffprog) :
		xl = []
		x = ffprog.upper()
		if x in os.environ :
			xl.append(os.environ[x])
		for x in os.environ['PATH'].split(os.pathsep) :
			xl.append(os.path.join(x, ffprog))
			if platform.system() == 'Windows' :
				xl.append(os.path.join(x, ffprog) + '.EXE')
		for y in xl :
			if os.path.exists(y) and os.access(y, os.X_OK) :
				return y
		return None

	def run(self, files) :

		if platform.system() == 'Windows' :
			self.encodings = locale.getdefaultlocale()
			self.encoding = self.encodings[1]

		reload(sys)
		sys.setdefaultencoding(self.encoding)

		self.options.ffmpeg = self._find_ffx('ffmpeg')
		if self.options.ffmpeg is None :
			print >>sys.stderr, "Cannot find ffmpeg"
			exit(1)
		self.options.ffprobe = self._find_ffx('ffprobe')
		if self.options.ffprobe is None :
			print >>sys.stderr, "Cannot find ffprobe"
			exit(1)

		filelist = []
		for root, dirs, files in os.walk('.', topdown=True):
			dirs[:] = [ d for d in dirs if not os.path.exists(os.path.join(os.path.join(root,d),'.nomedia')) ]
			for name in files:
				if name.lower().endswith('.kux') :
					filelist.append(os.path.join(root,name))

		for i in filelist :
#			 try:
				self._convert_one(i)
#			 except Exception,e:
#				 print str(e)


def kux2mp4_main() :
	oparser = optparse.OptionParser()
	oparser.add_option("-p", '--ffprobe', dest='ffprobe',default='ffprobe')
	oparser.add_option("-m", '--ffmpeg', dest='ffmpeg', default='ffmpeg')
	oparser.add_option("-T", '--tmpdir', dest='tmpdir', default=None)
	oparser.add_option("-4", '--forcemp4', dest='forcemp4', action='store_true', default=False)
	oparser.add_option("-O", '--overwrite', dest='overwrite', action='store_true', default=False)

	z = RuizConverter()
	(z.options, args) = oparser.parse_args()

	z.run(args[1:])

if __name__ == '__main__' :
	kux2mp4_main()
