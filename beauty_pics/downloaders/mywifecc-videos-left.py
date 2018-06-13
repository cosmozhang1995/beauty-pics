# -*- coding: utf-8 -*-
import re
import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))
from config import user_config, UserConfig
import requests
import progressbar
import traceback

rooturl = user_config.get("mywifecc", "root_url")
saving_dir = user_config.get("mywifecc", "saving_dir")
username = user_config.get("mywifecc", "username")
password = user_config.get("mywifecc", "password")
info_filename = user_config.get("mywifecc", "info_filename")

dirs = os.listdir(saving_dir)

sess = requests.session()
sess.post(rooturl + "/login/comp", { "login_id": username, "passwd": password })

prgbar = None
tmpfile = None

total = 0
downloaded = 0

for dirname in dirs:
  info = UserConfig(os.path.join(saving_dir, dirname, info_filename))
  number = info.get("number")
  pageurl = info.get("pageurl")
  def parse_videourl(url):
    if url is None:
      return url
    if re.match(r"^(http|https)://.*", url) is None:
      url = rooturl + re.sub(r"^/+", "", url)
    return url
  videourl1 = parse_videourl(info.get("video"))
  videourl2 = parse_videourl(info.get("video2"))
  for videourl in [videourl1, videourl2]:
    if videourl is None:
      continue
    r = sess.head(videourl, allow_redirects=True)
    filename = re.match(r"^.*\/([^\/]+)$", r.url).group(1).lower()
    filepath = os.path.join(saving_dir, dirname, filename)
    total += 1
    if os.path.exists(filepath):
      downloaded += 1


print "%d of %d videos downloaded" % (downloaded, total)
