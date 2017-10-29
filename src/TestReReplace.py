#!/usr/bin/python
# an temporal file to do some re replace job with Module.py


import re

f = open('/Users/bitbook/Documents/PostGradCourses/MainProj/Spac/src/randomText.txt', 'r')
for line in f:
    re.sub(r'module\.[a-z]\.', 'sssss', line)
f.close()