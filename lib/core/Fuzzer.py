# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Author: Mauro Soria

import threading

from lib.connection.RequestException import RequestException
from .Path import *
from .Scanner import *
from concurrent.futures import ThreadPoolExecutor


class Fuzzer(object):
    def __init__(
        self,
        requester,
        dictionary,
        config,
        testFailPath=None,
        threads=1,
        matchCallbacks=[],
        notFoundCallbacks=[],
        errorCallbacks=[],
    ):
        self.config = config 
        self.requester = requester
        self.dictionary = dictionary
        self.testFailPath = testFailPath
        self.basePath = self.requester.basePath
        self.threads = []
        self.threadsCount = (
            threads if len(self.dictionary) >= threads else len(self.dictionary)
        )
        self.running = False
        self.scanners = {}
        self.defaultScanner = None
        self.matchCallbacks = matchCallbacks
        self.notFoundCallbacks = notFoundCallbacks
        self.errorCallbacks = errorCallbacks
        self.matches = []
        self.errors = []

    def wait(self, timeout=None):
        for thread in self.threads:
            thread.join(timeout)

            if timeout and thread.is_alive():
                return False

        return True

    def setupScanners(self):
        if len(self.scanners):
            self.scanners = {}
        
        Pool = ThreadPoolExecutor(10)
        self.defaultScanner = Pool.submit(Scanner,self.requester, self.testFailPath).result()
        self.scanners["/"] = Pool.submit(Scanner,self.requester, self.testFailPath, suffix="/").result()
        self.scanners["dotfiles"] = Pool.submit(Scanner,self.requester, self.testFailPath, preffix=".").result()
        #self.defaultScanner = Scanner(self.requester, self.testFailPath)
        #self.scanners["/"] = Scanner(self.requester, self.testFailPath, suffix="/")
        #self.scanners["dotfiles"] = Scanner(self.requester, self.testFailPath, preffix=".")
        Pool.shutdown(wait=True)
        for extension in self.config.extensions:
            self.scanners[extension] = Scanner(
                self.requester, self.testFailPath, "." + extension
            )
        
        #return [self.defaultScanner,self.scanners]

    def setupThreads(self):
        if len(self.threads):
            self.threads = []

        for thread in range(self.threadsCount):
            newThread = threading.Thread(target=self.thread_proc)
            newThread.daemon = True
            self.threads.append(newThread)

    def getScannerFor(self, path):
        if path.endswith("/"):
            return self.scanners["/"]
        
        if path.startswith('.'):
            return self.scanners['dotfiles']

        for extension in list(self.scanners.keys()):
            if path.endswith(extension):
                return self.scanners[extension]

        # By default, returns empty tester
        return self.defaultScanner

    def start(self,path):
        status, response,host = self.scan(path)
        result = Path(path=path, status=status, response=response,host=host)
        try:
            if status:
                    self.matches.append(result)
                    for callback in self.matchCallbacks:
                            callback(result)
            else:
                pass
        except RequestException as e:
            print(e)

    def play(self):
        self.playEvent.set()

    def pause(self):
        self.playEvent.clear()
        for thread in self.threads:
            if thread.is_alive():
                self.pausedSemaphore.acquire()

    def stop(self):
        self.running = False
        self.play()

    def scan(self, path):
        response = self.requester.request(path)
        result = None
        if self.getScannerFor(path).scan(path, response):
            result = None if response.status == 404 else response.status
        return result, response,self.requester.host

    def isRunning(self):
        return self.running

    def finishThreads(self):
        self.running = False
        self.finishedEvent.set()

    def isFinished(self):
        return self.runningThreadsCount == 0

    def stopThread(self):
        self.runningThreadsCount -= 1


    def thread_proc(self):
        self.playEvent.wait()
        
        try:
            path = next(self.dictionary)
            
            while path:
                try:
                    status, response = self.scan(path)
                    result = Path(path=path, status=status, response=response)

                    if status:
                        self.matches.append(result)
                        for callback in self.matchCallbacks:
                            callback(result)
                    else:
                        for callback in self.notFoundCallbacks:
                            callback(result)

                except RequestException as e:

                    for callback in self.errorCallbacks:
                        callback(path, e.args[0]["message"])

                    continue

                finally:
                    if not self.playEvent.isSet():
                        self.pausedSemaphore.release()
                        self.playEvent.wait()

                    path = next(self.dictionary)  # Raises StopIteration when finishes

                    if not self.running:
                        break

        except StopIteration:
            return

        finally:
            self.stopThread()
