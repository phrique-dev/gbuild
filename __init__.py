"""
GBUILD is a Python package for making scripts to compile executables for C/C++
the only reason this package exist is to make the process of compiling C less annoying

by: voidksks
"""
import os

# constants
RED = "\033[31m"
YELLOW = "\033[33m"
END = "\033[m"

CPP_SUFFIXES = (".cpp", ".cxx", ".cc", ".ipp", ".ixx")
C_SUFFIXES = (".c",)
SOURCE_SUFFIXES = CPP_SUFFIXES + C_SUFFIXES

# gbuild methods
def gb_log_error(msg: str):
    print(f"{RED}[GBUILD]: {msg}{END}")

def gb_log_warning(msg: str):
    print(f"{RED}[GBUILD]: {msg}{END}")

def gb_try_compile(args: list[str]):
    import subprocess
    try:
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError:
        gb_log_error("Compile error...")
    except OSError:
        gb_log_warning("Cannot run the command...")

def gb_search_dir(target: str, path=".", recursive=False):
    with os.scandir(path) as entries:
        for item in entries:
            if item.is_dir() and item.name == target:
                return True
            if recursive and item.is_dir():
                gb_search_dir(target, item.path)
    return False

def gb_search_file(target: str, path=".", recursive=False):
    with os.scandir(path) as entries:
        for item in entries:
            if item.is_file() and item.name == target:
                return True
            if recursive and item.is_file():
                gb_search_file(target, item.path)
    return False

def gb_is_empty(iterable):
    return len(iterable) == 0

# "private" class for grouping all flags and stuff
class cmd():
    def __init__(self, compiler: str):
        self.compiler = compiler
        self.source_files = []
        self.out = ""
        self.flags = []
        self.includes = []

# Class for building the binaries
class Builder():
    def __init__(self, compiler):
        self._cmd = cmd(compiler)

    # getters
    def compiler(self):
        return self._cmd.compiler

    def executable_name(self):
        return self._cmd.out

    def source_files(self):
        return self._cmd.source_files

    def includes(self):
        return self._cmd.includes

    def flags(self):
        return self._cmd.flags

    # setters and methods
    def set_compiler(self, name: str):
        self._cmd.compiler = name

    def set_executable_name(self, name: str):
        from sys import platform
        if gb_is_empty(self._cmd.out):
            if platform == "win32" and ".exe" not in name:
                self._cmd.out = name + ".exe"
            else:
                self._cmd.out = name

    def include(self, path: str):
        if not gb_is_empty(path):
            p = f"-I{path}"
            self._cmd.includes.append(p)

    def search_sources(self, path: str, recursive=False):
        """
        Enter the path and search for valid source code files, and
        returns a list of source code paths.
        """
        sources = self._cmd.source_files
        with os.scandir(path) as entries:
            for item in entries:
                if item.is_file() and item.name.endswith(SOURCE_SUFFIXES):
                    sources.append(item.path)
                if item.is_dir() and recursive:
                    self.search_sources(item.path)

    def set_flags(self, *args):
        """
        Set flags for the compiler
        """
        self._cmd.flags += list(args)

    def build_executable(self, executablename="", builddir="."):
        """
        Build an executable to a given build path
        """
        if gb_is_empty(self._cmd.compiler):
            gb_log_error("Cannot detect compiler... Compilation failed!")
            return

        if gb_is_empty(executablename) and self._cmd.out is not None:
            executablename = self._cmd.out

        if builddir != "." and not gb_search_dir(builddir):
            os.makedirs(builddir, exist_ok=True)

        if gb_is_empty(self._cmd.source_files):
            gb_log_error("No source files was specified...")
            return

        cmd = [self._cmd.compiler, *self._cmd.flags, *self._cmd.includes, *self._cmd.source_files]
        if executablename:
            if "/" not in builddir:
                builddir += "/"
            cmd += ["-o" ,f"{builddir}{executablename}"]
            gb_try_compile(cmd)
        else:
            gb_log_error("Executable name was not defined...")
