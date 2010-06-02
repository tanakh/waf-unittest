Yet Another Waf Unittest
========================

Usage
-----

1. Copy unittestt.py to your project directory.

   ::

       $ wget http://github.com/tanakh/waf-unittest/raw/master/unittestt.py

2. Add tool_options() and check_tool()

   ::
    
        def set_options(opt):
            opt.tool_options('compiler_cxx')
            opt.tool_options('unittestt')
    
   ::
    
        def configure(conf):
            conf.check_tool('compiler_cxx')
            conf.check_tool('unittestt')

3. Add 'testt' or 'gtest' to your test program's feature.

   ::
    
        def build(bld):
            bld(features = 'cxx cprogram testt',
                source = 'test.cpp',
                includes = '.',
                target = 'test',
                uselib_local = 'lib',
		uselib = 'gtest')

   ::
    
        # autolink gtest_main
        def build(bld):
            bld(features = 'cxx cprogram gtest',
                source = 'test.cpp',
                includes = '.',
                target = 'test',
                uselib_local = 'lib')

4. Build without unittests

   ::
    
       $ waf build

5. Build with unittests and run it (updated only)

   ::

       $ waf build --check

6. Build with unittests and run all tests

   ::

       $ waf build --checkall

7. Build with a specified unittest and run it (always)

   ::

       $ waf build --checkone=test

8. Build with specified unittests by filter pattern (gtest style) and run it (always)

   ::

       $ waf build --checkfilter=test_target_name.tests.test
       $ waf build --checkfilter=test_target_name.tests.*
       $ waf build --checkfilter=*.tests.test

9. Enjoy!
