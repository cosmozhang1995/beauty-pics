# -*- coding: utf-8 -*-
import re
import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))
from config import user_config, UserConfig
import requests
import progressbar
import traceback

retrieve_local_dir = user_config.get("mywifecc", "retrieve_local_dir")
retrieve2_rooturl = user_config.get("mywifecc", "retrieve2_rooturl")
retrieve2_listfile = user_config.get("mywifecc", "retrieve2_listfile")
with open(retrieve2_listfile) as file:
  retrieve2_listfile = file.read()

prgbar = None
tmpfile = None

for line in retrieve2_listfile.split("\n"):
  line = line.strip()
  if len(line) == 0: continue
  remote_url = retrieve2_rooturl + line
  filename = line.split("/")[-1]
  filepath = os.path.realpath(os.path.join(retrieve_local_dir, line))
  try:
    r = sess.head(videourl, allow_redirects=True)
    if os.path.exists(filepath):
      continue
    tmpfilepath = filepath + ".download"
    tmpfile = open(tmpfilepath, "wb")
    r = requests.get(remote_url, stream=True)
    totallen = int(r.headers['Content-Length'])
    receivedlen = 0
    print "Downloading the video for %s" % line
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
