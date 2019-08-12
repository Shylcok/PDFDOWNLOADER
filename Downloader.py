#!/usr/bin/env python
# encoding: utf-8
"""
@version: python3.6
@author: JYFelt
@license: Apache Licence 
@contact: JYFelt@163.com
@site: https://www.jyfelt.cn
@software: PyCharm
@file: Downloader.py
@time: 2019/8/12上午8:49
"""
import requests
from bs4 import BeautifulSoup
import re
import winreg as _winreg
import os
import time
import datetime

NOW_TIME = datetime.datetime.now().strftime('%Y%m%d')


class WEBDownloader:
    def __init__(self, url, dir, file_type="all"):
        self._url = url
        self._type = file_type
        self.__i = 1
        self._dir = dir
        self._topRootDomain = (
            '.com', '.la', '.io', '.co', '.info', '.net', '.org', '.me', '.mobi',
            '.us', '.biz', '.xxx', '.ca', '.co.jp', '.com.cn', '.net.cn',
            '.org.cn', '.mx', '.tv', '.ws', '.ag', '.com.ag', '.net.ag',
            '.org.ag', '.am', '.asia', '.at', '.be', '.com.br', '.net.br',
            '.bz', '.com.bz', '.net.bz', '.cc', '.com.co', '.net.co',
            '.nom.co', '.de', '.es', '.com.es', '.nom.es', '.org.es',
            '.eu', '.fm', '.fr', '.gs', '.in', '.co.in', '.firm.in', '.gen.in',
            '.ind.in', '.net.in', '.org.in', '.it', '.jobs', '.jp', '.ms',
            '.com.mx', '.nl', '.nu', '.co.nz', '.net.nz', '.org.nz',
            '.se', '.tc', '.tk', '.tw', '.com.tw', '.idv.tw', '.org.tw',
            '.hk', '.co.uk', '.me.uk', '.org.uk', '.vg', ".com.hk")

    @staticmethod
    def get_desktop():
        key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                              r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        return _winreg.QueryValueEx(key, "Desktop")[0]

    def get_url_root(self):
        url = self._url
        url_root = ""
        try:
            for x in self._topRootDomain:
                if x in url:
                    url_root = url.split(x)[0] + x
        except Exception as ex:
            print("get_domain_root() -- error_msg: " + str(ex))
        return url_root + "/sp19/"

    def _get_content(self):
        try:
            response = requests.get(self._url)
        except requests.exceptions.BaseHTTPError as e:
            response = '-'
            print(e)
        if response.status_code != 200:
            print("[%d]请检查url输入是否正确！！！" % response.status_code)
            return -1
        return response.text

    def _soup_list(self):
        if self._get_content() == -1:
            return -1
        try:
            soup = BeautifulSoup(self._get_content(), 'html.parser')
            lists = soup.find_all(href=re.compile("assets/"))
            files = {}
            for li in lists:
                href = li.get('href')
                if href[-4:] == ".pdf":
                    files[li.string + '.pdf'] = href
                if href[-4:] == ".ppt":
                    files[li.string + '.ppt'] = href
                if href[-5:] == ".pptx":
                    files[li.string + '.pptx'] = href
                if href[-4:] == ".mp4":
                    files[li.string + '.mp4'] = href
        except Exception as e:
            files = {}
            print(e)
        return files

    def _download_file(self, name, file, length):
        path_ = WEBDownloader.get_desktop() + '\\DOWNLOADEDFiles' + NOW_TIME + "\\" + self._dir
        path = path_ + "\\" + name
        if not os.path.exists(path_):
            os.makedirs(path_)
        urls = self.get_url_root() + file
        size = 0
        try:
            r = requests.get(urls)
        except requests.exceptions.HTTPError as e:
            r = '-'
            print(e)

        chunk_size = 1024
        content_size = int(r.headers['content-length'])
        if r.status_code == 200:
            print('[文件大小]:%0.2f MB' % (content_size / chunk_size / 1024))
            with open(path, "wb") as f:
                for data in r.iter_content(chunk_size=chunk_size):
                    f.write(data)
                    size += len(data)
                    print('\r' + '[下载进度]:%s%.2f%%' % (
                        '>' * int(size * 50 / content_size), float(size / content_size * 100)))
            print("[√]%s下载完成，第%d个文件，共%d个" % (name, self.__i, length))
            self.__i += 1
        else:
            print("[×]下载失败，资源不存在，详情请访问下方链接", r.status_code)
        return urls

    def run(self):
        files = self._soup_list()
        if files == -1:
            print("下载退出！")
        else:
            length = len(files)
            start_time = time.time()
            print("开始下载!")
            for name, file in files.items():
                print(self._download_file(name, file, length))
            end_time = time.time()
            print('\n' + "全部下载完成!　用时%.2f秒, 已下载%d个，失败%d个。" % (end_time - start_time, self.__i, length - self.__i))


if __name__ == '__main__':
    DIR = input("输入文件夹名：（文件默认保存在\"桌面\\DOWNLOADEDFiles\\您输入的文件夹名\"文件夹中)\n")
    URL = input("请输入要下载的网址：（ds100.org/sp19请输入:1）\n")
    if URL == '1':
        URL = "http://www.ds100.org/sp19/syllabus#lecture-week-17"
    webDownloader = WEBDownloader(url=URL, dir=DIR)
    webDownloader.run()
