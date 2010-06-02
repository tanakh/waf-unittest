#! /usr/bin/env python
# encoding: utf-8

import os, sys
import Options, Task, Utils, Logs
from TaskGen import before, after, feature
from Constants import *

def detect(conf):
    if conf.check_cfg(path = 'gtest-config',
                      args = '--cppflags --cxxflags --ldflags --libs',
                      package = '',
                      uselib_store = 'GTEST'):
        def f(str):
            if str == 'gtest':
                return 'gtest_main'
            else:
                return str
        conf.env.LIB_GTEST = map(f, conf.env.LIB_GTEST)

def set_options(opt):
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

def test_remover(self):
    if not Options.options.check and not Options.options.checkall and self.target != Options.options.checkone and not match_filter(Options.options.checkfilter, self.target):
        self.meths[:] = []

feature('testt', 'gtest')(test_remover)
before('apply_core')(test_remover)

def make_test(self):
    if not 'cprogram' in self.features:
        Logs.error('test cannot be executed %s'%self)
        return
    self.default_install_path = None
    self.create_task('utest', self.link_task.outputs)

feature('testt', 'gtest')(make_test)
after('apply_link', 'vars_target_cprogram')(make_test)

def gtest_attach(self):
    if not self.env.HAVE_GTEST:
        Logs.error('gtest is not found')
        self.meths[:] = []
        return

    if isinstance(self.uselib, str):
        self.uselib += " GTEST"
    else:
        self.uselib.append('GTEST')

feature('gtest')(gtest_attach)
before('apply_core')(gtest_attach)

import threading
testlock = threading.Lock()

def exec_test(self):
    variant = self.env.variant()
    filename = self.inputs[0].abspath(self.env)

    try:
        fu = getattr(self.generator.bld, 'all_test_paths')
    except AttributeError:
        fu = os.environ.copy()
        self.generator.bld.all_test_paths = fu

        lst = []
        for obj in self.generator.bld.all_task_gen:
            link_task=getattr(obj, 'link_task', None)
            if link_task and link_task.env.variant()==variant:
                lst.append(link_task.outputs[0].parent.abspath(obj.env))

        def add_path(dct, path, var):
            dct[var] = os.pathsep.join(Utils.to_list(path)+[os.environ.get(var, '')])
        if sys.platform=='win32':
            add_path(fu, lst, 'PATH')
        elif sys.platform=='darwin':
            add_path(fu, lst, 'DYLD_LIBRARY_PATH')
            add_path(fu, lst, 'LD_LIBRARY_PATH')
        else:
            add_path(fu, lst, 'LD_LIBRARY_PATH')

    cmdline = [filename]
    cwd = self.inputs[0].parent.abspath(self.env)

    if isinstance(Options.options.checkfilter, str):
        (_, _, filt) = Options.options.checkfilter.partition('.')
        if filt != "":
            cmdline += ['--gtest_filter=' + filt]

    proc = Utils.pproc.Popen(cmdline, cwd = cwd, env = fu,
                             stderr = Utils.pproc.PIPE,
                             stdout = Utils.pproc.PIPE)
    (stdout, stderr) = proc.communicate()
    tup = (filename, proc.returncode, stdout, stderr)

    testlock.acquire()
    try:
        Logs.debug("ut: %r",tup)
        try:
            self.generator.bld.utest_results.append(tup)
        except:
            self.generator.bld.utest_results = [tup]

        a = getattr(self.generator.bld, 'added_post_fun', False)
        if not a:
            self.generator.bld.add_post_fun(summary)
            self.generator.bld.added_post_fun = True

    finally:
        testlock.release()

cls = Task.task_type_from_func('utest', func = exec_test, color = 'PINK', ext_in = '.bin')
old = cls.runnable_status

def test_status(self):
    if Options.options.checkall:
        return RUN_ME
    if Options.options.checkone == self.generator.name:
        return RUN_ME
    if isinstance(Options.options.checkfilter, str):
        if match_filter(Options.options.checkfilter, self.generator.name):
            return RUN_ME
    return old(self)

cls.runnable_status = test_status
cls.quiet = 1

def summary(bld):
    lst = getattr(bld, 'utest_results', [])

    if not lst: return

    total = len(lst)
    fail = len([x for x in lst if x[1]])

    Utils.pprint('CYAN', 'test summary')
    Utils.pprint('CYAN', '  tests that pass %d/%d' % (total-fail, total))

    for (f, code, out, err) in lst:
        if not code:
            Utils.pprint('GREEN', '    %s' % f)
            if isinstance(Options.options.checkfilter, str):
                print(out)

    if fail>0:
        Utils.pprint('RED', '  tests that fail %d/%d' % (fail, total))
        for (f, code, out, err) in lst:
            if code:
                Utils.pprint('RED', '    %s' % f)
                print(out)
