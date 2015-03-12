#!/usr/bin/env python3
import re, os, sys, glob, subprocess, codecs
import getopt, shutil

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC


FF_PROBE   = 'd:/Tools/ffmpeg/bin/ffprobe'

PROBER = 'mutagen'
#PROBER == 'ffprobe'

#################################################################################
class xencoding :
    def __init__(self) :
        self.rawbytes = None
        self.encoding = None
        self.string   = None
    def set(self, b, e = 'utf-8') :
        self.rawbytes = b
        self.string =self.rawbytes.decode(e)
        self.encoding = e
    def iconv(self, e) :
        try:
            self.string = codecs.decode(self.rawbytes, 'utf-8').encode(e).decode('utf-8')
            self.encoding = e
            return True
        except :
            self.string = '<??>'
            self.encoding = None
#        print(codecs.decode(b'\xc3\xafL\xc3\x96\xc3\x90\xc3\x8a\xc3\x98\xc2\xba\xc3\xb2\xc3\x8a\xc3\x95\xc2\xb2\xc3\x98','utf-8').encode('utf_7').decode('utf-8'))
        return False

class Media :
    def __init__(self) :
        self.name     = None
        self.type     = None
        self.artist   = xencoding()
        self.title    = xencoding()
        self.bitrate  = None
        self.duration = None
    def valid(self) :
        return (self.name is not None) and (self.type is not None) and (self.bitrate is not None) and (self.duration is not None)

    def guess_encoding(self, xe) :
        languages = [ 'utf_7', 'big5', 'gbk' ]
        for l in languages :
            if xe.iconv(l) :
               return True
        return False

    def dump(self):
        print("%s: %s" % (self.name, self.type))
        try:
            print("  Artist: %s" % (self.artist.string))
        except UnicodeEncodeError:
            self.guess_encoding(self.artist)
            print("  Artist: %s" % (self.artist.string))
        try:
            print("  Title:  %s" % (self.title.string))
        except UnicodeEncodeError:
            self.guess_encoding(self.title)
            print("  Title: %s" % (self.title.string))

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

    def get_id3_info(self, id3, key) :
        if key in id3 :
            return id3[key]
        else :
            return None

    def get_info(self, file) :
        id3 = None
        type  = None
        media = None
        try :
            id3 = MP3(file)
            media = Media()
            media.type     = 'mp3'
            media.name     = file
            media.duration = id3.info.length
            media.bitrate  = id3.info.bitrate
            media.title.set(bytes(id3['TIT2']))
            media.artist.set(bytes(id3['TPE1']))
#            print(media.title.rawbytes)
#            print(media.artist.rawbytes)
        except :
            pass

        if media is None :
            try :
                audio = FLAC(file)
                type = 'flac'
            except :
                pass

        return media

def should_move(s, d) :
    if not os.path.exists(d) :
        return True
    try :
        if os.stat(s).st_size > os.stat(d).st_size :
            return True
    except:
        pass
    return False

#===========================================================================
# Main
#===========================================================================

sv_min_duration = 60
sv_min_bitrate  = 192000
sv_target_dir   = None
sv_source_dir   = None

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "d:t:f:", (['duration=', 'from-dir=', 'to-dir=']))
except getopt.GetoptError as err:
    print(str(err))
    sys.exit(2)

for o, a in opts:
    if o == "-d" or o == '--duration':
        sv_min_duration = int(a)
    elif o == '-f' or o == '--from-dir':
        sv_source_dir = a
    elif o == '-t' or o == '--to-dir':
        sv_target_dir = a
    else:
        raise Exception("Unknown option " + o)

state = -1
count = 0
media = None
medialist = []

if PROBER == 'mutagen' :
    mp = MediaProbeMutagen()
elif PROBER == 'ffprobe' :
    mp = MediaProbeFfprobe()

if sv_source_dir is None or sv_target_dir is None :
    exit(0)

for root,dirs,files in os.walk(sv_source_dir) :
    for f in files :
        count += 1
        file = root + '/' + f
#        print("Processing %06u %s" % (count,file))
        media = mp.get_info(file)
        if media is not None :
            medialist.append(media)

print("%u media files reclaimed from %u cached files\n" % (len(medialist),count))
tr_table = { ord('"') : ' ', ord("'"):' ', ord('/'):' ', ord('\\'):' ', ord(':'):' ' };
for media in medialist :
    if media.duration >= sv_min_duration and media.bitrate >= sv_min_bitrate : #and media.title is not None :
        target_name = sv_target_dir + '/' + media.title.string.translate(tr_table) + '.' + media.type
        if should_move(media.name, target_name) :
            print("Move %s to %s" % (media.name, sv_target_dir))
            media.dump()
            shutil.move(media.name, target_name)
        else :
            print("Target file \"%s\" exists." % target_name)
