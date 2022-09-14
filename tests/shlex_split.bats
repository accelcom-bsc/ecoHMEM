#!/usr/bin/env bats

bats_require_minimum_version 1.5.0

setup() {
    export ECOHMEM_HOME=../
    export ECOHMEM_PYTHON=python3
    source "$ECOHMEM_HOME/scripts/utils.src"
}

@test "complains if wrong number of args" {
    run --separate-stderr shlex_split
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: shlex_split expects 2 parameters, the string to split and the output array's name" ]
    [ "$status" -eq 1 ]
    run --separate-stderr shlex_split one
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: shlex_split expects 2 parameters, the string to split and the output array's name" ]
    [ "$status" -eq 1 ]
    run --separate-stderr shlex_split one two three
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: shlex_split expects 2 parameters, the string to split and the output array's name" ]
    [ "$status" -eq 1 ]
}

@test "simple args" {
    local urr=()
    shlex_split "first second third" urr

    [ "${#urr[@]}" -eq 3 ]
    [ "${urr[0]}" = "first" ]
    [ "${urr[1]}" = "second" ]
    [ "${urr[2]}" = "third" ]
}

@test "double quoted space arg" {
    local urr=()
    shlex_split "first \"sec ond\" third" urr

    [ "${#urr[@]}" -eq 3 ]
    [ "${urr[0]}" = "first" ]
    [ "${urr[1]}" = "sec ond" ]
    [ "${urr[2]}" = "third" ]
}

@test "single quoted space arg" {
    local arr=()
    shlex_split "first 'sec ond' third" arr

    [ "${#arr[@]}" -eq 3 ]
    [ "${arr[0]}" = "first" ]
    [ "${arr[1]}" = "sec ond" ]
    [ "${arr[2]}" = "third" ]
}

@test "escaped space arg" {
    local arr=()
    shlex_split "first sec\\ ond third" arr

    [ "${#arr[@]}" -eq 3 ]
    [ "${arr[0]}" = "first" ]
    [ "${arr[1]}" = "sec ond" ]
    [ "${arr[2]}" = "third" ]
}

@test "double quoted newline in arg" {
    local arr=()
    shlex_split $'first "sec\nond" third' arr

    [ "${#arr[@]}" -eq 3 ]
    [ "${arr[0]}" = "first" ]
    [ "${arr[1]}" = $'sec\nond' ]
    [ "${arr[2]}" = "third" ]
}

@test "single quoted newline in arg" {
    local arr=()
    shlex_split $'first \'sec\nond\' third' arr

    [ "${#arr[@]}" -eq 3 ]
    [ "${arr[0]}" = "first" ]
    [ "${arr[1]}" = $'sec\nond' ]
    [ "${arr[2]}" = "third" ]
}

@test "escaped newline in arg" {
    local arr=()
    shlex_split $'first sec\\\nond third' arr

    [ "${#arr[@]}" -eq 3 ]
    [ "${arr[0]}" = "first" ]
    [ "${arr[1]}" = $'sec\nond' ]
    [ "${arr[2]}" = "third" ]
}

@test "single space is no args" {
    local urr=()
    shlex_split " " urr

    [ "${#urr[@]}" -eq 0 ]
}

@test "escaped space is one arg" {
    local urr=()
    shlex_split "\ " urr

    [ "${#urr[@]}" -eq 1 ]
}

@test "two spaces is no args" {
    local urr=()
    shlex_split "  " urr

    [ "${#urr[@]}" -eq 0 ]
}
