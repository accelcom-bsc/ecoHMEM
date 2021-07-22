#!/bin/bash

source "$HA_HOME/scripts/utils.src"

if [[ $# -lt 2 ]]; then
    ercho "Error: expected at least 2 params, output dir and xml config file path"
    exit 1
fi

out_dir=$1
extrae_xml=$2
shift
shift

if [[ -z $HA_EXTRAE_LIB ]]; then
    if [[ -z $HA_EXTRAE_HOME ]]; then
        ercho "Error: HA_EXTRAE_LIB and HA_EXTRAE_HOME are both empty or unset."
        exit 1
    fi
    if [[ -z $HA_IS_MPI_APP || -z $HA_IS_OMP_APP || -z $HA_IS_PTHREAD_APP || -z $HA_IS_FORTRAN_APP ]]; then
        ercho "Error: HA_IS_MPI_APP, HA_IS_OMP_APP, HA_IS_PTHREAD_APP and/or HA_IS_FORTRAN_APP are empty or unset. Set them or use HA_EXTRAE_LIB to provide the Extrae lib path."
        exit 1
    fi

    # elif order matters
    if [[ $HA_IS_MPI_APP -eq 1 && $HA_IS_OMP_APP -eq 1 ]]; then
        lib_path=$HA_EXTRAE_HOME/lib/libompitrace.so
    elif [[ $HA_IS_MPI_APP -eq 1 && $HA_IS_PTHREAD_APP -eq 1 ]]; then
        lib_path=$HA_EXTRAE_HOME/lib/libptmpitrace.so
    elif [[ $HA_IS_MPI_APP -eq 1 ]]; then
        lib_path=$HA_EXTRAE_HOME/lib/libmpitrace.so
    elif [[ $HA_IS_OMP_APP -eq 1 ]]; then
        lib_path=$HA_EXTRAE_HOME/lib/libomptrace.so
    elif [[ $HA_IS_PTHREAD_APP -eq 1 ]]; then
        lib_path=$HA_EXTRAE_HOME/lib/libpttrace.so
    else
        lib_path=$HA_EXTRAE_HOME/lib/libseqtrace.so
    fi

    if [[ $HA_IS_FORTRAN_APP -eq 1 ]]; then
        lib_path=${lib_path}f
    fi
else
    lib_path=$HA_EXTRAE_LIB
fi

#echo "Using Extrae lib: $lib_path"
#echo "out_dir $out_dir"

EXTRAE_FINAL_DIR=$out_dir EXTRAE_CONFIG_FILE=$extrae_xml LD_PRELOAD=$lib_path "${@}"



