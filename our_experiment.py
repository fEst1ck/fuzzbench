import subprocess

fuzzers = [
    "block",
    "edge",
    "path",
    # "peb",
    "pfp"
]

benchmarks = [
    #"systemd_fuzz-link-parser",
    #"systemd_fuzz-link-parser",
    # "jsoncpp_jsoncpp_fuzzer",
    # "jsoncpp_jsoncpp_fuzzer",
    "zlib_zlib_uncompress_fuzzer",
    "libxml2_xml",
    #"vorbis_decode_fuzzer",
    #"zlib_zlib_uncompress_fuzzer",
    # "re2_fuzzer",
    # "woff2_convert_woff2ttf_fuzzer",
    # "sqlite3_ossfuzz"
]

core_id = 0  # Start from core 0

for fuzzer in fuzzers:
    for benchmark in benchmarks:
        session_name = f"{fuzzer}_{benchmark}"

        shell_cmd = (
            "cd ~/fuzzbench && "
            f"export FUZZER_NAME=dummy_fuzzer_{fuzzer} && "
            f"export BENCHMARK_NAME={benchmark} && "
            f"make build-$FUZZER_NAME-$BENCHMARK_NAME && "
            f"make run-$FUZZER_NAME-$BENCHMARK_NAME; "
            "echo '[!] Done or failed. Press Ctrl-A D to detach.'; exec bash"
        )

        # Wrap the command with taskset to bind it to a single core
        taskset_cmd = f"taskset -c {core_id} bash -c '{shell_cmd}'"
        # screen_cmd = f"screen -dmS {session_name} {taskset_cmd}"
        screen_cmd = f"screen -dmS {session_name} bash -c '{shell_cmd}'"

        # print(f"Starting screen session: {session_name} on CPU core {core_id}")
        subprocess.run(screen_cmd, shell=True, check=True)

        core_id += 1  # Move to the next CPU core for the next experiment
