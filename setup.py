# -*- coding: utf-8 -*-
#
# This file is part of couchapp released under the Apache 2 license. 
# See the NOTICE for more information.

from distutils.command.install_data import install_data
from distutils.core import setup

import os
import sys
import fnmatch

if not hasattr(sys, 'version_info') or sys.version_info < (2, 5, 0, 'final'):
    raise SystemExit("Couchapp requires Python 2.5 or later.")


extra = {}
class install_package_data(install_data):
    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_lib', 'install_dir'))
        install_data.finalize_options(self)
 
cmdclass = {'install_data': install_package_data }



def get_data_files():
    data_files = []
    data_files.append((os.curdir, 
                       ["LICENSE", "MANIFEST.in", "NOTICE", "README.md", 
                        "THANKS.txt",]))
    for root in ('templates', 'vendor'):

        for dir, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if not x.startswith('.')]
            files = [x for x in files if not x.startswith('.')]

            dest = os.path.join("couchapp", dir),
            data_files.append((dest,
                              [os.path.join(dir, file_) for file_ in files]))


    return data_files

def get_packages_data():
    return {
            "couchapp": [
                "templates/*",
                "vendor/*"
            ] 
    }

def get_include_files():
    include_files = []
    
    data_path_src = os.curdir
    data_path_dst = os.curdir

    filelist = ["LICENSE", "MANIFEST.in", "NOTICE", "README.md", 
                        "THANKS.txt",]
    
    for fl in filelist:
        include_files.append((os.path.join(data_path_src, fl), 
                           os.path.join(data_path_dst, fl)))

    for root in ('templates', 'vendor'):
        for dir, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if not x.startswith('.')]
            files = [x for x in files if not x.startswith('.')]

            for f in files:
                src = os.path.join(dir, f) 
                include_files.append((src, src))

    return include_files


def get_couchapp_packages():
    return [
            "couchapp",
            "couchapp.ext",
            "couchapp.hooks",
            "couchapp.hooks.compress",
            "couchapp.vendors",
            "couchapp.vendors.backends"
            ]

def get_couchapp_all_packages():
    fls = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(os.curdir,
                                                             "couchapp")):
        for filename in fnmatch.filter(filenames, "*.py"):
            fileui = os.path.join(dirpath, filename)
            if not os.access(fileui, os.R_OK):
                raise IOError("Can not access the file {0}" \
                        .format(fileui))
            fileui = fileui.replace("%s%s" % (os.curdir, os.sep), "")
            fileui = fileui.replace("%s" % os.sep, ".")
            fileui = fileui.replace(".py", "")
            fileui = fileui.replace(".__init__", "")
            fls.append(fileui)
    return fls

def get_include_modules():
    inc = [
        "restkit", "restkit.http", "restkit.conn", "restkit.contrib",
        "restkit.pool", "restkit.util", "restkit.client"
    ]
    if sys.platform in ("win32",):
        pass     
    return inc

def get_package_modules():
    return [
        "restkit",
    ]

def get_scripts():
    if os.name == "posix":
        return [os.path.join("resources", "scripts", "couchapp")]
    return [os.path.join("resources", "scripts", "couchapp.bat")]


if os.name == "nt":
    # py2exe needs to be installed to work
    try:
        import py2exe

        # Help py2exe to find win32com.shell
        try:
            import modulefinder
            import win32com
            for p in win32com.__path__[1:]: # Take the path to win32comext
                modulefinder.AddPackagePath("win32com", p)
            pn = "win32com.shell"
            __import__(pn)
            m = sys.modules[pn]
            for p in m.__path__[1:]:
                modulefinder.AddPackagePath(pn, p)
        except ImportError:
            raise SystemExit('You need pywin32 installed ' +
                    'http://sourceforge.net/projects/pywin32')
    
         # If run without args, build executables, in quiet mode.
        if len(sys.argv) == 1:
            sys.argv.append("py2exe")
            sys.argv.append("-q")
        Executable = lambda x, *y, **z: x
        setup_requires = ["py2exe"]


    except ImportError:
        raise SystemExit('You need py2exe installed to run Couchapp.')
    
elif sys.platform == "linux2":
    import cx_Freeze
    from cx_Freeze import setup, Executable
    
    setup_requires = ["cx_Freeze"]
