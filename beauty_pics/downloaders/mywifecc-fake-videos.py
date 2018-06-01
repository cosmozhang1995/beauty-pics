# -*- coding: utf-8 -*-
import re
import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))
from config import user_config, UserConfig

rooturl = user_config.get("mywifecc", "root_url")
saving_dir = user_config.get("mywifecc", "saving_dir")
info_filename = user_config.get("mywifecc", "info_filename")

dirs = os.listdir(saving_dir)

videodir = "G:\\Downloads\\MyWife.cc"

videos = os.listdir(videodir)

def standard_name(url):
  name = re.match(r"^(.*\/)?([^\/]+)\.[\w\d]+$", url).group(2).lower()
  name = re.sub(r"_\d+(m|k)$", "", name)
  return name

for i in xrange(len(videos)):
  videos[i] = (videos[i], standard_name(videos[i]))

for dirname in dirs:
  info = UserConfig(os.path.join(saving_dir, dirname, info_filename))
  egvideourl = info.get("egvideo")
  if "nakazawa" in egvideourl:
    print dirname
  standardegvideo = standard_name(egvideourl)
  matchedvideo = filter(lambda item: item[1] == standardegvideo, videos)
  if len(matchedvideo) > 0:
    videos = filter(lambda item: item[1] != standardegvideo, videos)
    file = open(os.path.join(saving_dir, dirname, matchedvideo[0][0]), "w")
    file.write("fake")
    file.close()

print "Didn't match:"

for video in videos:
  print video[0]
