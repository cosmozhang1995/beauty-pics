import sys, os
import re
import codecs


class UserConfigSection:
  def __init__(self, name, dic):
    self.name = name
    self.dic = dic

  # def __getattr__(self, name):
  #   if name in self.dic:
  #     return self.dic[name]
  #   else:
  #     raise Exception("Cannot find property <%s>" % name)

  # def __setattr__(self, name, value):
  #   if not name == "dic" and not name == "name":
  #     self.dic[name] = value

class UserConfig:
  def __init__(self, filename = None):
    dic = {"root": {}}
    if not filename is None:
      file = open(filename)
      content = file.read()
      file.close()
      lines = content.split("\n")
      secname = "root"
      for line in lines:
        m = re.match(r"\[([\w\d_]+)\]", line)
        if not m is None:
          secname = m.group(1)
          if not secname in dic:
            dic[secname] = {}
          continue
        m = re.match(r"([\w\d_]+)\s*\=(.*)", line)
        if not m is None:
          propname = m.group(1)
          propval = m.group(2)
          propval = propval.strip()
          m = re.match(r"\"(.*)\"", propval)
          if not m is None:
            propval = m.group(1)
            dic[secname][propname] = propval
            continue
          m = re.match(r"\'(.*)\'", propval)
          if not m is None:
            propval = m.group(1)
            dic[secname][propname] = propval
            continue
          if not re.match(r"\d+", propval) is None:
            propval = int(propval)
            dic[secname][propname] = propval
            continue
          if not re.match(r"\d*\.\d+", propval) is None:
            propval = float(propval)
            dic[secname][propname] = propval
            continue
          if propval.lower() == "true":
            propval = True
            dic[secname][propname] = propval
            continue
          if propval.lower() == "false":
            propval = False
            dic[secname][propname] = propval
            continue
          if propval.lower() == "none":
            propval = None
            dic[secname][propname] = propval
            continue
          if propval.lower() == "null":
            propval = None
            dic[secname][propname] = propval
            continue
          dic[secname][propname] = propval
    for k in dic:
      dic[k] = UserConfigSection(k, dic[k])
    self.dic = dic

  def get(self, secname, propname = None):
    if propname is None:
      propname = secname
      secname = "root"
    return self.dic[secname].dic[propname]

  def set(self, secname, propname, propval = None):
    if propval is None:
      propval = propname
      propname = secname
      secname = "root"
    if not secname in self.dic:
      self.dic[secname] = {}
    self.dic[secname].dic[propname] = propval

  # def __getattr__(self, name):
  #   if name in self.dic:
  #     return self.dic[name]
  #   else:
  #     raise Exception("Cannot find section <%s>" % name)

  # def __setattr__(self, name, value):
  #   if not name == "dic":
  #     self.dic[name] = value

  def save(self, filename = None):
    def section_content(section):
      content = ""
      for k in section.dic:
        v = section.dic[k]
        if isinstance(v, str) or isinstance(v, unicode):
          v = '"' + v + '"'
        else:
          v = str(v)
        content += k + " = " + v + "\n"
      content += "\n"
      return content
    content = ""
    content += section_content(self.dic["root"])
    for secname in self.dic:
      if secname != "root":
        content += '[' + secname + ']' + "\n"
        content += section_content(self.dic[secname])
    if not filename is None:
      file = codecs.open(filename, "w", "utf-8")
      file.write(content)
      file.close()
    return content

user_config = UserConfig(os.path.realpath(os.path.join(os.path.dirname(__file__), "user.cfg")))