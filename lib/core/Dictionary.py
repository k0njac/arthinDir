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

import re
import threading

import urllib.parse

from lib.utils.FileUtils import File


class Dictionary(object):


    def __init__(self, paths, extensions, suffixes=None, prefixes=None, lowercase=False, uppercase=False, forcedExtensions=False, noDotExtensions=False, excludeExtensions=[]):
        self.entries = []
        self.currentIndex = 0
        self.condition = threading.Lock()
        self._extensions = extensions
        self._prefixes = prefixes
        self._suffixes = suffixes
        self._paths = paths
        self._forcedExtensions = forcedExtensions
        self._noDotExtensions = noDotExtensions
        self._excludeExtensions = excludeExtensions
        self.lowercase = lowercase
        self.uppercase = uppercase
        self.dictionaryFiles = [File(path) for path in self.paths]


    @property
    def extensions(self):
        return self._extensions

    @extensions.setter
    def extensions(self, value):
        self._extensions = value

    @property
    def paths(self):
        return self._paths

    @paths.setter
    def paths(self, paths):
        self._paths = paths

    @classmethod
    def quote(cls, string):
        return urllib.parse.quote(string, safe=":/~?%&+-=$!@^*()[]{}<>;'\"|\\,._")

    def generate(self):
        reext = re.compile('\%ext\%', re.IGNORECASE).sub
        reextdot = re.compile('\.\%ext\%', re.IGNORECASE).sub
        exclude = re.findall
        result = []
        for dictFile in self.dictionaryFiles:
            for line in list(dict.fromkeys(dictFile.getLines())):
                if line.startswith("/"):
                    line = line[1:]
                if "%noforce%" in line.lower():
                    noforce = True
                else:
                    noforce = False
                if line.lstrip().startswith("#"):
                    continue
                if len(self._excludeExtensions):
                    matched = False
                    for excludeExtension in self._excludeExtensions:
                        if len(exclude("." + excludeExtension, line)):
                            matched = True
                            break
                    if matched:
                        continue
                if "%ext%" in line.lower():
                    for extension in self._extensions:
                        if self._noDotExtensions:
                            newline = reextdot(extension, line)

                        else:
                            newline = line
                            
                        newline = reext(extension, newline)

                        quote = self.quote(newline)
                        result.append(quote)

                # If forced extensions is used and the path is not a directory ... (terminated by /)
                # process line like a forced extension.
                elif self._forcedExtensions and not line.rstrip().endswith("/") and not noforce:
                    quoted = self.quote(line)

                    for extension in self._extensions:
                        # Why? Check https://github.com/maurosoria/dirsearch/issues/70
                        if extension.strip() == '':
                            result.append(quoted)
                        else:
                            result.append(quoted + ('' if self._noDotExtensions else '.') + extension)

                    if quoted.strip() != '':
                        result.append(quoted)
                        result.append(quoted + "/")

                # Append line unmodified.
                else:
                    result.append(self.quote(line))
        if self._prefixes:
            for res in list(dict.fromkeys(result)):
                for pref in self._prefixes:
                    if not res.startswith(pref): 
                        result.append(pref + res)
        if self._suffixes:
            for res in list(dict.fromkeys(result)):
                if not res.rstrip().endswith("/"):
                    for suff in self._suffixes:
                        result.append(res + suff)


        if self.lowercase:
            self.entries = list(dict.fromkeys(map(lambda l: l.lower(), result)))
            
        elif self.uppercase:
            self.entries = list(dict.fromkeys(map(lambda l: l.upper(), result)))

        else:
            self.entries = list(dict.fromkeys(result))
        return self.entries