# -*- coding: utf-8 -*-
import re
import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))
from config import user_config, UserConfig

saving_dir = user_config.get("mywifecc", "saving_dir")

dirs = os.listdir(saving_dir)
dirs = filter(lambda dirname: os.path.isdir(os.path.join(saving_dir, dirname)), dirs)

for dirname in dirs:
  filenames = os.listdir(os.path.join(saving_dir, dirname))
  filenames = filter(lambda fname: re.match(r"^.*\.(mp4)$", fname.lower()), filenames)
  for filename in filenames:
    print "%s/%s" % (dirname, filename)

