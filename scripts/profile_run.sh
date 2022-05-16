#!/bin/bash -e

if [[ -z $ECOHMEM_HOME ]]; then
    echo "Error: ECOHMEM_HOME is not set, maybe you forgot to source the config file?"
    exit 1
fi

source "$ECOHMEM_HOME/scripts/utils.src"

while [[ $# -gt 0 ]]; do
  arg="$1"
  case $arg in
    --trace-name)
      arg_trace_name="$2"
      shift
      shift
      ;;
    --trace-name=*)
      arg_trace_name="${key#*=}"
      shift
      ;;
    --trace-type)
      arg_trace_type="$2"
      shift
      shift
      ;;
    --trace-type=*)
      arg_trace_type="${key#*=}"
      shift
      ;;
    --output-dir)
      arg_output_dir="$2"
      shift
      shift
      ;;
    --output-dir=*)
      arg_output_dir="${key#*=}"
      shift
      ;;
    --app-args)
      arg_app_args="$2"
      shift
      shift
      ;;
    --app-args=*)
      arg_app_args="${key#*=}"
      shift
      ;;
    --app-runner)
      arg_app_runner="$2"
      shift
      shift
      ;;
    --app-runner=*)
      arg_app_runner="${key#*=}"
      shift
      ;;
    --runner-flags)
      arg_runner_flags="$2"
      shift
      shift
      ;;
    --runner-flags=*)
      arg_runner_flags="${key#*=}"
      shift
      ;;
    --mpirun-flags)
      arg_mpirun_flags="$2"
      shift
      shift
      ;;
    --mpirun-flags=*)
      arg_mpirun_flags="${key#*=}"
      shift
      ;;
    --mpi2prv-flags)
      arg_mpi2prv_flags="$2"
      shift
      shift
      ;;
    --mpi2prv-flags=*)
      arg_mpi2prv_flags="${key#*=}"
      shift
      ;;
    --force)
      arg_force=y
      shift
      ;;
    --force-cfgs)
      arg_force_cfgs=y
      shift
      ;;
    --force-postprocess)
      arg_force_postprocess=y
      shift
      ;;
    --ignore-app-exitcode)
      arg_ignore_app_exitcode=y
      shift
      ;;
    *)
      ercho "Error: Unknown argument $arg"
      exit 1
      ;;
  esac
done

force=${arg_force:-n}
force_cfgs=${arg_force_cfgs:-n}
force_postprocess=${arg_force_postprocess:-n}
ignore_app_exitcode=${arg_ignore_app_exitcode:-n}

output_dir=${arg_output_dir:-$ECOHMEM_TRACE_OUTPUT_DIR}
trace_name=${arg_trace_name:-$ECOHMEM_TRACE_NAME}
trace_type=${arg_trace_type:-$ECOHMEM_TRACE_TYPE}

paramedir_configs_dir="$output_dir/configs"
postprocess_data_dir="$output_dir/postprocessed_data"

trace_file="$output_dir/$trace_name.prv"
trace_pcf_file="$output_dir/$trace_name.pcf"

app_args_str=${arg_app_args:-$ECOHMEM_APP_ARGS}
mpirun_flags_str=${arg_mpirun_flags:-$ECOHMEM_MPIRUN_FLAGS}
app_runner=${arg_app_runner:-$ECOHMEM_APP_RUNNER}
app_runner_flags_str=${arg_app_runner_flags:-$ECOHMEM_APP_RUNNER_FLAGS}
mpi2prv_extra_flags_str=${arg_mpi2prv_flags:-$ECOHMEM_MPI2PRV_EXTRA_FLAGS}

if [[ -e $output_dir ]]; then
    if [[ ! -d $output_dir ]]; then
        ercho "Error: the path '$output_dir' already exists but is not a directory."
        exit 1
    fi
else
    echo "Info: creating output directory '$output_dir'"
    mkdir "$output_dir"
fi

###
# Run app with profiling library
#
do_run=y
if [[ $force == "n" ]]; then
    if [[ -f $trace_file ]]; then
        do_run=n
        echo "Info: trace file '$trace_file' already exists, skipping profiling run (use --force to rerun it)"
    elif [[ -f "$output_dir/TRACE.mpits" ]]; then
        do_run=n
        echo "Info: intermediate trace file '$output_dir/TRACE.mpits' already exists, skipping profiling run (use --force to force a rerun)"
    fi
fi

if [[ $do_run == "y" ]]; then    
    app_out_file=$output_dir/profile.out
    app_err_file=$output_dir/profile.err

    # parse quotes and backslashes in arg/flag lists
    app_runner_flags=()
    shlex_split "$app_runner_flags_str" app_runner_flags
    mpirun_flags=()
    shlex_split "$mpirun_flags_str" mpirun_flags
    app_args=()
    shlex_split "$app_args_str" app_args

    cmd=()
    if [[ ! -z $app_runner ]]; then
        cmd+=("$app_runner" "${app_runner_flags[@]}")
    fi

    if [[ $ECOHMEM_IS_MPI_APP -eq 1 ]]; then
        cmd+=("$ECOHMEM_MPIRUN" "${mpirun_flags[@]}")
    fi

    cmd+=("$ECOHMEM_LOAD_EXTRAE_SCRIPT" "$output_dir" "$ECOHMEM_EXTRAE_XML"  "$ECOHMEM_APP_BINARY" "${app_args[@]}")
    
    set +e
    "${cmd[@]}" > "$app_out_file" 2> "$app_err_file"
    retcode=$?
    set -e

    if [[ $retcode -ne 0 ]]; then
        if [[ $ignore_app_exitcode == "y" ]]; then
            echo "Warn: ignoring non-zero application exit code: $retcode"
        else
            ercho "Error: the application execution failed (exit code $retcode), check '$app_err_file' and '$app_out_file' for more details"
            exit 1
        fi
    fi

    # FIXME workaround for extrae output dir, the envar EXTRAE_FINAL_DIR doesn't seem to work
    set +e
    mv *.prv *.pcf *.row set-0 TRACE.mpits TRACE.sym TRACE.spawn "$output_dir"
    set -e
