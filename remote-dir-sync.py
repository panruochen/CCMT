#!/usr/bin/env python

import os, sys, subprocess

def get_md5sums(args, shell, fake_dir) :
    sp = subprocess.Popen(args, shell=shell, stdout=subprocess.PIPE)
    results, errors = sp.communicate()
    if sp.returncode != 0 :
        print >> sys.stderr, "Cannot get local md5 sums from %s" % fake_dir
    md5sum = dict()
    for line in results.split('\n') :
        a = line.rstrip('\r\n').split()
        if len(a) < 2 :
            continue
        f = a[1][1:]
        s = a[0]
        md5sum[f] = s
    return md5sum

def run_md5sum_locally() :
    cmdline = 'cd %s && md5sum -b *' % local_ufs
    return get_md5sums(cmdline, True, local_ufs)

def run_md5sum_remotely(host, remote_dir, amss1) :
    args = ['ssh', host, 'cd %s && md5sum -b *' % remote_dir]
    return get_md5sums(args, False, amss1)

def dict_get_diff(a, b) :
    c = dict()
    for x in a :
        if (x not in b) or (a[x] != b[x]) :
            c[x] = a[x]
    return c

local_ufs = os.environ['MY_UFS']
if not local_ufs :
    print >> sys.stderr, "MY_UFS not set"
    exit(2)

amss1 = os.environ['AMSS1']
if not amss1 :
    print >> sys.stderr, "AMSS1 not set"
    exit(2)
remote_ufs = amss1 + '/release/ufs'
a = remote_ufs.split(':')
host = a[0]
remote_dir = a[1]

local_md5sums  = run_md5sum_locally()
remote_md5sums = run_md5sum_remotely(host, remote_dir, amss1)
c = dict_get_diff(remote_md5sums, local_md5sums)

print "Syncing %u files from remote server" % len(c)
if len(c) > 0 :
    for x in c :
        args = ['scp', remote_ufs + '/' + x, local_ufs + '/' + x]
        print args
        sp = subprocess.check_call(args)
