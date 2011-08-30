#!/usr/bin/env python
# encoding: ISO8859-1

import os, subprocess, sys
from waflib.TaskGen import before, after, feature
from waflib import Options, Task, Utils, Logs, Errors

C1 = b'#XXX'
C2 = b'#YYY'
UNPACK_DIR = '.unittest-gtest'
GTEST_DIR = 'gtest-1.6.0/fused-src'


def cleanup():
  import shutil
  try: shutil.rmtree(UNPACK_DIR)
  except OSError: pass

def unpack_gtest():
  cwd = os.getcwd()

  fname = __file__
  if fname.endswith('.pyc'):
    fname = fname[0:-1]
  f = open(fname, 'rb')

  while 1:
    line = f.readline()
    if not line:
      Logs.error('not contain gtest archive')
      sys.exit(1)
    if line == b'#==>\n':
      txt = f.readline()
      if not txt:
        Logs.error('corrupt archive')
      if f.readline() != b'#<==\n':
        Logs.error('corrupt archive')
      break

  txt = txt[1:-1].replace(C1, b'\n').replace(C2, b'\r')

  cleanup()

  tmp = 't.tar.bz2'

  os.makedirs(UNPACK_DIR)
  os.chdir(UNPACK_DIR)
  t = open(tmp, 'wb')
  t.write(txt)
  t.close()

  try:
    subprocess.check_call(['tar',  'xf', tmp])
  except:
    os.chdir(cwd)
    cleanup()
    Logs.error('gtest cannot be unpacked.')

  os.unlink(tmp)
  os.chdir(cwd)

def configure(conf):
    try:
      unpack_gtest()
      conf.msg('Unpacking gtest', 'yes')
    except:
      conf.msg('Unpacking gtest', 'no')
      Logs.error(sys.exc_info()[1])

    conf.check_cxx(lib = 'pthread', uselib_store = 'GTEST_PTHREAD')

def options(opt):
    opt.add_option('--check', action = 'store_true', default = False,
                   help = 'Execute unit tests')
    opt.add_option('--checkall', action = 'store_true', default = False,
                   help = 'Execute all unit tests')
    opt.add_option('--checkone', action = 'store', default = False,
                   help = 'Execute specified unit test')
    opt.add_option('--checkfilter', action = 'store', default = False,
                   help = 'Execute unit tests sprcified by pattern')

def match_filter(filt, targ):
    if isinstance(filt, str):
        (pat, _, _) = filt.partition('.')
        if pat == '*':
            return True
        return pat == targ
    return False

@feature('testt', 'gtest')
@before('process_rule')
def test_remover(self):
    if not Options.options.check and not Options.options.checkall and self.target != Options.options.checkone and not match_filter(Options.options.checkfilter, self.target):
        self.meths[:] = []

@feature('gtest')
@before('process_source')
def gtest_attach(self):
    DIR = UNPACK_DIR + '/' + GTEST_DIR
    self.source = self.to_list(getattr(self, 'source', [])) + [
      DIR + '/gtest/gtest-all.cc',
      DIR + '/gtest/gtest_main.cc']
    self.includes = self.to_list(getattr(self, 'includes', [])) + [DIR]
    self.use = self.to_list(getattr(self, 'use', [])) + ['GTEST_PTHREAD']

@feature('testt', 'gtest')
@after('apply_link')
def make_test(self):
    if not 'cprogram' in self.features and not 'cxxprogram' in self.features:
        Logs.error('test cannot be executed %s'%self)
        return
    self.default_install_path = None
    self.create_task('utest', self.link_task.outputs)

import threading
testlock = threading.Lock()

class utest(Task.Task):
    """
    Execute a unit test
    """
    color = 'PINK'
    ext_in = ['.bin']
    vars = []
    def runnable_status(self):
        stat = super(utest, self).runnable_status()
        if stat != Task.SKIP_ME:
            return stat

        if Options.options.checkall:
            return Task.RUN_ME
        if Options.options.checkone == self.generator.name:
            return Task.RUN_ME
        if isinstance(Options.options.checkfilter, str):
            if match_filter(Options.options.checkfilter, self.generator.name):
                return Task.RUN_ME

        return stat

    def run(self):
        """
        Execute the test. The execution is always successful, but the results
        are stored on ``self.generator.bld.utest_results`` for postprocessing.
        """
        
        status = 0
        
        filename = self.inputs[0].abspath()
        self.ut_exec = getattr(self, 'ut_exec', [filename])
        if getattr(self.generator, 'ut_fun', None):
            self.generator.ut_fun(self)

        try:
            fu = getattr(self.generator.bld, 'all_test_paths')
        except AttributeError:
            fu = os.environ.copy()
            self.generator.bld.all_test_paths = fu

            lst = []
            for g in self.generator.bld.groups:
                for tg in g:
                    if getattr(tg, 'link_task', None):
                        lst.append(tg.link_task.outputs[0].parent.abspath())
                        
            def add_path(dct, path, var):
                dct[var] = os.pathsep.join(Utils.to_list(path) + [os.environ.get(var, '')])

            if sys.platform == 'win32':
                add_path(fu, lst, 'PATH')
            elif sys.platform == 'darwin':
                add_path(fu, lst, 'DYLD_LIBRARY_PATH')
                add_path(fu, lst, 'LD_LIBRARY_PATH')
            else:
                add_path(fu, lst, 'LD_LIBRARY_PATH')


        if isinstance(Options.options.checkfilter, str):
            (_, _, filt) = Options.options.checkfilter.partition('.')
            if filt != "":
                self.ut_exec += ['--gtest_filter=' + filt]

        cwd = getattr(self.generator, 'ut_cwd', '') or self.inputs[0].parent.abspath()
        proc = Utils.subprocess.Popen(self.ut_exec, cwd=cwd, env=fu, stderr=Utils.subprocess.PIPE, stdout=Utils.subprocess.PIPE)
        (stdout, stderr) = proc.communicate()

        tup = (filename, proc.returncode, stdout, stderr)
        self.generator.utest_result = tup
        
        testlock.acquire()
        try:
            bld = self.generator.bld
            Logs.debug("ut: %r", tup)
            try:
                bld.utest_results.append(tup)
            except AttributeError:
                bld.utest_results = [tup]

            a = getattr(self.generator.bld, 'added_post_fun', False)
            if not a:
                self.generator.bld.add_post_fun(summary)
                self.generator.bld.added_post_fun = True

        finally:
            testlock.release()

def summary(bld):
    lst = getattr(bld, 'utest_results', [])

    if not lst: return

    total = len(lst)
    fail = len([x for x in lst if x[1]])

    Logs.pprint('CYAN', 'test summary')
    Logs.pprint('CYAN', '  tests that pass %d/%d' % (total-fail, total))

    for (f, code, out, err) in lst:
        if not code:
            Logs.pprint('GREEN', '    %s' % f)
            if isinstance(Options.options.checkfilter, str):
                print(out)

    if fail>0:
        Logs.pprint('RED', '  tests that fail %d/%d' % (fail, total))
        for (f, code, out, err) in lst:
            if code:
                Logs.pprint('RED', '    %s' % f)
                print(out.decode())
        raise Errors.WafError('test failed')

