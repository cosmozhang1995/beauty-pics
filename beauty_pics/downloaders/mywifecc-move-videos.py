# -*- coding: utf-8 -*-
import re
import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))
from config import user_config, UserConfig

rooturl = user_config.get("mywifecc", "root_url")
saving_dir = user_config.get("mywifecc", "saving_dir")
saving_dir = "G:\\Downloads\\MyWife.cc-pics"
info_filename = user_config.get("mywifecc", "info_filename")

dirs = os.listdir(saving_dir)
dirs = filter(lambda dirname: os.path.isdir(os.path.join(saving_dir, dirname)), dirs)

videodir = "G:\\Downloads\\MyWife.cc"

videos = os.listdir(videodir)

def en_name(url):
  name = url.split("/")[-1].split(".")[0].lower()
  name = re.sub(r"_\d+(m|k)", "", name)
  name = re.sub(r"_saikai", "", name)
  name = re.sub(r"_$", "", name)
  return name

for i in xrange(len(videos)):
  videos[i] = (videos[i], en_name(videos[i]))

for dirname in dirs:
  info = UserConfig(os.path.join(saving_dir, dirname, info_filename))
  print dirname
  egvideourl = info.get("egvideo")
  if egvideourl is None: continue
  the_enname = en_name(egvideourl)
  matched_videos = filter(lambda x: x[1] == the_enname, videos)
  videos = filter(lambda x: x[1] != the_enname, videos)
  for mvideo in matched_videos:
    os.rename(os.path.join(videodir, mvideo[0]), os.path.join(saving_dir, dirname, mvideo[0]))

print "Didn't match:"

for video in videos:
  print video[0]
