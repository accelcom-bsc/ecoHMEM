#!/usr/bin/env bats

bats_require_minimum_version 1.5.0

setup() {
    export ECOHMEM_HOME=../
    export EHTEST_SCRIPT="$ECOHMEM_HOME/scripts/generate_distribution.sh"
    export EHTEST_PRINT_ARGS="$ECOHMEM_HOME/tests/print_args"
}


@test "complains if undefined output path" {
    export ECOHMEM_ADVISOR_OUTPUT_FILE=""
    export ECOHMEM_TRACE_TYPE=loads
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: the output file path is empty, specify it using the corresponding env var or the --output-file flag." ]
    [ "$status" -eq 1 ]
}

@test "nop if already existing output" {
    EHTEST_OUTFILE=$(mktemp)
    echo 'some text' > "$EHTEST_OUTFILE"
    export ECOHMEM_ADVISOR_OUTPUT_FILE="$EHTEST_OUTFILE"
    export ECOHMEM_TRACE_TYPE=loads
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = "|EH| Info: output file '$EHTEST_OUTFILE' already exists, skipping processing (use --force to redo it)" ]
    [ "$stderr" = "" ]
    [ "$status" -eq 0 ]
    out=$(cat "$EHTEST_OUTFILE")
    [ "$out" = "some text" ]
    rm "$EHTEST_OUTFILE"
}

@test "nop if already existing output is not a file" {
    EHTEST_OUTDIR=$(mktemp -d)
    export ECOHMEM_ADVISOR_OUTPUT_FILE="$EHTEST_OUTDIR"
    export ECOHMEM_TRACE_TYPE=loads
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: the path '$EHTEST_OUTDIR' already exists but is not a regular file." ]
    [ "$status" -eq 1 ]
    rmdir "$EHTEST_OUTDIR"
}

@test "complains if undefined input dir" {
    export ECOHMEM_ADVISOR_OUTPUT_FILE="somename"
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: the input directory path is empty, specify it using the corresponding env var or the --input-dir flag." ]
    [ "$status" -eq 1 ]
}

@test "complains if input dir doesn't exist" {
    export ECOHMEM_TRACE_OUTPUT_DIR="some dir"
    export ECOHMEM_ADVISOR_OUTPUT_FILE="somename"
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: the input directory path 'some dir' doesn't exist or is not a directory." ]
    [ "$status" -eq 1 ]
}

@test "complains if input dir is not a directory" {
    EHTEST_OUTFILE=$(mktemp)
    export ECOHMEM_TRACE_OUTPUT_DIR="$EHTEST_OUTFILE"
    export ECOHMEM_ADVISOR_OUTPUT_FILE="somename"
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: the input directory path '$EHTEST_OUTFILE' doesn't exist or is not a directory." ]
    [ "$status" -eq 1 ]
    rm "$EHTEST_OUTFILE"
}

@test "complains if postprocessed data subdir doesn't exist" {
    EHTEST_INDIR=$(mktemp -d)
    export ECOHMEM_TRACE_OUTPUT_DIR="$EHTEST_INDIR"
    export ECOHMEM_ADVISOR_OUTPUT_FILE="somename"
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: the postprocessed data subdirectory '$EHTEST_INDIR/postprocessed_data' doesn't exist or is not a directory." ]
    [ "$status" -eq 1 ]
    rmdir "$EHTEST_INDIR"
}

@test "complains if postprocessed data subdir is not a directory" {
    EHTEST_INDIR=$(mktemp -d)
    touch "$EHTEST_INDIR/postprocessed_data"
    export ECOHMEM_TRACE_OUTPUT_DIR="$EHTEST_INDIR"
    export ECOHMEM_ADVISOR_OUTPUT_FILE="somename"
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: the postprocessed data subdirectory '$EHTEST_INDIR/postprocessed_data' doesn't exist or is not a directory." ]
    [ "$status" -eq 1 ]
    rm "$EHTEST_INDIR/postprocessed_data"
    rmdir "$EHTEST_INDIR"
}

@test "complains if trace type is undefined" {
    EHTEST_INDIR=$(mktemp -d)
    mkdir "$EHTEST_INDIR/postprocessed_data"
    export ECOHMEM_TRACE_OUTPUT_DIR="$EHTEST_INDIR"
    export ECOHMEM_ADVISOR_OUTPUT_FILE="somename"
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: unknown trace type:" ]
    [ "$status" -eq 1 ]
    rmdir "$EHTEST_INDIR/postprocessed_data" "$EHTEST_INDIR"
}

@test "complains if trace type is invalid" {
    EHTEST_INDIR=$(mktemp -d)
    mkdir "$EHTEST_INDIR/postprocessed_data"
    export ECOHMEM_TRACE_OUTPUT_DIR="$EHTEST_INDIR"
    export ECOHMEM_ADVISOR_OUTPUT_FILE="somename"
    export ECOHMEM_TRACE_TYPE="loadsblah"
    run --separate-stderr "$EHTEST_SCRIPT"
    [ "$output" = "" ]
    [ "$stderr" = "|EH| Error: unknown trace type: loadsblah" ]
    [ "$status" -eq 1 ]
    rmdir "$EHTEST_INDIR/postprocessed_data" "$EHTEST_INDIR"
}
