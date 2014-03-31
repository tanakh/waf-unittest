#!/usr/bin/env python
# encoding: utf-8

import os, subprocess, sys

TMPL_NAME = 'unittestt.py'
DEST_NAME = 'unittest_gtest.py'
TARBALL_NAME = 'fused-gtest.tar.bz2'
GTEST_DIR = 'gtest-1.7.0/fused-src/gtest'

C1 = '#XXX'.encode()
C2 = '#YYY'.encode()

try:
  if subprocess.call(['tar', 'cjf', TARBALL_NAME, GTEST_DIR]):
    raise

  t = open(TMPL_NAME, 'rb')
  scr = t.read()
  t.close()

  t = open(TARBALL_NAME, 'rb')
  tbz = t.read()
  t.close()

  scr += '#==>\n#'.encode()
  scr += tbz.replace('\n'.encode(), C1).replace('\r'.encode(), C2)
  scr += '\n#<==\n'.encode()

  t = open(DEST_NAME, 'wb')
  t.write(scr)
  t.close()

  os.unlink(TARBALL_NAME)

except:
  print(sys.exc_info()[1])
