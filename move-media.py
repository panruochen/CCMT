#!/usr/bin/env python3
import re, os, sys, glob, subprocess, codecs
import getopt, shutil

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC

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

def usage() :
    print("Usage: %s --from-dir=FROM_DIR --to-dir=TO_DIR [--duration=DURATION] [--bitrate=BITRATE]" % sys.argv[0], file=sys.stderr)
    print("""
        Reclaim high quality media files with a mininal bitrate BITRATE and duration DURATION
        from FROM_DIR to TO_DIR""" , file=sys.stderr)

#===========================================================================
# Main
#===========================================================================

sv_min_duration = 60
sv_min_bitrate  = 192000
sv_target_dir   = None
sv_source_dir   = None

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "b:d:t:f:", (['bitrate=', 'duration=', 'from-dir=', 'to-dir=']))
except getopt.GetoptError as err:
    print(str(err))
    sys.exit(2)

for o, a in opts:
    if o == "-d" or o == '--duration':
        sv_min_duration = int(a)
    elif o == "-b" or o == '--bitrate':
        sv_min_bitrate = int(a)
    elif o == '-f' or o == '--from-dir':
        sv_source_dir = a
    elif o == '-t' or o == '--to-dir':
        sv_target_dir = a
    else:
        raise Exception("Unknown option " + o)

count = 0
media = None
medialist = []

mp = MediaProbeMutagen()

if sv_source_dir is None or sv_target_dir is None :
    usage()
    exit(0)

for root,dirs,files in os.walk(sv_source_dir) :
    for f in files :
        count += 1
        file = root + '/' + f
#        print("Processing %06u %s" % (count,file))
        media = mp.get_info(file)
        if media is not None :
            medialist.append(media)

print("%u media files are found from %u files\n" % (len(medialist),count))
tr_table = { ord('"') : ' ', ord("'"):' ', ord('/'):' ', ord('\\'):' ', ord(':'):' ' };
for media in medialist :
    if media.duration >= sv_min_duration and media.bitrate >= sv_min_bitrate : #and media.title is not None :
        if media.title.string is not None :
            target_name = sv_target_dir + '/' + media.title.string.translate(tr_table) + '.' + media.type
        else :
            target_name = sv_target_dir + '/' + os.path.basename(media.name) + '.' + media.type
        if should_move(media.name, target_name) :
            print("Move %s to %s" % (media.name, target_name))
            media.dump()
            try:
                shutil.move(media.name, target_name)
            except:
                print('Ignore %s' % media.name)
        else :
            print("Target file \"%s\" exists." % target_name)
