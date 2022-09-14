#!/usr/bin/env bats

bats_require_minimum_version 1.5.0

setup() {
    export ECOHMEM_HOME=../
    export ECOHMEM_PYTHON=python3
    source "$ECOHMEM_HOME/scripts/utils.src"

    EHTEST_OUTFILE=$(mktemp)
}

teardown() {
    rm "$EHTEST_OUTFILE"
}

@test "keeps exit code" {
    run log_exec_out "$ECOHMEM_PYTHON" -c 'import sys; sys.exit(0)' /dev/null
    [ "$status" -eq 0 ]
    run log_exec_out "$ECOHMEM_PYTHON" -c 'import sys; sys.exit(3)' /dev/null
    [ "$status" -eq 3 ]
}

@test "redirects stdout" {
    unset ECOHMEM_PRINT_CMDS
    run log_exec_out "$ECOHMEM_PYTHON" -c 'print("Hello")' "$EHTEST_OUTFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "Hello" ]
}

@test "complains if too few args" {
    run --separate-stderr log_exec_out
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: log_exec_out expects 2 or more parameters" ]
    [ "$status" -eq 1 ]
    run --separate-stderr log_exec_out one
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: log_exec_out expects 2 or more parameters" ]
    [ "$status" -eq 1 ]
}

@test "no print when unset" {
    unset ECOHMEM_PRINT_CMDS
    run log_exec_out "$ECOHMEM_PYTHON" -c 'print("Hello")' "$EHTEST_OUTFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "Hello" ]
}

@test "no print when 0" {
    export ECOHMEM_PRINT_CMDS=0
    run log_exec_out echo Hello "$EHTEST_OUTFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "Hello" ]
}

@test "prints when 1" {
    export ECOHMEM_PRINT_CMDS=1
    run log_exec_out "$ECOHMEM_PYTHON" -c 'print("Hello")' "$EHTEST_OUTFILE"
    [ "$output" = "|EH| Executing: $ECOHMEM_PYTHON -c print(\"Hello\") > $EHTEST_OUTFILE" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "Hello" ]
}

@test "simple args" {
    run log_exec_out "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first second third "$EHTEST_OUTFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "first|second|third" ]
}

@test "double quoted space arg" {
    run log_exec_out "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first "sec ond" third "$EHTEST_OUTFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "first|sec ond|third" ]
}

@test "single quoted space arg" {
    run log_exec_out "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first sec' 'ond third "$EHTEST_OUTFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "first|sec ond|third" ]
}

@test "escaped space arg" {
    run log_exec_out "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first sec\ ond third "$EHTEST_OUTFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "first|sec ond|third" ]
}

@test "newline in arg" {
    run log_exec_out "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first sec$'\n'ond third "$EHTEST_OUTFILE"
    [ "$output" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = $'first|sec\nond|third' ]
}


