# install_clcache_msbuild

Since the integration of `clcache` with `msbuild` is rather cumbersome, 
this script provide an helper in order to simplify the process.

It is compatible with MSVC 2010, 2015 and 2017 (tested with MSVC 2015 and 2017).

## What this script does:

* Check that python3 and pip3 are installed and are in the PATH
* Check that the pip installed scripts are in the PATH (PYTHONHOME\Scripts)
* Call `pip install .` from the repo and check that clcache is then in the PATH.
  `clcache` will subsequently be used from the PYTHONHOME\\Scripts directory.
* Modify the user msbuild preference files inside `%AppData%\..\Local\Microsoft\MSBuild\v4.0`
  so that clcache becomes the default compiler. (These prefs are shared between MSVC 2010 to 2017).
* Find all cl.exes version on your computer (for MSVC 2010 to MSVC 2017), and allows you 
  to select the correct one, by showing a detailed list of their version and target architecture.
* Set the env variable `CLCACHE_CL` with the correct path to cl.exe

As additional options, this script can also 
* change the cache location
* change the cache size
* change the timeout CLCACHE_OBJECT_CACHE_TIMEOUT_MS

## Caveat 
Since the msbuild preference files inside `%AppData%\..\Local\Microsoft\MSBuild\v4.0` are shared
between different MSVC installations, clcache will be activated for all instances of MSVC.

## Note
`vswhere.exe` is a tool provided by Microsoft in order to locate installations of MSVC >= 2017.

## Usage

````
usage: install_clcache_msbuild.py [-h] [--cachedir CACHEDIR]
                                  [--cache_size CACHE_SIZE]
                                  [--clcache_timeout CLCACHE_TIMEOUT]
                                  {status,install,enable,disable,enable_logs,disable_logs,show_cl_list,select_cl}
````

Sample usage session:

````bash
> python install_clcache_msbuild.py install
Looking for python in PATH
C:\Python36-32\python.exe
Looking for pip in PATH
C:\Python36-32\Scripts\pip.exe

######################################################################
Installing clcache (installClcache)
######################################################################
====> pip install .(in folder F:\dvp\OpenSource\clcache)
Processing f:\dvp\opensource\clcache
Requirement already satisfied: pymemcache in c:\python36-32\lib\site-packages (from clcache==4.1.1.dev65+g105e486.d20181119) (2.0.0)
Requirement already satisfied: pyuv in c:\python36-32\lib\site-packages (from clcache==4.1.1.dev65+g105e486.d20181119) (1.4.0)
Requirement already satisfied: six in c:\python36-32\lib\site-packages (from pymemcache->clcache==4.1.1.dev65+g105e486.d20181119) (1.11.0)
Installing collected packages: clcache
  Found existing installation: clcache 4.1.1.dev65+g105e486.d20181119
    Uninstalling clcache-4.1.1.dev65+g105e486.d20181119:
      Successfully uninstalled clcache-4.1.1.dev65+g105e486.d20181119
  Running setup.py install for clcache ... done
Successfully installed clcache-4.1.1.dev65+g105e486.d20181119
You are using pip version 10.0.1, however version 18.1 is available.
You should consider upgrading via the 'python -m pip install --upgrade pip' command.
Looking for clcache in PATH
C:\Python36-32\Scripts\clcache.exe

######################################################################
Force clcache via Msbbuild user settings (copyMsvcPrefClcache)
######################################################################
Wrote pref in C:\Users\pascal\AppData\Local\Microsoft\MSBuild\v4.0\Microsoft.Cpp.ARM.user.props
Wrote pref in C:\Users\pascal\AppData\Local\Microsoft\MSBuild\v4.0\Microsoft.Cpp.Win32.user.props
Wrote pref in C:\Users\pascal\AppData\Local\Microsoft\MSBuild\v4.0\Microsoft.Cpp.x64.user.props

######################################################################
Select cl compiler: (selectCl)
######################################################################
   #           version targetArch   hostArch                                                              folder (shortened)
   1              14.0      amd64      amd64                                               C:\ProgX86\MSVC 14.0\vc\bin\amd64
   2              14.0        arm      amd64                                           C:\ProgX86\MSVC 14.0\vc\bin\amd64_arm
   3              14.0        x86      amd64                                           C:\ProgX86\MSVC 14.0\vc\bin\amd64_x86
   4              14.0      amd64        x86                                           C:\ProgX86\MSVC 14.0\vc\bin\x86_amd64
   5              14.0        arm        x86                                             C:\ProgX86\MSVC 14.0\vc\bin\x86_arm
   6              14.0        x86        x86                                                     C:\ProgX86\MSVC 14.0\vc\bin
   7   15.7.27703.2047        x64        x64       C:\ProgX86\MSVC\2017\Enterprise\VC\Tools\MSVC\14.14.26428\bin\Hostx64\x64
   8   15.7.27703.2047        x86        x64       C:\ProgX86\MSVC\2017\Enterprise\VC\Tools\MSVC\14.14.26428\bin\Hostx64\x86
   9   15.7.27703.2047        x64        x86       C:\ProgX86\MSVC\2017\Enterprise\VC\Tools\MSVC\14.14.26428\bin\Hostx86\x64
  10   15.7.27703.2047        x86        x86       C:\ProgX86\MSVC\2017\Enterprise\VC\Tools\MSVC\14.14.26428\bin\Hostx86\x86
Enter the number corresponding to the desired compiler: 6
Selected : C:\Program Files (x86)\Microsoft Visual Studio 14.0\vc\bin\cl.exe
====> SETX CLCACHE_CL "C:\Program Files (x86)\Microsoft Visual Studio 14.0\vc\bin\cl.exe"

SUCCESS: Specified value was saved.

######################################################################
Note about clcache usage: (showClCacheUsage)
######################################################################
====> clcache --help
clcache.py v4.1.0-dev
  --help    : show this help
  -s        : print cache statistics
  -c        : clean cache
  -C        : clear cache
  -z        : reset cache statistics
  -M <size> : set maximum cache size (in bytes)
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

