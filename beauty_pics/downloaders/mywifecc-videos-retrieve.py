# -*- coding: utf-8 -*-
import re
import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))
from config import user_config, UserConfig
import ftplib
import progressbar
import traceback

retrieve_server = user_config.get("mywifecc", "retrieve_server")
retrieve_remote_dir = user_config.get("mywifecc", "retrieve_remote_dir")
retrieve_local_dir = user_config.get("mywifecc", "retrieve_local_dir")
retrieve_username = user_config.get("mywifecc", "retrieve_username")
retrieve_password = user_config.get("mywifecc", "retrieve_password")

def make_retrdirlist_callback(save_list, file_filter = None):
  # file_filter: function (props, filename) -> Boolean
  def retrdirlist_callback(line):
    # print line
    mc = re.match(r"([\w\-]{10})\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\S+\s+\S+\s+\S+)\s+(\S.*)", line)
    if not mc is None:
      props = mc.group(1)
      filename = mc.group(7)
      if file_filter is None or file_filter(props, filename):
        save_list.append(filename)
    else:
      raise "didn't find pattern in \"%s\"" % line
  return retrdirlist_callback

ftp = ftplib.FTP(retrieve_server)
ftp.login(retrieve_username, retrieve_password)
ftp.cwd(retrieve_remote_dir)
dirs = []
ftp.dir(".", make_retrdirlist_callback(dirs))

prgbar = None
tmpfile = None

def on_exception():
  # print "[Error] Something went wrong when downloading the file"
  traceback.print_exc()
  if not tmpfile is None:
    tmpfile.close()
    tmpfile = None
  if not prgbar is None:
    progressbar.streams.flush()
    prgbar = None
  try:
    ftp.quit()
  except:
    pass
  try:
    ftp.close()
  except:
    pass
  ftp = ftplib.FTP(retrieve_server)
  ftp.login(retrieve_username, retrieve_password)
  ftp.cwd(retrieve_remote_dir)

for dirname in dirs:
  try:
    local_dir = os.path.join(retrieve_local_dir, dirname)
    if not os.path.exists(local_dir):
      os.makedirs(local_dir)
    ftp.cwd(dirname)
    filenames = []
    def filename_filter(props, filename):
      return filename.split(".")[-1] in ["mp4"]
    ftp.dir(".", make_retrdirlist_callback(filenames, filename_filter))
    for filename in filenames:
      try:
        filepath = os.path.join(retrieve_local_dir, dirname, filename)
        if os.path.exists(filepath):
          continue
        totallen = ftp.size(filename)
        receivedlen = 0
        tmpfilepath = filepath + ".download"
        tmpfile = open(tmpfilepath, "wb")
        print "Retrieving %s/%s" % (dirname, filename)
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
        retrfilecallback_dict = {
          "receivedlen": receivedlen,
          "tmpfile": tmpfile,
          "prgbar": prgbar
        }
        def retrfilecallback(chunk):
          retrfilecallback_dict['receivedlen'] += len(chunk)
          retrfilecallback_dict['tmpfile'].write(chunk)
          retrfilecallback_dict['prgbar'].update(retrfilecallback_dict['receivedlen'])
        ftp.retrbinary("RETR %s" % filename, retrfilecallback)
        receivedlen = retrfilecallback_dict['receivedlen']
        tmpfile.close()
        tmpfile = None
        prgbar.finish()
        prgbar = None
        os.rename(tmpfilepath, filepath)
      except Exception, e:
        on_exception()
        raise e
    ftp.cwd("..")
  except Exception, e:
    on_exception()
    raise e

ftp.quit()
ftp.close()
