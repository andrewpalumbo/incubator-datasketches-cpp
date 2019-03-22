# Modified from:
# http://www.benjack.io/2018/02/02/python-cpp-revisited.html

import os
#import re
import sys
import sysconfig
import platform
import subprocess

from distutils.version import LooseVersion
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: " +
                ", ".join(e.name for e in self.extensions))

        # if platform.system() == "Windows":
        #     cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)',
        #                                            out.decode()).group(1))
        #     if cmake_version < '3.12.0':
        #         raise RuntimeError("Cmake >= 3.12.0 is required")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir]
        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(
                           cfg.upper(),
                           extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
                build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''),
            self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args,
                              cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.', '--target', 'python'] + build_args,
                              cwd=self.build_temp)
        #subprocess.check_call(['cmake', '--build', '.', '--target', 'py_install'] + build_args,
        #                      cwd=self.build_temp)
        print() # add an empty line to pretty print

setup(
    name='datasketches',
    version='0.0.1',
    author='Jon Malkin',
    author_email='jon.malkin@yahoo.com',
    description='A wrapper for the C++ Datasketches library',
    long_description='',
    # tell setuptools to look for any packages under 'src'
    packages=find_packages('python/src'),
    # tell setuptools that all packages will be under the 'src' directory
    # and nowhere else
    package_dir={'':'python/src'},
    # add an extension module named 'python_cpp_example' to the package 
    # 'python_cpp_example'
    #ext_modules=[CMakeExtension('datasketches/datasketches')],
    ext_modules=[CMakeExtension('datasketches')],
    # add custom build_ext command
    cmdclass=dict(build_ext=CMakeBuild)
    #zip_safe=False
)
