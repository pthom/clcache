
import ctypes
import sys
import subprocess
import os
import os.path
import winreg
import argparse


def dirAbsolutePath(folder):
    return os.path.abspath(os.path.realpath(folder))


THIS_DIR = dirAbsolutePath(os.path.dirname(__file__))
CLCACHE_REPO_DIR = dirAbsolutePath(THIS_DIR + "\\..")
MSVC_BIN_FOLDER = "C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\VC\\bin\\"
MSBUILD_USER_SETTINGS_DIR = dirAbsolutePath(os.getenv('APPDATA') + "\\..\\Local\\Microsoft\\MSBuild\\v4.0")
MSBUILD_SETTING_FILE_CONTENT_CLCACHE = """<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ImportGroup Label="PropertySheets">
  </ImportGroup>
  <PropertyGroup Label="UserMacros" />
  <PropertyGroup />
  <PropertyGroup>
    <CLToolExe>clcache.exe</CLToolExe>
  </PropertyGroup>
  <ItemDefinitionGroup />
  <ItemGroup />
</Project>
"""
MSBUILD_SETTING_FILE_CONTENT_NO_CLCACHE = """<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ImportGroup Label="PropertySheets">
  </ImportGroup>
  <PropertyGroup Label="UserMacros" />
  <PropertyGroup />
  <ItemDefinitionGroup />
  <ItemGroup />
</Project>
"""


def isAdmin():
    return ctypes.windll.shell32.IsUserAnAdmin()


def currentFuncName(n=0):
    return sys._getframe(n + 1).f_code.co_name #pylint: disable=W0212


def hasProgramInPath(prog):
    print("Looking for " + prog + " in PATH")
    result = subprocess.call("where " + prog)
    if result != 0:
        print(prog + " not found in PATH")
    return result == 0


def whereProgram(prog):
    allProgrs = subprocess.check_output("where " + prog).decode("utf-8")
    firstProg = allProgrs.split("\r")[0]
    return firstProg


def showCmd(cmd):
    print("====> " + cmd)


def callAndShowCmd(command: str, cwd: str = None) -> bool:
    if cwd is not None:
        print("====> " + command + "(in folder " + cwd +  ")")
    else:
        print("====> " + command)
    if cwd is not None:
        return subprocess.call(command, cwd=cwd) == 0
    else:
        return subprocess.call(command) == 0


def implSetAndStoreEnvVariable(name, value, allUsers=False):
    """
    Stocke une variable d'environnement touts utilisateurs sous windows
    """
    if allUsers:
        cmd = "SETX {0} \"{1}\" /M".format(name, value)
    else:
        cmd = "SETX {0} \"{1}\"".format(name, value)
    if not callAndShowCmd(cmd):
        return False
    os.environ[name] = value
    return True


def setAndStoreEnvVariable(name, value):
    return implSetAndStoreEnvVariable(name, value, allUsers=isAdmin())


def implRemoveEnvVariable(name, allUsers=False):
    if allUsers:
        command = "REG DELETE HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment /F /V " + name
    else:
        command = "REG DELETE HKCU\\Environment /F /V " + name
    if not callAndShowCmd(command):
        return False
    if name is os.environ:
        os.environ.pop(name, None)
    return True


def removeEnvVariable(name):
    return implRemoveEnvVariable(name, allUsers=isAdmin())


def implReadEnvVariableFromRegistry(name, allUsers=False) -> str:
    if allUsers:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg, r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment")
    else:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(reg, r"Environment")
    try:
        result = winreg.QueryValueEx(key, name)
    except FileNotFoundError:
        return None
    return result[1]


def readEnvVariableFromRegistry(name):
    return implReadEnvVariableFromRegistry(name, allUsers=isAdmin())


def showStepIntro(details=0):
    print()
    print("######################################################################")
    print(details + " (" + currentFuncName(1) + ")")
    print("######################################################################")


def installClcache():
    showStepIntro("Installing clcache")
    status = callAndShowCmd("pip install .", cwd=CLCACHE_REPO_DIR)
    if not status:
        return False
    if not hasProgramInPath("clcache"):
        print("Humm. its seems that the install failed")
        return False
    return True


def listFiles(folder, appendFolder=True):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if appendFolder:
        files = [os.path.join(folder, f) for f in files]
    return files


def implCopyMsvcPref(prefContent):
    files = listFiles(MSBUILD_USER_SETTINGS_DIR)
    for file in files:
        with open(file, 'w') as f:
            f.write(prefContent)
            print("Wrote pref in " + file)
    return True


def copyMsvcPrefClcache():
    showStepIntro("Force clcache via Msbbuild user settings")
    return implCopyMsvcPref(MSBUILD_SETTING_FILE_CONTENT_CLCACHE)


