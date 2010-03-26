
APPNAME = 'waf_unittest'
VERSION = '0.0.0'

srcdir = '.'
blddir = 'build'

def set_options(opt):
    opt.tool_options('compiler_cxx')
    opt.tool_options('unittestt')

def configure(conf):
    conf.check_tool('compiler_cxx')
    conf.check_tool('unittestt')

def build(bld):
    bld(features = 'cxx cshlib',
        source = 'lib.cpp',
        includes = '.',
        target = 'lib')

    bld(features = 'cxx cprogram gtest',
        source = 'test.cpp',
        includes = '.',
        target = 'test',
        uselib_local = 'lib')

    bld(features = 'cxx cprogram gtest',
        source = 'test2.cpp',
        includes = '.',
        target = 'test2',
        uselib_local = 'lib')

def shutdown(ctx):
    pass

