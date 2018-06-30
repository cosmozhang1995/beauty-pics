# -*- coding: utf-8 -*-
import re
import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))
from config import user_config, UserConfig

retrieve_local_dir = user_config.get("mywifecc", "retrieve_local_dir")
retrieve2_rooturl = user_config.get("mywifecc", "retrieve2_rooturl")
retrieve2_listfile = user_config.get("mywifecc", "retrieve2_listfile")
with open(retrieve2_listfile) as file:
  retrieve2_listfile = file.read()

ndownloaded = 0
ntotal = 0

for line in retrieve2_listfile.split("\n"):
  line = line.strip()
  if len(line) == 0: continue
  remote_url = retrieve2_rooturl + line
  filename = line.split("/")[-1]
  filepath = os.path.realpath(os.path.join(retrieve_local_dir, line))
  if os.path.exists(filepath):
    ndownloaded += 1
  ntotal += 1

print "%d of %d videos retrieved" % (ndownloaded, ntotal)