def copyMsvcPrefOriginal():
    showStepIntro("Disable clcache via Msbbuild user settings")
    return implCopyMsvcPref(MSBUILD_SETTING_FILE_CONTENT_NO_CLCACHE)


def clcacheSetEnv():
    showStepIntro("set CLCACHE_CL env variable")
    if not setAndStoreEnvVariable("CLCACHE_CL", MSVC_BIN_FOLDER + "\\cl.exe"):
        return False
    # CLCACHE_OBJECT_CACHE_TIMEOUT_MS
    return True


def enableLogs():
    return setAndStoreEnvVariable("CLCACHE_LOG", "1")


def disableLogs():
    return removeEnvVariable("CLCACHE_LOG")


def showClCacheUsage():
    showStepIntro("Note about clcache usage:")
    subprocess.run("clcache --help")
    return True


def fullClcacheSetup():
    if not installClcache():
        return False
    if not copyMsvcPrefClcache():
        return False
    if not clcacheSetEnv():
        return False
    if not showClCacheUsage():
        return False
    return True


def clCacheDisable():
    if not copyMsvcPrefOriginal():
        return False
    return True


def showStatus():
    if hasProgramInPath("clcache"):
        print("clcache is in your PATH")
    else:
        print("clcache is not installed")

    if readEnvVariableFromRegistry("CLCACHE_LOG") is not None:
        print("logs are enabled")
    else:
        print("logs are disabled")

    prefFile = MSBUILD_USER_SETTINGS_DIR + "\\Microsoft.Cpp.Win32.user.props"
    isEnabled = False
    with open(prefFile, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "<CLToolExe>clcache.exe</CLToolExe>" in line:
                isEnabled = True
    if isEnabled:
        print("clcache is *ENABLED* in " + MSBUILD_USER_SETTINGS_DIR)
    else:
        print("clcache is *NOT ENABLED* in " + MSBUILD_USER_SETTINGS_DIR)
    print("call clcache -s for statistics")
    return True


def makeInitialChecks():
    if not hasProgramInPath("python"):
        print("This program needs python 3")
        return False
    if not hasProgramInPath("pip"):
        print("This program needs pip 3")
        return False

    if not "python 3" in subprocess.check_output(["python", "--version"]).decode("utf-8").lower():
        print("Bad python version : this program needs python 3")
        return False

    if not "python 3" in subprocess.check_output(["pip", "--version"]).decode("utf-8").lower():
        print("Bad pip version : this program needs pip for python 3")
        return False

    pipScriptsDir = os.path.dirname(whereProgram("python")) + "\\Scripts"
    if pipScriptsDir.lower() not in os.environ["PATH"].lower():
        print("Can't find pip_scripts_dir in your PATH. pip_scripts_dir=" + pipScriptsDir)
        print("Please add this to your PATH")
        return False
    return True


def main():
    epilog = """Actions summary:
    status       : Show the install status and tells if clcache is enabled    
    install:     : Install and enable clcache for msbuild integration"
    disable:     : Disable clcache
    enable_logs  : Activate clcache logs during builds
    disable_logs : Disable clcache logs during builds
    """
    helpTimeout = """clcache object cache timeout in seconds
    (increase if you have failures during your build)
    """
    parser = argparse.ArgumentParser(
        description="Configure clcache for use with msbuild",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    choices = ["status", "install", "disable", "enable_logs", "disable_logs"]
    parser.add_argument("action", choices=choices, help="action")
    parser.add_argument("--cachedir", help="clcache directory")
    parser.add_argument("--cache_size", help="clcache size in Go", type=int, default=0)
    parser.add_argument("--clcache_timeout", help=helpTimeout, type=int, default=0)

    if sys.argv[0][-3:] == ".py":
        argv = sys.argv[1:]
    else:
        argv = sys.argv
    args = parser.parse_args(argv)

    if args.action == "status":
        if not showStatus():
            return False
    elif args.action == "install":
        if not makeInitialChecks():
            return False
        if not fullClcacheSetup():
            return False
    elif args.action == "disable":
        if not clCacheDisable():
            return False
    elif args.action == "enable_logs":
        if not enableLogs():
            return False
    elif args.action == "disable_logs":
        if not disableLogs():
            return False

    if args.cachedir is not None:
        setAndStoreEnvVariable("CLCACHE_DIR", args.cachedir)

    if args.cache_size > 0:
        giga = 1024 * 1024 * 1024
        byteSize = giga * args.cache_size
        if not callAndShowCmd("clcache -M " +str(byteSize)):
            return False

    if args.clcache_timeout > 0:
        timeMs = args.clcache_timeout * 1000
        setAndStoreEnvVariable("CLCACHE_OBJECT_CACHE_TIMEOUT_MS", str(timeMs))

    return True


if __name__ == "__main__":
    if not main():
        print("FAILURE")
        sys.exit(1)
