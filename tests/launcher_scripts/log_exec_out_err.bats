#!/usr/bin/env bats

bats_require_minimum_version 1.5.0

setup() {
    export ECOHMEM_HOME=../
    export ECOHMEM_PYTHON=python3
    source "$ECOHMEM_HOME/scripts/utils.src"

    EHTEST_OUTFILE=$(mktemp)
    EHTEST_ERRFILE=$(mktemp)
}

teardown() {
    rm "$EHTEST_OUTFILE"
    rm "$EHTEST_ERRFILE"
}

@test "keeps exit code" {
    run log_exec_out_err "$ECOHMEM_PYTHON" -c 'import sys; sys.exit(0)' /dev/null /dev/null
    [ "$status" -eq 0 ]
    run log_exec_out_err "$ECOHMEM_PYTHON" -c 'import sys; sys.exit(3)' /dev/null /dev/null
    [ "$status" -eq 3 ]
}

@test "redirects stdout and stderr" {
    unset ECOHMEM_PRINT_CMDS
    run log_exec_out_err "$ECOHMEM_PYTHON" -c 'import sys;print("Hello");print("World",file=sys.stderr)' "$EHTEST_OUTFILE" "$EHTEST_ERRFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "Hello" ]
    err=$(cat "$EHTEST_ERRFILE")
    [ "$err" = "World" ]
}

@test "complains if too few args" {
    run --separate-stderr log_exec_out_err
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: log_exec_out_err expects 3 or more parameters" ]
    [ "$status" -eq 1 ]
    run --separate-stderr log_exec_out_err one
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: log_exec_out_err expects 3 or more parameters" ]
    [ "$status" -eq 1 ]
    run --separate-stderr log_exec_out_err one two
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: log_exec_out_err expects 3 or more parameters" ]
    [ "$status" -eq 1 ]
}

@test "no print when unset" {
    unset ECOHMEM_PRINT_CMDS
    run log_exec_out_err "$ECOHMEM_PYTHON" -c 'import sys;print("Hello");print("World",file=sys.stderr)' "$EHTEST_OUTFILE" "$EHTEST_ERRFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "Hello" ]
    err=$(cat "$EHTEST_ERRFILE")
    [ "$err" = "World" ]
}

@test "no print when 0" {
    export ECOHMEM_PRINT_CMDS=0
    run log_exec_out_err echo Hello "$EHTEST_OUTFILE" "$EHTEST_ERRFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "Hello" ]
    err=$(cat "$EHTEST_ERRFILE")
    [ "$err" = "" ]
}

@test "prints when 1" {
    export ECOHMEM_PRINT_CMDS=1
    run log_exec_out_err "$ECOHMEM_PYTHON" -c 'import sys;print("Hello");print("World",file=sys.stderr)' "$EHTEST_OUTFILE" "$EHTEST_ERRFILE"
    [ "$output" = "|EH| Executing: $ECOHMEM_PYTHON -c import sys;print(\"Hello\");print(\"World\",file=sys.stderr) > $EHTEST_OUTFILE 2> $EHTEST_ERRFILE" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "Hello" ]
    err=$(cat "$EHTEST_ERRFILE")
    [ "$err" = "World" ]
}

@test "simple args" {
    run log_exec_out_err "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first second third "$EHTEST_OUTFILE" "$EHTEST_ERRFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "first|second|third" ]
    err=$(cat "$EHTEST_ERRFILE")
    [ "$err" = "" ]
}

@test "double quoted space arg" {
    run log_exec_out_err "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first "sec ond" third "$EHTEST_OUTFILE" "$EHTEST_ERRFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "first|sec ond|third" ]
    err=$(cat "$EHTEST_ERRFILE")
    [ "$err" = "" ]
}

@test "single quoted space arg" {
    run log_exec_out_err "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first sec' 'ond third "$EHTEST_OUTFILE" "$EHTEST_ERRFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "first|sec ond|third" ]
    err=$(cat "$EHTEST_ERRFILE")
    [ "$err" = "" ]
}

@test "escaped space arg" {
    run log_exec_out_err "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first sec\ ond third "$EHTEST_OUTFILE" "$EHTEST_ERRFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "first|sec ond|third" ]
    err=$(cat "$EHTEST_ERRFILE")
    [ "$err" = "" ]
}

@test "newline in arg" {
    run log_exec_out_err "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first sec$'\n'ond third "$EHTEST_OUTFILE" "$EHTEST_ERRFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = $'first|sec\nond|third' ]
    err=$(cat "$EHTEST_ERRFILE")
    [ "$err" = "" ]
}


