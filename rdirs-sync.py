#!/usr/bin/env python

# Synchronize contents of a remote directory with its local counterpart

import os, sys, subprocess

class SshAgent :
    def __init__(self, host) :
        self.host = host

    def prun(self, cmdline) :
        args = ['ssh', self.host, cmdline]
        sp = subprocess.Popen(args, stdout=subprocess.PIPE)
        results, errors = sp.communicate()
        if sp.returncode != 0 :
            return sp.returncode,None
        return sp.returncode,results

    def check_call(self, cmdline) :
        args = ['ssh', self.host, cmdline]
        subprocess.check_call(args)

class FileTransferAgent :
    RDIFF = 1
    SCP   = 2

    def __init__(self, ssh, remote_dir, local_dir) :
        self.ssh = ssh
        self.remote_dir = remote_dir
        self.local_dir  = local_dir

    def sync_by_rdiff(self, filename, remote_tmpdir) :
        if not remote_tmpdir.endswith('/') :
            remote_tmpdir += '/'
        local_dir = self.local_dir
        if not local_dir.endswith('/') :
            local_dir += '/'

        sourceFile   = local_dir + filename
        localSigFile = local_dir + 'a.Sig'
        localDelFile = local_dir + 'a.Del'
        destFile      = self.remote_dir + '/' + filename
        remoteSigFile = remote_tmpdir + 'a.Sig'
        remoteDelFile = remote_tmpdir + 'a.Del'
        tmpFile = local_dir + 'a.Tmp'

        subprocess.check_call(['rdiff', 'signature', '-H', 'md4', sourceFile, localSigFile])
        subprocess.check_call(['scp', '-q', localSigFile, ssh.host + ':' + remoteSigFile])
        ssh.check_call('rdiff delta %s %s %s' % (remoteSigFile, destFile, remoteDelFile))
        subprocess.check_call(['scp', '-q', ssh.host + ':' + remoteDelFile, localDelFile])
        subprocess.check_call(['rdiff', 'patch', sourceFile, localDelFile, tmpFile])

        os.remove(sourceFile)
        os.rename(tmpFile, sourceFile)
        os.remove(localSigFile)
        os.remove(localDelFile)
        ssh.check_call('rm -f %s %s' % (remoteDelFile, remoteSigFile))

    def sync_by_scp(self, filename) :
        subprocess.check_call(['scp', ssh.host + ':' + self.remote_dir + '/' + filename, self.local_dir + '/' + filename])

    def sync(self, method, filename, remote_tmpdir) :
        sys.stdout.write("%-60s" % filename)
        if method == self.RDIFF :
            self.sync_by_rdiff(filename, remote_tmpdir)
        elif method == self.SCP :
            self.sync_by_scp(filename)
        sys.stdout.write('OK\n')

class Md5Agent :
    def __init__(self, ssh, remote_dir, local_dir) :
        self.ssh = ssh
        self.remote_dir = remote_dir
        self.local_dir  = local_dir
        self.local_md5  = dict()
        self.remote_md5 = None

    @staticmethod
    def parse_results(self, results) :
        md5sum = dict()
        for line in results.split('\n') :
            a = line.rstrip('\r\n').split()
            if len(a) < 2 :
                continue
            f = a[1][1:]
            s = a[0]
            md5sum[f] = s
        return md5sum

    def get_files_to_be_updated(self) :
        self.local_md5_sums()
        self.remote_md5_sums()
        return self.dict_diff(self.remote_md5, self.local_md5)

    @staticmethod
    def dict_diff(a, b) :
        z1 = dict()
        z2 = dict()
        for x in a :
            if (x not in b) :
                z2[x] = a[x]
            elif (a[x] != b[x]) :
                z1[x] = a[x]
        return z1,z2

    @staticmethod
    def dump(d) :
        for a in d :
            print "%s %s" % (a, d[a])

    def local_md5_sums(self) :
        files = os.listdir(self.local_dir)
        if len(files) > 0 :
            args = ['md5sum', '-b'] + files
            sp = subprocess.Popen(args, cwd=self.local_dir, stdout=subprocess.PIPE)
            results, errors = sp.communicate()
            if sp.returncode != 0 :
                raise Exception("Cannot get local md5 sums from %s" % self.local_dir)
            self.local_md5 = self.parse_results(self, results)

    def remote_md5_sums(self) :
        cmdline = 'cd %s && md5sum -b *' % self.remote_dir
        ret,results = ssh.prun(cmdline)
        if ret != 0 :
            raise Exception("Cannot get remote md5 sums from %s" % self.remote_dir)
        self.remote_md5 = self.parse_results(self, results)


#===============================================================================
#  The main function starts here
#===============================================================================
gv_local_ufs = os.environ['MY_UFS']
if not gv_local_ufs :
    print >> sys.stderr, "MY_UFS not set"
    exit(2)

amss1 = os.environ['AMSS1']
if not amss1 :
    print >> sys.stderr, "AMSS1 not set"
    exit(2)
gv_remote_ufs = amss1 + '/release/ufs'
a = gv_remote_ufs.split(':')
remote_host = a[0]
remote_dir = a[1]

ssh  = SshAgent(remote_host)
sync = FileTransferAgent(ssh, remote_dir, gv_local_ufs)
mmgr = Md5Agent(ssh, remote_dir, gv_local_ufs)

d1,d2 = mmgr.get_files_to_be_updated()
##mmgr.dump(mmgr.local_md5)
##print
##mmgr.dump(mmgr.remote_md5)
#exit(0)

print "Syncing %u files from remote server" % (len(d1) + len(d2))
if len(d1) + len(d2) > 0 :
    for x in d1 :
        sync.sync(FileTransferAgent.RDIFF, x, '/tmp')
    for x in d2 :
        sync.sync(FileTransferAgent.SCP, x, None)

    d1,d2 = mmgr.get_files_to_be_updated()
    if len(d1) + len(d2) > 0 :
        print >>sys.stderr, "Syncing failed !! %u files remain unsync"
        exit(2)
