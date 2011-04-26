Yet Another Waf Unittest
========================

Usage
-----

1. Copy unittestt.py to your project directory.

   ::

       $ wget http://github.com/tanakh/waf-unittest/raw/master/unittestt.py

2. Add load('unittestt') to options() and configure().

   ::
    
        def options(opt):
            opt.load('compiler_cxx unittestt')
    
   ::
    
        def configure(conf):
            conf.load('compiler_cxx unittestt')

3. Add 'testt' or 'gtest' to your test program's feature.

   ::
    
        def build(bld):
            bld.program(features = 'testt',
                        source = 'test.cpp',
                        includes = '.',
                        target = 'test',
                        use = 'lib GTEST')

   ::
    
        # autolink gtest_main
        def build(bld):
            bld.program(features = 'gtest',
                        source = 'test.cpp',
                        includes = '.',
                        target = 'test',
                        use = 'lib')

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
