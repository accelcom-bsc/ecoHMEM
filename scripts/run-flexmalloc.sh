#!/bin/bash -e

if [[ -z $HA_HOME ]]; then
    echo "Error: HA_HOME is not set, maybe you forgot to source the config file?"
    exit 1
fi

source "$HA_HOME/scripts/utils.src"

while [[ $# -gt 0 ]]; do
  arg="$1"
  case $arg in
    --obj-file)
      arg_obj_file="$2"
      shift
      shift
      ;;
    --obj-file=*)
      arg_obj_file="${key#*=}"
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
    --flexmalloc-config)
      arg_fm_config="$2"
      shift
      shift
      ;;
    --flexmalloc-config=*)
      arg_fm_config="${key#*=}"
      shift
      ;;
    *)
      ercho "Error: Unknown argument $arg"
      exit 1
      ;;
  esac
done

#output_file=${arg_output_file:-$HA_ADVISOR_OUTPUT_FILE}

fm_mem_config=${arg_fm_config:-$HA_FLEXMALLOC_MEM_CONFIG}
obj_dist_file=${arg_obj_file:-$HA_ADVISOR_OUTPUT_FILE}

app_args_str=${arg_app_args:-$HA_APP_ARGS}
mpirun_flags_str=${arg_mpirun_flags:-$HA_MPIRUN_FLAGS}
app_runner=${arg_app_runner:-$HA_APP_RUNNER}
app_runner_flags_str=${arg_app_runner_flags:-$HA_APP_RUNNER_FLAGS}


#output_dir=
#app_out_file=$output_dir/run.out
#app_err_file=$output_dir/run.err

export FLEXMALLOC_HOME=$HA_FLEXMALLOC_HOME
export FLEXMALLOC_FALLBACK_ALLOCATOR=$HA_FLEXMALLOC_FALLBACK_ALLOCATOR
export FLEXMALLOC_MINSIZE_THRESHOLD=$HA_FLEXMALLOC_MINSIZE_THRESHOLD
export FLEXMALLOC_MINSIZE_THRESHOLD_ALLOCATOR=$HA_FLEXMALLOC_MINSIZE_THRESHOLD_ALLOCATOR

# parse quotes and backslashes in arg/flag lists
app_runner_flags=()
shlex_split "$app_runner_flags_str" app_runner_flags
mpirun_flags=()
shlex_split "$mpirun_flags_str" mpirun_flags
app_args=()
shlex_split "$app_args_str" app_args

if [[ $HA_IS_MPI_APP -eq 1 ]]; then
    "$app_runner" "${app_runner_flags[@]}"   "$HA_MPIRUN" "${mpirun_flags[@]}"   "$HA_LOAD_FLEXMALLOC_SCRIPT" "$fm_mem_config" "$obj_dist_file"   "$HA_APP_BINARY" "${app_args[@]}" #> "$app_out_file" 2> "$app_err_file"
else
    if [[ ! -z $arg_mpirun_flags ]]; then
        echo "Warn: ignoring --mpirun-flags because the app is not configured as an MPI app"
    fi

    "$app_runner" "${app_runner_flags[@]}"   "$HA_LOAD_FLEXMALLOC_SCRIPT" "$fm_mem_config" "$obj_dist_file"   "$HA_APP_BINARY" "${app_args[@]}" #> "$app_out_file" 2> "$app_err_file"
fi

