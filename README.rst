Yet Another Waf Unittest
========================

Usage
-----

1. Copy unittestt.py to your project directory.

2. Add tool_options() and check_tool()

   ::
    
        def set_options(opt):
            opt.tool_options('compiler_cxx')
            opt.tool_options('unittestt')
    
   ::
    
        def configure(conf):
            conf.check_tool('compiler_cxx')
            conf.check_tool('unittestt')

3. Add your test program's feature to 'testt' or 'gtest'

   ::
    
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

7. Enjoy!
