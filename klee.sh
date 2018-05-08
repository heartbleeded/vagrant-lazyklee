#!/bin/bash
export LLVM_VERSION=3.4 
export SOLVERS=STP:Z3 
export STP_VERSION=2.1.2 
export DISABLE_ASSERTIONS=0 
export ENABLE_OPTIMIZED=1 
export KLEE_UCLIBC=klee_uclibc_v1.0.0 
export KLEE_SRC=/home/vagrant/klee_src 
export COVERAGE=0 
export BUILD_DIR=/home/vagrant/klee_build 
export ASAN_BUILD=0 
export UBSAN_BUILD=0 
export TRAVIS_OS_NAME=linux
sudo apt-get update
sudo apt-get -y --no-install-recommends install clang-${LLVM_VERSION} llvm-${LLVM_VERSION} llvm-${LLVM_VERSION}-dev llvm-${LLVM_VERSION}-runtime llvm libcap-dev git subversion cmake make libboost-program-options-dev python3 python3-dev python3-pip perl flex bison libncurses-dev zlib1g-dev patch wget unzip binutils
sudo pip3 install -U lit tabulate wllvm
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 50
( wget -O - http://download.opensuse.org/repositories/home:delcypher:z3/xUbuntu_14.04/Release.key | sudo apt-key add - )
sudo sh -c "echo 'deb http://download.opensuse.org/repositories/home:/delcypher:/z3/xUbuntu_14.04/ /' >> /etc/apt/sources.list.d/z3.list"
sudo apt-get update
cd ~
git clone https://github.com/klee/klee ${KLEE_SRC}
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}
${KLEE_SRC}/.travis/solvers.sh
cd ${BUILD_DIR} && mkdir test-utils && cd test-utils
${KLEE_SRC}/.travis/testing-utils.sh
sudo ln -s /usr/bin/clang /usr/bin/clang-${LLVM_VERSION}
sudo ln -s /usr/bin/clang++ /usr/bin/clang++-${LLVM_VERSION}
cd ${BUILD_DIR}
${KLEE_SRC}/.travis/klee.sh
echo 'export PATH=$PATH:'${BUILD_DIR}'/klee/bin' >> /home/vagrant/.bashrc
for executable in ${BUILD_DIR}/klee/bin/* ; do sudo ln -s ${executable} /usr/bin/`basename ${executable}`; done