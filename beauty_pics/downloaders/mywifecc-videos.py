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

debug = False
debug_numbers = [604]
debug_no_download = True

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
  if debug and not number in debug_numbers:
    continue
  for videourl in [videourl1, videourl2]:
    if videourl is None:
      continue
    try:
      r = sess.head(videourl, allow_redirects=True)
      filename = re.match(r"^.*\/([^\/]+)$", r.url).group(1)
      filepath = os.path.join(saving_dir, dirname, filename)
      if filename.lower() in map(lambda x: x.lower(), os.listdir(os.path.join(saving_dir, dirname))):
        continue
      tmpfilepath = filepath + ".download"
      tmpfile = open(tmpfilepath, "wb")
      r = sess.get(videourl, stream=True)
      totallen = int(r.headers['Content-Length'])
      receivedlen = 0
      print "Downloading the video for %s" % pageurl
      if debug and debug_no_download:
        continue
      prgbar = progressbar.ProgressBar(max_value=totallen, widgets = [
        "%-20s" % (filename),
        progressbar.Bar(),
        " ",
        progressbar.Percentage(),
        " ",
        progressbar.ETA(),
        " ",
        progressbar.FileTransferSpeed(),
        " ",
        progressbar.DataSize("value"),
        "/",
        progressbar.DataSize("max_value")
      ])
      for chunk in r:
        receivedlen += len(chunk)
        tmpfile.write(chunk)
        prgbar.update(receivedlen)
      tmpfile.close()
      tmpfile = None
      prgbar.finish()
      prgbar = None
      os.rename(tmpfilepath, filepath)
    except Exception, e:
      # print "[Error] Something went wrong when downloading the file"
      traceback.print_exc()
      if not tmpfile is None:
        tmpfile.close()
        tmpfile = None
      if not prgbar is None:
        progressbar.streams.flush()
        prgbar = None
