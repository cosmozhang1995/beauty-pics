# -*- coding: utf-8 -*-
import scrapy
import re
import os
from config import user_config, UserConfig
from pyquery import PyQuery as pq
import requests

rooturl = user_config.get("mywifecc", "root_url")
saving_dir = user_config.get("mywifecc", "saving_dir")
username = user_config.get("mywifecc", "username")
password = user_config.get("mywifecc", "password")
download_thumb = user_config.get("mywifecc", "download_thumb")
download_topview = user_config.get("mywifecc", "download_topview")
download_gallery = user_config.get("mywifecc", "download_gallery")
info_filename = user_config.get("mywifecc", "info_filename")
thumb_filename = user_config.get("mywifecc", "thumb_filename")
topview_filename = user_config.get("mywifecc", "topview_filename")

class MywifeccSpider(scrapy.Spider):
  name = "mywifecc"
  allowed_domains = ["mywife.cc"]

  def start_requests(self):
    # login first
    return [scrapy.FormRequest( url = rooturl + "login/comp", formdata = { "login_id": username, "passwd": password }, meta = {'cookiejar': 1}, callback = self.parse_first )]

  # def parse_login(self, response):
  #   return [scrapy.Request(rooturl, meta = {'cookiejar': response.meta['cookiejar']})]

  def parse_first(self, response):
    rootEl = pq(response.body_as_unicode())
    lastpageEl = pq(rootEl(".pagenation-btm a")[-1])
    lastpage_href = lastpageEl.attr("href")
    m = re.match(r"^(.*\=)(\d+)$", lastpage_href)
    pagequery = m.group(1)
    lastpagenum = int(m.group(2))
    print "Last page: %d" % lastpagenum
    for i in xrange(1, lastpagenum + 1):
      yield scrapy.Request( rooturl + pagequery + str(i), meta = {'cookiejar': response.meta['cookiejar']}, callback = self.parse_page )

  def parse_page(self, response):
    rootEl = pq(response.body_as_unicode())
    listEl = rootEl(".mywifeichiran .wifecon")
    for itemEl in listEl:
      anchorEl = pq(pq(itemEl)('a')[0])
      href = anchorEl.attr('href')
      portraiturl = anchorEl('img').attr('src')
      saveto = os.path.join(saving_dir, href.replace("/", "-"))
      need_crawl = False
      if not os.path.exists(saveto) or not os.path.exists(os.path.join(saveto, info_filename)):
        need_crawl = True
      else:
        allfiles = os.listdir(saveto)
        if download_thumb and not thumb_filename in allfiles:
          need_crawl = True
        elif download_topview and not topview_filename in allfiles:
          need_crawl = True
        else:
          info = UserConfig(os.path.join(saveto, info_filename))
          desired_images = info.get('desired_images')
          if download_gallery and len(filter(lambda fname: re.match(r"\d+\.(jpg|jpeg|png|gif)", fname.lower()), allfiles)) < desired_images:
            need_crawl = True
      if need_crawl:
        # If the directory does not exists, crawl it
        yield scrapy.Request( rooturl + href, meta = {
          'cookiejar': response.meta['cookiejar'],
          'href': href,
          'saveto': saveto,
          'portraiturl': portraiturl
        }, callback = self.parse )

  def parse(self, response):
    rootEl = pq(response.body_as_unicode())
    titleEl = rootEl("head title")
    titleText = titleEl.text()
    m = re.match(r"No\.(\d+)[\u3000]*([^\|]+).*", titleText)
    number = int(m.group(1))
    name = m.group(2)
    name = name.replace(u"蒼い再会", "")
    name = re.sub(u"[\u3000\s]+$", "", re.sub(u"^[\u3000\s]+", "", name))
    intro = rootEl(".modelsamplephototop").text()
    intro = intro.replace(r"^\s+", "").replace(r"\s+$", "").replace(r"\n+", "\n").replace("\n", "\\n")
    videoEl = rootEl(".modelsamplephototop #video")
    egvideourl = videoEl.attr('src')
    name_en = re.match(r"^.*\/([^\/]+)\.\w+$", egvideourl).group(1).lower()
    name_en = re.sub(r"_\d+(m|k)$", "", name_en)
    name_en = re.sub(r"_$", "", name_en)
    saikai = ("_saikai" in name_en)
    name_en = re.sub(r"_saikai$", "", name_en)
    name_en = re.sub(r"_$", "", name_en)
    name_en = re.sub(r"_+", "_", name_en)
    name_en = name_en.split("_")
    name_en = map(lambda word: word[0].upper() + word[1:], name_en)
    name_en = " ".join(name_en)
    videourl = pq(rootEl(".modeldlicon a")[0]).attr("href")
    videourl2 = rootEl(".modeldlicon2 a")
    if len(videourl2) > 0:
      videourl2 = pq(videourl2[0]).attr("href")
    else:
      videourl2 = None
    saveto = response.meta['saveto']
    if not os.path.exists(saveto):
      os.makedirs(saveto)
    def download_img(url, filename = None):
      if filename is None:
        m = re.match(r"^.*\/([^\/]+)$", url)
        filename = m.group(1)
      savepath = os.path.join(saveto, filename)
      if not os.path.exists(savepath):
        return scrapy.Request( url, meta = {
            'cookiejar': response.meta['cookiejar'],
            'savepath': savepath
          }, callback = self.parse_download )
      else:
        return None
    portraiturl = response.meta['portraiturl']
    if download_thumb and not os.path.exists(os.path.join(saveto, thumb_filename)):
      yield download_img(portraiturl, thumb_filename)
    topphotourl = videoEl.attr('poster')
    if download_topview and not os.path.exists(os.path.join(saveto, topview_filename)):
      yield download_img(topphotourl, topview_filename)
    imgEls = rootEl(".modelphoto .fancybox img")
    if download_gallery:
      for photoEl in imgEls:
        photourl = pq(photoEl).attr('src')
        yield download_img(photourl)
    desired_images = len(imgEls)
    infoconf = UserConfig()
    infoconf.set("pageurl", response.url)
    infoconf.set("number", number)
    infoconf.set("href", response.meta['href'])
    infoconf.set("name", name)
    infoconf.set("name_en", name_en)
    infoconf.set("saikai", saikai)
    infoconf.set("intro", intro)
    infoconf.set("video", videourl)
    infoconf.set("video2", videourl2)
    infoconf.set("egvideo", egvideourl)
    infoconf.set("desired_images", desired_images)
    infoconf.save(os.path.join(saveto, info_filename))

  def parse_download(self, response):
    file = open(response.meta['savepath'], "wb")
    file.write(response.body)
    file.close()











