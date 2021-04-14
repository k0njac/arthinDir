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
dicpath = "db/dic.txt" #字典位置
useRandomAgents = False 
cookie = ""
data = ""
maxRetries = 2
delay = 0
timeout = 10
ip =None 
proxy = None
proxylist = None
redirect = False 
requestByHostname=False
data = None
useragent = None
threadsCount = 1

extensions = ['php','jsp','jsp','jspx','html','htm','js','asp','aspx']
excludeStatusCodes = [500,502]
includeStatusCodes = [200,301]
excludeTexts = []
excludeRegexps = []
testFailPath = None #自定义随机目录匹配404

