# Yet Another Waf Unittest

## Usage

* Copy unittestt.py to your project directory.

* Add tool_options() and check_tool()

    def set_options(opt):
        opt.tool_options('compiler_cxx')
        opt.tool_options('unittestt')

    def configure(conf):
        conf.check_tool('compiler_cxx')
        conf.check_tool('unittestt')

* Add your test program's feature to 'testt' or 'gtest'

    def build(bld):
        bld(features = 'cxx cprogram gtest',
            source = 'test.cpp',
            includes = '.',
            target = 'test',
            uselib_local = 'lib')

* Build without unittests

    $ waf build

* Build with unittests and run it (updated only)

    $ waf build --check

* Build with unittests and run all tests

    $ waf build --checkall

* Enjoy!
