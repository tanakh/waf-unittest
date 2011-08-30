#!/usr/bin/env python
# encoding: utf-8

import os, subprocess, sys

TMPL_NAME = 'unittestt.py'
DEST_NAME = 'unittest_gtest.py'
TARBALL_NAME = 'fused-gtest.tar.bz2'
GTEST_DIR = 'gtest-1.6.0/fused-src/gtest'

C1 = b'#XXX'
C2 = b'#YYY'

try:
  subprocess.check_call(['tar', 'cjf', TARBALL_NAME, GTEST_DIR])

  t = open(TMPL_NAME, 'rb')
  scr = t.read()
  t.close()

  t = open(TARBALL_NAME, 'rb')
  tbz = t.read()
  t.close()

  scr += b'#==>\n#'
  scr += tbz.replace(b'\n', C1).replace(b'\r', C2)
  scr += b'\n#<==\n'

  t = open(DEST_NAME, 'wb')
  t.write(scr)
  t.close()

  os.unlink(TARBALL_NAME)

except:
  print(sys.exc_info()[1])
