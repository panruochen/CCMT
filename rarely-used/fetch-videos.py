#!/usr/bin/env python
# -*- coding: utf-8 -*-
#=====================================================================
# 使用方法：
#   1. 使用工具解析视频文件的地址，并拷贝到一个文本文件中
#   2. 运行本程序自动下载并合并视频文件
#=====================================================================

import os, sys, subprocess
import optparse

gFFMPEG = '/d/Tools/ffmpeg/bin/ffmpeg'

#=====================================================================
#  The main process
#=====================================================================
oparser = optparse.OptionParser()

oparser.add_option("-d", '', action='store_true', dest='act_download', default=False)
oparser.add_option("-m", '', action='store_true', dest='act_merge', default=False)
oparser.add_option("-f", '', action='store', dest='ilist', default='urls.txt')
oparser.add_option("-o", '', action='store', dest='ofile',default='out.mp4')

(options, args) = oparser.parse_args()

if len(args) > 0 :
    ifile = args[0]
else :
    ifile = options.ilist

fh = open(ifile, "r")
filelist = []
for line in fh :
    f = line.rstrip('\r\n')
    i = f.rfind('/')
    if i < 0 :
        exit(1)
    filelist.append((f, f[i+1:], "%d.ts" % len(filelist)))
fh.close()

if options.act_download :
    for f,b,t in filelist :
        if os.path.exists(b) :
            continue
        cl_args = ('wget', '--connect-timeout=10', '--read-timeout=10', f)
        ret = subprocess.call(cl_args)
        if ret :
            exit(1)

n = 1
concat_params = 'concat'
if options.act_merge :
    for f,b,t in filelist :
#        print b
        if n == 1 :
            concat_params += ':'
        else :
            concat_params += '|'
        concat_params += t
        cl = '%s -i %s -c copy -bsf:v h264_mp4toannexb -f mpegts %s' % (gFFMPEG, b, t)
        cl_args = cl.split()
        ret = subprocess.call(cl_args)
        if ret :
            exit(1)
        n += 1

#print concat_params
#exit(0)

for i in range(1, 1+len(filelist)) :
    a = '%d.ts' % i
    if not os.path.exists(a) :
        print >>sys.stderr, "%s does not exist" % a
        exit(1)

cl_args = [gFFMPEG, '-i', concat_params,  '-bsf:a', 'aac_adtstoasc', '-codec', 'copy', options.ofile]
print ' '.join(cl_args)
ret = subprocess.call(cl_args)

