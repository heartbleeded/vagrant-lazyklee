#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import atexit
import os
from commands import getoutput, getstatusoutput

GRAY = "\033[90m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
ENDC = "\033[0m"

def indent(text, width=4):
    return " " * width + text.replace("\n", "\n" + " " * width)

def vagrant_exec(cmd):
    if args.verbose:
        print indent(GRAY + "$ " + cmd + ENDC)
    return getstatusoutput("vagrant ssh -c \"%s\"" % cmd)

def compile_bitcode(file_name, out_name):
    print "[+] Compiling llvm bitcode..."
    cmd = "clang -emit-llvm -c -g -DKLEE -I klee_src/include/"

    with open(args.src, "r") as f:
        code = f.read()
    if "klee.h" not in code:
        cmd += " -include klee_src/include/klee/klee.h"
        print indent(GREEN + "Auto include klee_build/klee.h" + ENDC)
    if "assert.h" not in code:
        cmd += " -include klee_build/klee-uclibc/include/assert.h"
        print indent(GREEN + "Auto include assert.h" + ENDC)
    if args.clang_args:
        cmd += " " + args.clang_args
    cmd += " sharedFolder/LazyKLEE/%s -o %s" % (file_name, out_name)

    ret, out = vagrant_exec(cmd)
    out = out.replace("warning:", YELLOW + "warning" + GRAY + ":")
    out = out.replace("error:", RED + "error" + GRAY + ":")
    if out:
        print indent(GRAY + out + ENDC)
    if ret:
        exit()

def run_klee(out_name):
    print "[+] Running KLEE..."
    cmd = "klee -check-overshift=0 -check-div-zero=0"
    if args.optimize:
        cmd += " -optimize"
    if args.libc:
        cmd += " -libc=uclibc"
    if args.posix:
        cmd += " -posix-runtime"
    if args.klee_args:
        cmd += " " + args.klee_args
    cmd += " " + out_name
    if args.args:
        cmd += " " + args.args

    ret, out = vagrant_exec(cmd)
    out = out.replace("WARNING:", YELLOW + "WARNING" + GRAY + ":")
    out = out.replace("WARNING ONCE:", YELLOW + "WARNING ONCE" + GRAY + ":")
    out = out.replace("ERROR:", RED + "ERROR" + GRAY + ":")
    out = GRAY + out + ENDC
    if "ASSERTION FAIL" in out:
        if args.verbose:
            print indent(out)
        print "[!] " + GREEN + "ASSERTION triggered!" + ENDC

        _, out = vagrant_exec("ls ./klee-last/ | grep .assert.err")
        test_case = out.split(".")[0] + ".ktest"
        cmd = "ktest-tool "
        if args.write_ints:
            cmd += "--write-ints "
        cmd += "./klee-last/%s" % test_case
        _, out = vagrant_exec(cmd)
        print indent(out)
    else:
        print indent(out)
        print "[!] " + RED + "ASSERTION not triggered..." + ENDC

def cleanup():
    if args.interact:
        print "\n[+] Entering container..."
        os.system("vagrant ssh")
        if getoutput("VBoxManage list runningvms | grep klee"):
            print "[+] Removing output files..."
            vagrant_exec("rm -rf klee-*")

def main():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="source code")
    parser.add_argument("-v", "--verbose", help="show verbose message", action="store_true")
    parser.add_argument("-i", "--interact", help="interact with container after running KLEE", action="store_true")
    parser.add_argument("-o", "--optimize", help="run KLEE with -optimize", action="store_true")
    parser.add_argument("-l", "--libc", help="run KLEE with -libc=uclibc", action="store_true")
    parser.add_argument("-p", "--posix", help="run KLEE with -posix-runtime", action="store_true")
    parser.add_argument("-w", "--write-ints", help="convert 4-byte sequences to integers in ktest-tool", action="store_true")
    parser.add_argument("-c", "--clang-args", help="additional arguments for clang")
    parser.add_argument("-k", "--klee-args", help="additional arguments for KLEE")
    parser.add_argument("-a", "--args", help="additional arguments for target program")
    args = parser.parse_args()

    print "=== LazyKLEE ==="

    if not os.path.isfile(args.src):
        print "Souce code [%s] not found!" % args.src
        exit()

    if not getoutput("which vagrant"):
        print "docker not found, install docker first"
        exit()

    if not getoutput("VBoxManage list runningvms | grep klee"):
        print "KLEE image not found, run `docker pull klee/klee` first"
        exit()

    path = os.path.dirname(os.path.abspath(args.src))
    file_name = os.path.basename(args.src)
    out_name = os.path.splitext(file_name)[0] + ".bc"

    atexit.register(cleanup)

    compile_bitcode(args.src, out_name)
    run_klee(out_name)

if __name__ == "__main__":
    main()

