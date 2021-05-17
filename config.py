'''
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
'''


httpmethod = "GET" # GET post
dicpath = ["db/dic.txt"] #字典位置
resultFile = "report/result.txt" #结果位置
pool =500 #线程池的数量
useRandomAgents = False 
cookie = ""
data = ""
maxRetries = 2
delay = 0
timeout = 3
ip =None 
proxy = None
proxylist = None
redirect = False 
requestByHostname=False
data = None
useragent = None
threadsCount = 1
'''
Dictionary(self.config.dicpath, self.config.extensions, self.config.suffixes, 
                                     self.config.prefixes, self.config.lowercase, self.config.uppercase, 
                                     self.config.forceExtensions, self.config.noDotExtensions, 
                                     self.config.excludeExtensions)
['db/dicc.txt'] ['*'] [] [] False False False False []
'''
extensions = []
excludeStatusCodes = [500,502]
includeStatusCodes = [200,301]
excludeTexts = []
excludeRegexps = []
testFailPath = None #自定义随机目录匹配404
suffixes = []
prefixes = []
lowercase = False
uppercase = False
forceExtensions = False
noDotExtensions = False
excludeExtensions = []