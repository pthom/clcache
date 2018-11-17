# install_clcache_msbuild

Since the integration of `clcache` with `msbuild` is rather cumbersome, 
this script provide an helper in order to simplify the process.

## What this script does:

* Check that python3 and pip3 are installed and are in the PATH
* Check that the pip installed scripts are in the PATH (PYTHONHOME\Scripts)
* Call `pip install .` from the repo and check that clcache is then in the PATH.
  `clcache` will subsequently be used from the PYTHONHOME\\Scripts directory.
* Modify the user msbuild preference files inside `%AppData%\..\Local\Microsoft\MSBuild\v4.0`
  so that clcache becomes the default compiler
* Set the env variable `CLCACHE_CL` with the correct path to cl.exe

As additional options, this script can also 
* change the cache location
* change the cache size
* change the timeout CLCACHE_OBJECT_CACHE_TIMEOUT_MS

Usage : 

````
c:
cd C:\clcache\install_for_msbuild
python install_clcache_msbuild.py -h

usage: install_clcache_msbuild.py [-h] [--cachedir CACHEDIR]
                                  [--cache_size CACHE_SIZE]
                                  [--clcache_timeout CLCACHE_TIMEOUT]
                                  {status,install,disable,enable_logs,disable_logs}

Configure clcache for use with msbuild

positional arguments:
  {status,install,disable,enable_logs,disable_logs}
                        action

optional arguments:
  -h, --help            show this help message and exit
  --cachedir CACHEDIR   clcache directory
  --cache_size CACHE_SIZE
                        clcache size in Go
  --clcache_timeout CLCACHE_TIMEOUT
                        clcache object cache timeout in seconds (increase if
                        you have failures during your build)

Actions summary:
    status       : Show the install status and tells if clcache is enabled
    install:     : Install and enable clcache for msbuild integration"
    disable:     : Disable clcache
    enable_logs  : Activate clcache logs during builds
    disable_logs : Disable clcache logs during builds

````



# Caveats with msbuild and clcache : 

## incremental builds with clcache and msbuild

clcache has serious isses with incremental builds. After a full build, you will always get a full rebuild even if you modify only one file !

There is a pull request that succesfully correct this here: https://github.com/frerich/clcache/pull/319/commits



## clcache is not compatible with `/Zi` debug information format : use `/Z7` instead.

See 
https://github.com/frerich/clcache/issues/30 
and https://stackoverflow.com/questions/284778/what-are-the-implications-of-using-zi-vs-z7-for-visual-studio-c-projects

With cmake, you can do the following:


  ```cmake
  message("msvc_clccache_force_z7_debug_format use /Z7 debug format")
  if(MSVC)
    string(REGEX REPLACE "/Z[iI7]" ""
           CMAKE_CXX_FLAGS_DEBUG
           "${CMAKE_CXX_FLAGS_DEBUG}")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Z7")
  endif()
  ````

