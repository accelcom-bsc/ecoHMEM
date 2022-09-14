#!/usr/bin/env bats

bats_require_minimum_version 1.5.0

setup() {
    export ECOHMEM_HOME=../
    export EHTEST_SCRIPT="$ECOHMEM_HOME/scripts/run.sh"
    export EHTEST_PRINT_ARGS="$ECOHMEM_HOME/tests/print_args"
}

@test "app with args from env vars" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'import sys;print(\"Hello\");print(\"World\",file=sys.stderr)'"
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = "Hello" ]
    [ "$stderr" = "World" ]
    [ "$status" -eq 0 ]
}

@test "print commands env var works" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'import sys;print(\"Hello\");print(\"World\",file=sys.stderr)'"
    export ECOHMEM_PRINT_CMDS=1
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = $'|EH| Executing: python3 -c import sys;print("Hello");print("World",file=sys.stderr)\nHello' ]
    [ "$stderr" = "World" ]
    [ "$status" -eq 0 ]
}

@test "flag --app-args overrides env var" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'import sys;print(\"Hello\");print(\"World\",file=sys.stderr)'"
    run --separate-stderr "$EHTEST_SCRIPT" --app-args "-c 'import sys;print(\"Bye\");print(\"Moon\",file=sys.stderr)'"
    [ "$output" = "Bye" ]
    [ "$stderr" = "Moon" ]
    [ "$status" -eq 0 ]
}

@test "flag --app-args= overrides env var" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'import sys;print(\"Hello\");print(\"World\",file=sys.stderr)'"
    run --separate-stderr "$EHTEST_SCRIPT" --app-args="-c 'import sys;print(\"Bye\");print(\"Moon\",file=sys.stderr)'"
    [ "$output" = "Bye" ]
    [ "$stderr" = "Moon" ]
    [ "$status" -eq 0 ]
}

