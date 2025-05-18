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
"""Integration code for pathAFL fuzzer."""

import os
import shutil
import subprocess

from fuzzers import utils


def prepare_build_environment():
    """Set environment variables used to build targets for pathAFL-based
    fuzzers."""
    os.environ["CC"] = "/path-clang"
    os.environ["CXX"] = "/path-clang++"
    os.environ["FUZZER"] = "/dummy-fuzzer"
    os.environ["FUZZER_LIB"] = "/libStandaloneFuzzTarget.a"


def build():
    """Build benchmark."""
    prepare_build_environment()

    utils.build_benchmark()

    print("[post_build] Copying afl-fuzz to $OUT directory")

    # Copy out the afl-fuzz binary as a build artifact.
    shutil.copy("/.coverage_data/coverage.json", os.environ["OUT"])
    shutil.copy("/dummy-fuzzer", os.environ["OUT"])


def prepare_fuzz_environment(input_corpus):
    """Prepare to fuzz with AFL or another AFL-based fuzzer."""
    # Tell AFL to not use its terminal UI so we get usable logs.
    os.environ['CFG_FILE'] = './coverage.json'
    os.environ['FUZZER_LIB'] = '/libStandaloneFuzzTarget.a'

    # AFL needs at least one non-empty seed to start.
    utils.create_seed_file_for_empty_corpus(input_corpus)


def run_afl_fuzz(input_corpus,
                 output_corpus,
                 target_binary):
    """Run afl-fuzz."""
    # Spawn the afl fuzzing process.
    print('[run_afl_fuzz] Running target with afl-fuzz')
    # os.environ["DEBUG"] = "1"
    # os.environ["RUST_LOG"] = "info"
    command = [
        './dummy-fuzzer',
        '-i',
        input_corpus,
        '-o',
        output_corpus,
        '-j',
        '4',
        '-c',
        'block,edge,path,pfp',
        '-u',
        'edge,pfp',
        '--',
        target_binary,
    ]
    subprocess.check_call(command)


def fuzz(input_corpus, output_corpus, target_binary):
    """Run afl-fuzz on target."""
    prepare_fuzz_environment(input_corpus)

    run_afl_fuzz(input_corpus, output_corpus, target_binary)