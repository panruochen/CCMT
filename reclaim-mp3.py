#!/usr/bin/env python3
import re, os, sys, glob, subprocess, codecs

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC


FF_PROBE   = 'd:/Tools/ffmpeg/bin/ffprobe'
CACHE2_DIR = 'd:/PersonalConfigs/firefox-profiles/cache2/entries'
#CACHE2_DIR = 'c:/Tools/Mozilla Firefox/configs/PRC/cache2/entries'

PROBER = 'mutagen'
#PROBER == 'ffprobe'

#################################################################################
class Media :
    def __init__(self) :
        self.name     = None
        self.type     = None
        self.artist   = None
        self.title    = None
        self.bitrate  = None
        self.duration = None
    def valid(self) :
        return (self.name is not None) and (self.type is not None) and (self.bitrate is not None) and (self.duration is not None)
    def iconv(self, s) :
        if type(s).__name__ == 'list' :
            s1 = ''
            for i in s :
                s1 += i
        elif type(s).__name__ == 'str' :
            s1 = s
        else :
            raise Exception("Invalid type")
        s1 = codecs.encode(s1, 'ascii', 'ignore')
        for i in ['big5', 'gbk', 'gb2312', 'gb18030'] :
            s2 = None
            try :
                s2 = s1.decode(i)
            except:
                pass
            if s2 is not None :
                print("String decoded as %s" % i, file=sys.stderr)
                break
        return s2

    def dump(self):
        print("%s: %s" % (self.name, self.type))
        try :
            print("  Artist: %s" % (self.artist))
        except UnicodeEncodeError:
            print("  Artist: %s" % self.iconv(self.artist))
        try:
            print("  Title:  %s" % (self.title))
        except UnicodeEncodeError:
            print("  Title: %s" % self.iconv(self.title))
        print("  Duration:  %s" % (self.duration))
        print("  Bitrate:  %s\n" % (self.bitrate))


class MediaProbe :
    def __init__(self):
        pass
    def get_info(self, file):
        pass

class MediaProbeFFMPEG(MediaProbe) :
    def __init__(self) :
        MediaProbe.__init__(self)
    def run_ffprobe(file) :
        msg = None
        sp = subprocess.Popen([FF_PROBE, '-hide_banner', '-i', file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = sp.communicate()
        if sp.returncode == 0 and err is not None :
            try:
                msg = err.decode('utf-8')
            except:
                msg = err.decode('ascii')
        return sp.returncode, msg

    def get_info(self, file):
        media = None
        ret, msg = run_ffprobe(file)
        if ret == 0 and msg[0] != '[' :
            for line in msg.split('\n'):
                fx = line.split(',')
                if len(fx) >= 3 and fx[0] == 'Input #0' :
                    fx[1] = fx[1].strip()
                    if fx[1] in ('jpeg_pipe', 'png_pipe', 'gif') :
                        pass
                    elif fx[1] == 'mp3' :
                        media = Media()
                        media.type = 'mp3'
                        c = fx[2].split("'")
                        media.name = c[1]
                        state = 0
    #                else :
    #                    print(msg, '\n')
                elif state == 0 :
                    fx = line.split(':')
                    if len(fx) >= 1 :
                        fx[0] = fx[0].strip()
                        if fx[0] == 'Duration' :
                            fx = line.split()
                            media.duration = fx[1].rstrip(',')
                            media.bitrate = fx[5]
                            state = -1
                            break
                        elif fx[0] == 'artist' :
                            media.artist = fx[1].strip()
                        elif fx[0] == 'title' :
                            media.title = fx[1].strip()
        return media

class MediaProbeMutagen(MediaProbe) :
    def __init__(self) :
        MediaProbe.__init__(self)
    def get_info(self, file) :
        audio = None
        type  = None
        try :
            audio = MP3(file, ID3=EasyID3)
            type = 'mp3'
        except :
            pass

        if audio is None :
            try :
                audio = FLAC(file)
                type = 'flac'
            except :
                pass

        media = None
        if audio is not None :
            media = Media()
            media.duration = audio.info.length
            media.bitrate  = audio.info.bitrate
            if 'title' in audio :
                media.title    = audio['title']
            if 'artist' in audio :
                media.artist   = audio['artist']
            media.name     = file
            media.type     = type
        return media

state = -1
count = 0
media = None
medialist = []

if PROBER == 'mutagen' :
    mp = MediaProbeMutagen()
elif PROBER == 'ffprobe' :
    mp = MediaProbeFfprobe()


"""
filelist = []
#for root,dirs,files in os.walk('d:/DevTools/global5.82') :
for root,dirs,files in os.walk('d:/Media/==Music==') :
    print(root)
    print(dirs)
    print(files)
    filelist += [root + f for f in files]
    filelist += []
print("Totally %u files" % len(filelist))
exit(0)
"""

CACHE2_DIR = 'd:/Media/==Music=='
#CACHE2_DIR = 'd:/tmp'
for root,dirs,files in os.walk(CACHE2_DIR) :
    for f in files :
        count += 1
        file = root + '/' + f
        print("Processing %06u %s" % (count,file))
        media = mp.get_info(file)
        if media is not None :
            medialist.append(media)

print("%u media files reclaimed from %u cached files\n" % (len(medialist),count))

for media in medialist :
    media.dump()
