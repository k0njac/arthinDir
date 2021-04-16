# -*- coding: utf-8 -*-
import gc
import os
import sys
import time
import re
import urllib.parse
from loguru import logger
from lib.utils import FileUtils
from lib.core import Dictionary,Fuzzer
from lib.connection import Requester, RequestException
class SkipTargetInterrupt(Exception):
    pass
class Controller(object):
    def __init__(self, script_path,config):
            logger.add('runtime.log')
            default_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
                "Accept-Language": "*",
                "Accept-Encoding": "*",
                "Keep-Alive": "300",
                "Cache-Control": "max-age=0",
            }
            self.script_path = script_path
            self.save_path = script_path
            self.config  = config
            if self.config.httpmethod.lower() not in ["get", "head", "post", "put", "patch", "options", "delete", "trace", "debug"]:
                logger.debug("Invalid http method!")
                exit(1)
            self.includeStatusCodes = self.config.includeStatusCodes
            self.excludeStatusCodes = self.config.excludeStatusCodes
            self.excludeTexts = self.config.excludeTexts
            self.excludeRegexps = self.config.excludeRegexps
            
            self.httpmethod = self.config.httpmethod.lower()
            #self.dicpath = (FileUtils.buildPath(self.script_path,self.config.dicpath))
            self.Readdictionary = Dictionary(self.config.dicpath, self.config.extensions, self.config.suffixes, 
                                     self.config.prefixes, self.config.lowercase, self.config.uppercase, 
                                     self.config.forceExtensions, self.config.noDotExtensions, 
                                     self.config.excludeExtensions)
            self.dictionary =self.Readdictionary.generate()
            #print(self.dictionary)
            self.urlList =  FileUtils.getLines(
                    FileUtils.buildPath(self.script_path, "target.txt")
                )

            self.scanresult = []

            self.reqList = {}#存储self.requester
            self.scannerList = {}#存储self.scanners
            self.fuzzList = {}
            scanFlag = True
            badUrl = []
            if self.config.useRandomAgents:
                self.randomAgents = FileUtils.getLines(
                    FileUtils.buildPath(self.script_path, "db", "user-agents.txt")
                )
            logger.debug("[+]check urlList.超时的会移出扫描列表")
            for currentdic in self.dictionary:
               # print(currentdic)
                for url in self.urlList:
                    try:
                        if scanFlag:
                            self.requester = Requester(
                                    url,
                                    cookie=self.config.cookie,
                                    useragent=self.config.useragent,
                                    maxPool=self.config.threadsCount,
                                    maxRetries=self.config.maxRetries,
                                    delay=self.config.delay,
                                    timeout=self.config.timeout,
                                    ip=self.config.ip,
                                    proxy=self.config.proxy,
                                    proxylist=self.config.proxylist,
                                    redirect=self.config.redirect,
                                    requestByHostname=self.config.requestByHostname,
                                    httpmethod=self.config.httpmethod,
                                    data=self.config.data,
                                )
                            self.requester.request("/")
                            self.reqList[url] = self.requester
                            matchCallbacks = [self.matchCallback]
                            notFoundCallbacks = [self.notFoundCallback]
                            errorCallbacks = [self.errorCallback, self.appendErrorLog]
                            self.fuzzer = Fuzzer(
                                self.requester,
                                self.dictionary,
                                self.config,
                                testFailPath=self.config.testFailPath,
                                threads=self.config.threadsCount,
                                matchCallbacks=matchCallbacks,
                                notFoundCallbacks=notFoundCallbacks,
                                errorCallbacks=errorCallbacks,
                            )

                            self.fuzzer.setupScanners()
                            self.fuzzList[url] = self.fuzzer
                            #self.scannerList[url]=self.fuzzer.setupScanners()
                        else:
                           # print(self.reqList)
                            self.requester =self.reqList[url]
                            self.fuzzer = self.fuzzList[url]
                            #self.scannerList[url]=self.fuzzer.setupScanners()
                        #logger.debug("[+]scan:%s %s"%(url,currentdic))
                        self.fuzzer.start(currentdic)
                    except:
                        logger.debug("[-]Error:%s timeout"%(url))
                        badUrl.append(url)
                for bad in badUrl:
                    self.urlList.remove(bad)
                badUrl=[]
                scanFlag = False
                if self.config.useRandomAgents:
                        self.requester.setRandomAgents(self.randomAgents)
    



    def matchCallback(self, path):
        if path.status:
            if path.status not in self.excludeStatusCodes and (path.status in self.includeStatusCodes):
                for excludeText in self.excludeTexts:
                    if excludeText in path.response.body.decode():
                        del path
                        return
                
                for excludeRegexp in self.excludeRegexps:
                    if (
                        re.search(excludeRegexp, path.response.body.decode())
                        is not None
                    ):
                        del path
                        return
                self.savaReport(path)
    def notFoundCallback(self):
        pass
    def errorCallback(self):
        pass 
    def appendErrorLog(self):
        pass 
    def savaReport(self,path):
        print('[+]Success:',path.response.url)