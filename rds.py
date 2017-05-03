#!/usr/bin/env python
# Synchronize contents of a remote directory with its local counterpart

import os, sys, subprocess
import ConfigParser, optparse

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
    RSYNC   = 2

    def __init__(self, ssh, remote_dir, local_dir) :
        self.ssh = ssh
        self.remote_dir = remote_dir
        self.local_dir  = local_dir

    def copy_via_rdiff(self, filename, remote_tmpdir) :
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
        subprocess.check_call(['rsync', '-q', localSigFile, ssh.host + ':' + remoteSigFile])
        ssh.check_call('rdiff delta %s %s %s' % (remoteSigFile, destFile, remoteDelFile))
        subprocess.check_call(['rsync', '-q', ssh.host + ':' + remoteDelFile, localDelFile])
        subprocess.check_call(['rdiff', 'patch', sourceFile, localDelFile, tmpFile])

        os.remove(sourceFile)
        os.rename(tmpFile, sourceFile)
        os.remove(localSigFile)
        os.remove(localDelFile)
        ssh.check_call('rm -f %s %s' % (remoteDelFile, remoteSigFile))

    def copy_via_rsync(self, filename) :
        subprocess.check_call(['rsync', ssh.host + ':' + self.remote_dir + '/' + filename, self.local_dir + '/' + filename])

    def sync(self, method, filename, remote_tmpdir) :
        sys.stdout.write("%-60s" % filename)
        if method == self.RDIFF :
            self.copy_via_rdiff(filename, remote_tmpdir)
        elif method == self.RSYNC :
            self.copy_via_rsync(filename)
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
# create the options parser
optionsparser = optparse.OptionParser()

# define the options we require/support
optionsparser.add_option("-f", "--force", dest="force", help="Copy all remote subdirectories and files to local", default=False)
optionsparser.add_option("-d", "--use-rdiff", dest="rdiff", help="Use rdiff for file transfer", default=False)

# parse the options
(options, args) = optionsparser.parse_args()

config = ConfigParser.ConfigParser()

rds_conf  = ".rds.conf"
section   = 'parameters'
conf_dir  = None
conf_file = None
gv_local_dir   = None
gv_remote_host = None
gv_remote_dir  = None

for conf_dir in ('.', os.environ['HOME']):
    conf_file = conf_dir + '/' + rds_conf
    if os.path.exists(conf_file) :
        config.read(conf_file)
        gv_local_dir   = config.get(section, "local_dir", os.getcwd())
        gv_remote_host = config.get(section, "remote_host")
        gv_remote_dir  = config.get(section, "remote_dir")
        break
    conf_file = None

if not conf_file :
    print >>sys.stderr, rds_conf + " is not found"
    exit(2)

if (not gv_local_dir) or (not gv_remote_host) or (not gv_remote_dir) :
    print >>sys.stderr, 'All of "local_dir", "remote_host" and "remote_dir" must be set in "' + file + '"'
    exit(2)

#print "LOCAL_DIR:   %s" % gv_local_dir
#print "REMOTE_HOST: %s" % gv_remote_host
#print "REMOTE_DIR:  %s" % gv_remote_dir

os.chdir(gv_local_dir)

ssh  = SshAgent(gv_remote_host)
fta  = FileTransferAgent(ssh, gv_remote_dir, gv_local_dir)
mmgr = Md5Agent(ssh, gv_remote_dir, gv_local_dir)

d1,d2 = mmgr.get_files_to_be_updated()
##mmgr.dump(mmgr.local_md5)
##print
##mmgr.dump(mmgr.remote_md5)
#exit(0)

print "%u files to be transferred from %s" % (len(d1) + len(d2), gv_remote_host)
if len(d1) + len(d2) > 0 :
    if options.rdiff:
      for x in d1 :
        fta.sync(FileTransferAgent.RDIFF, x, '/tmp')
    else:
      for x in d1 :
        fta.sync(FileTransferAgent.RSYNC, x, None)
    for x in d2 :
      fta.sync(FileTransferAgent.RSYNC, x, None)

    # Verify
    d1,d2 = mmgr.get_files_to_be_updated()
    if len(d1) + len(d2) > 0 :
        print >>sys.stderr, "Synchronization fails! %u files remain."
        exit(2)
