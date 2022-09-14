#!/usr/bin/env bats

setup() {
#    load 'test_helper/bats-assert/load'

    export ECOHMEM_HOME=../
    export ECOHMEM_PYTHON=python3
    source "$ECOHMEM_HOME/scripts/utils.src"
}

@test "keeps exit code" {
    run log_exec "$ECOHMEM_PYTHON" -c 'import sys; sys.exit(0)'
    [ "$status" -eq 0 ]
    run log_exec "$ECOHMEM_PYTHON" -c 'import sys; sys.exit(3)'
    [ "$status" -eq 3 ]
}

@test "no print when unset" {
    unset ECOHMEM_PRINT_CMDS
    run log_exec "$ECOHMEM_PYTHON" -c 'print("Hello")'
    [ "$output" = "Hello" ]
    [ "$status" -eq 0 ]
}

@test "no print when 0" {
    export ECOHMEM_PRINT_CMDS=0
    run log_exec echo Hello
    [ "$output" = "Hello" ]
    [ "$status" -eq 0 ]
}

@test "prints when 1" {
    export ECOHMEM_PRINT_CMDS=1
    run log_exec "$ECOHMEM_PYTHON" -c 'print("Hello")'
    [ "$output" = '|EH| Executing: '"$ECOHMEM_PYTHON"$' -c print("Hello")\nHello' ]
    [ "$status" -eq 0 ]
}

@test "simple args" {
    run log_exec "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first second third
    [ "$output" = "first|second|third" ]
    [ "$status" -eq 0 ]
}

@test "double quoted space arg" {
    run log_exec "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first "sec ond" third
    [ "$output" = "first|sec ond|third" ]
    [ "$status" -eq 0 ]
}

@test "single quoted space arg" {
    run log_exec "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first sec' 'ond third
    [ "$output" = "first|sec ond|third" ]
    [ "$status" -eq 0 ]
}

@test "escaped space arg" {
    run log_exec "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first sec\ ond third
    [ "$output" = "first|sec ond|third" ]
    [ "$status" -eq 0 ]
}

@test "newline in arg" {
    run log_exec "$ECOHMEM_PYTHON" -c 'import sys; print("|".join(sys.argv[1:]))' first sec$'\n'ond third
    [ "$output" = $'first|sec\nond|third' ]
    [ "$status" -eq 0 ]
}