elif sys.platform == "darwin":
    import py2app

    Executable = lambda x, *y, **z: x
    setup_requires = ["py2app"]

    

from couchapp import __version__
 
setup(
    name = 'Couchapp',
    version = __version__,
    url = 'http://github.com/couchapp/couchapp/tree/master',
    license =  'Apache License 2',
    author = 'Benoit Chesneau',
    author_email = 'benoitc@e-engura.org',
    description = 'Standalone CouchDB Application Development Made Simple.',
    long_description = """CouchApp is a set of helpers and a jQuery plugin
    that conspire to get you up and running on CouchDB quickly and
    correctly. It brings clarity and order to the freedom of CouchDB's
    document-based approach.""",
    keywords = 'couchdb couchapp',
    platforms = ['any'],
    classifiers = [
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Database',
        'Topic :: Utilities',
    ],

    packages= get_couchapp_packages(),
    packages_data = get_packages_data(),

    cmdclass=cmdclass,
    
   
    scripts=get_scripts(),

    zipfile=None,

    data_files=get_data_files(),

    executables=[Executable("Couchapp.py", copyDependentFiles=True)],
    
    windows=[{"script": "couchapp.pyw"}],


    app = ['Couchapp.py'],

    options = dict(py2exe={
                        'compressed': 1,
                        'optimize': 2,
                        "ascii": 1,
                        "excludes": [
                            "pywin",
                            "pywin.debugger",
                            "pywin.debugger.dbgcon",
                            "pywin.dialogs",
                            "pywin.dialogs.list",
                        ],
                        'dll_excludes': [ 
                            "kernelbase.dll",
                            "powrprof.dll"
                            ],
                        'includes': get_include_modules(),
                        'packages': get_package_modules()
                   },

                   build_exe={
                        "compressed": 1,
                        "optimize": 2,
                        "includes": get_include_modules(),
                        "packages": get_package_modules(),
                        "include_files": get_include_files(),
                        "create_shared_zip": 1,
                        "include_in_shared_zip": get_include_files()
                   },

                   bdist_mpkg=dict(zipdist=True,
                                   license='LICENSE',
                                   readme='contrib/macosx/Readme.html',
                                   welcome='contrib/macosx/Welcome.html'),
                   
                   py2app=dict(
                        compressed = False,
                        optimize = 2,
                        argv_emulation = 1,
                        includes =  get_include_modules() + get_couchapp_all_packages(),
                        packages = get_package_modules(),
                        resources =  ["NOTICE", "LICENSE", "README.md", "THANKS.txt",
                              "FAQ", "INSTALL", "README", "THANKS",
                              "TODO"],

                        plist =  {
                            "CFBundleName": "Couchapp",
                            "CFBundleShortVersionString": "0.7.3", # must be in X.X.X format
                            "CFBundleGetInfoString": "Couchapp 0.7.3",
                            "CFBundleExecutable": "Couchapp",
                            "CFBundleIdentifier": "org.couchapp.Couchapp",
                        },
                    )),
                                   
    entry_points={
            
            "distutils.commands": [
                "py2app = py2app.build_app:py2app",
            ],
            
            "distutils.setup_keywords": [
                "app = py2app.build_app:validate_target",
                "plugin = py2app.build_app:validate_target",
            ],
            

            "console_scripts": [
                "py2applet = py2app.script_py2applet:main",
            ],
            
            "py2app.converter": [
                "xib          = py2app.converters.nibfile:convert_xib",
                "datamodel    = py2app.converters.coredata:convert_datamodel",
                "mappingmodel = py2app.converters.coredata:convert_mappingmodel",
            ],
            
            "py2app.recipe": [
            ],
            
            "couchapp.extension": [
                "autotpush=couchapp.ext.autopush"
            ],

            "couchapp.vendor": [
                "git=couchapp.vendors.backends.git:GitVendor",
                "hg=couchapp.vendors.backends.hg:HgVendor",
                "couchdb=couchapp.vendors.backends.couchdb:CouchdbVendor"
            ],

            "couchapp.hook": [
                "compress=couchapp.hooks.compress:hook"
            ]
    },
    
    test_suite='tests',
    setup_requires=setup_requires,
    **extra
)