fi

##
# Merge traces
#
do_merge=n
if [[ ! -e $trace_file ]]; then
    do_merge=y
    echo "Info: merging intermediate Extrae trace to generate '$trace_file'"
fi

if [[ $do_merge == "y" ]]; then
    echo "Info: merging intermediate profiling trace"
    if [[ -z $ECOHMEM_MPI2PRV ]]; then
        ercho "Error: ECOHMEM_MPI2PRV is unset and is required to merge the intermediate Extrae trace."
        exit 1
    fi
    
    # parse quotes and backslashes
    mpi2prv_extra_flags=()
    shlex_split "$mpi2prv_extra_flags_str" mpi2prv_extra_flags

    "$ECOHMEM_MPI2PRV" -f "$output_dir/TRACE.mpits" -o "$trace_file" "${mpi2prv_extra_flags[@]}"
fi

##
# Generate Paramedir config files
#
do_cfgs=y
if [[ -e $paramedir_configs_dir ]]; then
    if [[ -d $paramedir_configs_dir ]]; then
        if [[ $do_run == "n" && $force_cfgs == "n" ]]; then
            do_cfgs=n
            echo "Info: paramedir configs directory '$paramedir_configs_dir' already exists, skipping generation (use --force-cfgs to regenerate them)"
        fi
    else
        ercho "Error: the path '$paramedir_configs_dir' already exists but is not a directory."
        exit 1
    fi
else
    mkdir "$paramedir_configs_dir"
fi

if [[ $do_cfgs == "y" ]]; then
    echo "Info: generating paramedir config files"
    if [[ $trace_type == "loads" ]]; then
        "$ECOHMEM_PARAMEDIR_CFG_GEN" -f --ld "$trace_pcf_file" "$paramedir_configs_dir"
    elif [[ $trace_type == "loads_stores" ]]; then
        "$ECOHMEM_PARAMEDIR_CFG_GEN" -f --ldst "$trace_pcf_file" "$paramedir_configs_dir"
    else
        ercho "Error: unknown trace type: $trace_type"
        exit 1
    fi
fi

##
# Postprocess traces
#
do_postpo=y
if [[ -e $postprocess_data_dir ]]; then
    if [[ -d $postprocess_data_dir ]]; then
        if [[ $do_run == "n" && $force_postprocess == "n" ]]; then
            do_postpo=n
            echo "Info: postprocessed data directory '$postprocess_data_dir' already exists, skipping processing (use --force-postprocess to redo it)"
        fi
    else
        ercho "Error: the path '$postprocess_data_dir' already exists but is not a directory."
        exit 1
    fi
else
    mkdir "$postprocess_data_dir"
fi

if [[ $do_postpo == "y" ]]; then
    echo "Info: postprocessing profiling data"
    if [[ $trace_type == "loads" ]]; then
        "$ECOHMEM_PARAMEDIR" "$trace_file" "$paramedir_configs_dir/ld_load-miss.cfg" "$postprocess_data_dir/$trace_type.load_miss.csv"
        "$ECOHMEM_PARAMEDIR" "$trace_file" "$paramedir_configs_dir/ld_max-size.cfg"  "$postprocess_data_dir/$trace_type.sizes.csv"
        
        "$ECOHMEM_ALLOCSINFO" "$trace_file" > "$postprocess_data_dir/$trace_type.allocsinfo.json" 2> "$postprocess_data_dir/$trace_type.allocsinfo.err"
    elif [[ $trace_type == "loads_stores" ]]; then
        "$ECOHMEM_PARAMEDIR" "$trace_file" "$paramedir_configs_dir/ldst_load-miss.cfg"       "$postprocess_data_dir/$trace_type.load_miss.csv"
        "$ECOHMEM_PARAMEDIR" "$trace_file" "$paramedir_configs_dir/ldst_l1d-store-miss.cfg"  "$postprocess_data_dir/$trace_type.store_miss_L1.csv"
        "$ECOHMEM_PARAMEDIR" "$trace_file" "$paramedir_configs_dir/ldst_max-size.cfg"        "$postprocess_data_dir/$trace_type.sizes.csv"

        "$ECOHMEM_ALLOCSINFO" "$trace_file" > "$postprocess_data_dir/$trace_type.allocsinfo.json" 2> "$postprocess_data_dir/$trace_type.allocsinfo.err"
    else
        ercho "Error: unknown trace type: $trace_type"
        exit 1
    fi
fi



