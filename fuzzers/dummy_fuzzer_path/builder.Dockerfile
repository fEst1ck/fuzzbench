# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG parent_image
FROM $parent_image

# Update the package list and install necessary dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    wget \
    cargo \
    git \
    lsb-release software-properties-common gnupg

RUN rm -rf /usr/local/bin/clang /usr/local/bin/clang++ /usr/local/bin/llvm*
RUN rm -rf /usr/local/lib/clang
RUN rm -rf /usr/local/include/clang
RUN rm -rf /usr/local/share/clang

# Install LLVM 19
# Download the LLVM installation script
RUN wget https://apt.llvm.org/llvm.sh && \
    chmod +x llvm.sh

# Install LLVM 19 using the script
RUN ./llvm.sh 19

# Clean up by removing the installation script
RUN rm llvm.sh

# Set the default clang and clang++ to the installed version
RUN update-alternatives --install /usr/bin/clang clang /usr/bin/clang-19 100 && \
    update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-19 100

# Install path-cov-instr for path coverage instrumentation
RUN git clone https://github.com/fEst1ck/path-cov-instr.git && \
    cd path-cov-instr && \
    git checkout 0095e75244e2f62a578a621d1e57a14a53faa37d && \
    # export CC=clang-19 CXX=clang++-19 && \
    make && \
    cp libCodeCoveragePass.so /libCodeCoveragePass.so && \
    cp coverage_runtime.o /coverage_runtime.o && \
    cp path-clang /path-clang && \
    cp path-clang++ /path-clang++

# Install path-cov for path reduction
RUN git clone https://github.com/fEst1ck/path-cov.git && \
    cd path-cov && \
    git checkout 9d8fc8c73d86e63bbec64cdb3cef5608719a88a8

# Uninstall old Rust
RUN if which rustup; then rustup self uninstall -y; fi

# Install latest Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > /rustup.sh && \
    sh /rustup.sh -y

ENV PATH="/root/.cargo/bin:${PATH}"

# Install the dummy fuzzer
RUN git clone https://github.com/fEst1ck/dummy-fuzzer && \
    cd dummy-fuzzer && \
    git checkout a87b211e4871ca8d9dca6c724697b3dfe6755c50 && \
    cargo build --release && \
    cp target/release/dummy-fuzzer /dummy-fuzzer

COPY FuzzTarget.c /FuzzTarget.c
RUN clang -O2 -c /FuzzTarget.c && \
    ar rc /libStandaloneFuzzTarget.a FuzzTarget.o && \
    rm /FuzzTarget.c