@test "app runner from env vars" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    export ECOHMEM_APP_RUNNER=$EHTEST_PRINT_ARGS
    run --separate-stderr "$EHTEST_SCRIPT"
    expected=$(cat <<END
argc = 4
0: |$EHTEST_PRINT_ARGS|
1: |python3|
2: |-c|
3: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flag --app-runner overrides env var" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    export ECOHMEM_APP_RUNNER=echo
    run --separate-stderr "$EHTEST_SCRIPT" --app-runner $EHTEST_PRINT_ARGS
    expected=$(cat <<END
argc = 4
0: |$EHTEST_PRINT_ARGS|
1: |python3|
2: |-c|
3: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flag --app-runner= overrides env var" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    export ECOHMEM_APP_RUNNER=echo
    run --separate-stderr "$EHTEST_SCRIPT" --app-runner=$EHTEST_PRINT_ARGS
    expected=$(cat <<END
argc = 4
0: |$EHTEST_PRINT_ARGS|
1: |python3|
2: |-c|
3: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "app runner with flags from env vars" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    export ECOHMEM_APP_RUNNER=$EHTEST_PRINT_ARGS
    export ECOHMEM_APP_RUNNER_FLAGS="some flags"
    run --separate-stderr "$EHTEST_SCRIPT"
    expected=$(cat <<END
argc = 6
0: |$EHTEST_PRINT_ARGS|
1: |some|
2: |flags|
3: |python3|
4: |-c|
5: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flag --runner-flags overrides env var" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    export ECOHMEM_APP_RUNNER=$EHTEST_PRINT_ARGS
    export ECOHMEM_APP_RUNNER_FLAGS="some flags"
    run --separate-stderr "$EHTEST_SCRIPT" --runner-flags "other FLAGS"
    expected=$(cat <<END
argc = 6
0: |$EHTEST_PRINT_ARGS|
1: |other|
2: |FLAGS|
3: |python3|
4: |-c|
5: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flag --runner-flags= overrides env var" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    export ECOHMEM_APP_RUNNER=$EHTEST_PRINT_ARGS
    export ECOHMEM_APP_RUNNER_FLAGS="some flags"
    run --separate-stderr "$EHTEST_SCRIPT" --runner-flags="other FLAGS"
    expected=$(cat <<END
argc = 6
0: |$EHTEST_PRINT_ARGS|
1: |other|
2: |FLAGS|
3: |python3|
4: |-c|
5: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "mpirun from env vars" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    export ECOHMEM_MPIRUN=$EHTEST_PRINT_ARGS
    export ECOHMEM_IS_MPI_APP=1
    run --separate-stderr "$EHTEST_SCRIPT"
    expected=$(cat <<END
argc = 4
0: |$EHTEST_PRINT_ARGS|
1: |python3|
2: |-c|
3: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "mpirun with flags from env vars" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    export ECOHMEM_MPIRUN=$EHTEST_PRINT_ARGS
    export ECOHMEM_MPIRUN_FLAGS="some flags"
    export ECOHMEM_IS_MPI_APP=1
    run --separate-stderr "$EHTEST_SCRIPT"
    expected=$(cat <<END
argc = 6
0: |$EHTEST_PRINT_ARGS|
1: |some|
2: |flags|
3: |python3|
4: |-c|
5: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flag --mpirun-flags overrides env var" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    export ECOHMEM_MPIRUN=$EHTEST_PRINT_ARGS
    export ECOHMEM_MPIRUN_FLAGS="some flags"
    export ECOHMEM_IS_MPI_APP=1
    run --separate-stderr "$EHTEST_SCRIPT" --mpirun-flags "other FLAGS"
    expected=$(cat <<END
argc = 6
0: |$EHTEST_PRINT_ARGS|
1: |other|
2: |FLAGS|
3: |python3|
4: |-c|
5: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flag --mpirun-flags= overrides env var" {
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    export ECOHMEM_MPIRUN=$EHTEST_PRINT_ARGS
    export ECOHMEM_MPIRUN_FLAGS="some flags"
    export ECOHMEM_IS_MPI_APP=1
    run --separate-stderr "$EHTEST_SCRIPT" --mpirun-flags="other FLAGS"
    expected=$(cat <<END
argc = 6
0: |$EHTEST_PRINT_ARGS|
1: |other|
2: |FLAGS|
3: |python3|
4: |-c|
5: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flexmalloc with app with args from env vars" {
    export ECOHMEM_LOAD_FLEXMALLOC_SCRIPT=$EHTEST_PRINT_ARGS
    export ECOHMEM_FLEXMALLOC_MEM_CONFIG=fmconfig
    export ECOHMEM_ADVISOR_OUTPUT_FILE="advisor out"
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    run --separate-stderr "$EHTEST_SCRIPT" --flexmalloc
    expected=$(cat <<END
argc = 6
0: |$EHTEST_PRINT_ARGS|
1: |fmconfig|
2: |advisor out|
3: |python3|
4: |-c|
5: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flag --obj-file overrides env var" {
    export ECOHMEM_LOAD_FLEXMALLOC_SCRIPT=$EHTEST_PRINT_ARGS
    export ECOHMEM_FLEXMALLOC_MEM_CONFIG=fmconfig
    export ECOHMEM_ADVISOR_OUTPUT_FILE="advisor out"
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    run --separate-stderr "$EHTEST_SCRIPT" --flexmalloc --obj-file "another advisorout"
    expected=$(cat <<END
argc = 6
0: |$EHTEST_PRINT_ARGS|
1: |fmconfig|
2: |another advisorout|
3: |python3|
4: |-c|
5: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flag --obj-file= overrides env var" {
    export ECOHMEM_LOAD_FLEXMALLOC_SCRIPT=$EHTEST_PRINT_ARGS
    export ECOHMEM_FLEXMALLOC_MEM_CONFIG=fmconfig
    export ECOHMEM_ADVISOR_OUTPUT_FILE="advisor out"
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    run --separate-stderr "$EHTEST_SCRIPT" --flexmalloc --obj-file="another advisorout"
    expected=$(cat <<END
argc = 6
0: |$EHTEST_PRINT_ARGS|
1: |fmconfig|
2: |another advisorout|
3: |python3|
4: |-c|
5: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flag --flexmalloc-config overrides env var" {
    export ECOHMEM_LOAD_FLEXMALLOC_SCRIPT=$EHTEST_PRINT_ARGS
    export ECOHMEM_FLEXMALLOC_MEM_CONFIG=fmconfig
    export ECOHMEM_ADVISOR_OUTPUT_FILE="advisor out"
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    run --separate-stderr "$EHTEST_SCRIPT" --flexmalloc --flexmalloc-config "another config"
    expected=$(cat <<END
argc = 6
0: |$EHTEST_PRINT_ARGS|
1: |another config|
2: |advisor out|
3: |python3|
4: |-c|
5: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flag --flexmalloc-config= overrides env var" {
    export ECOHMEM_LOAD_FLEXMALLOC_SCRIPT=$EHTEST_PRINT_ARGS
    export ECOHMEM_FLEXMALLOC_MEM_CONFIG=fmconfig
    export ECOHMEM_ADVISOR_OUTPUT_FILE="advisor out"
    export ECOHMEM_APP_BINARY=python3
    export ECOHMEM_APP_ARGS="-c 'print(\"Hello\")'"
    run --separate-stderr "$EHTEST_SCRIPT" --flexmalloc --flexmalloc-config="another config"
    expected=$(cat <<END
argc = 6
0: |$EHTEST_PRINT_ARGS|
1: |another config|
2: |advisor out|
3: |python3|
4: |-c|
5: |print("Hello")|
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}

@test "flexmalloc env vars are exported" {
    export ECOHMEM_LOAD_FLEXMALLOC_SCRIPT=python3
    # (ab)use the two params to pass the command to python
    export ECOHMEM_FLEXMALLOC_MEM_CONFIG=-c
    export ECOHMEM_ADVISOR_OUTPUT_FILE="import os;env=os.environ;print(env['FLEXMALLOC_HOME']);print(env['FLEXMALLOC_FALLBACK_ALLOCATOR']);print(env['FLEXMALLOC_MINSIZE_THRESHOLD']);print(env['FLEXMALLOC_MINSIZE_THRESHOLD_ALLOCATOR'])"
    export ECOHMEM_APP_BINARY=ls
    export ECOHMEM_FLEXMALLOC_HOME="fm home"
    export ECOHMEM_FLEXMALLOC_FALLBACK_ALLOCATOR="fallback allocator"
    export ECOHMEM_FLEXMALLOC_MINSIZE_THRESHOLD="12321"
    export ECOHMEM_FLEXMALLOC_MINSIZE_THRESHOLD_ALLOCATOR="min alloca"
    run --separate-stderr "$EHTEST_SCRIPT" --flexmalloc
    expected=$(cat <<END
fm home
fallback allocator
12321
min alloca
END
    )
    [ "$output" = "$expected" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
}


