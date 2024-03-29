#!/bin/bash -e

if [[ -z $ECOHMEM_HOME ]]; then
    echo "|HE| Error: ECOHMEM_HOME is not set, maybe you forgot to source the config file?"
    exit 1
fi

this_dir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
source "$this_dir/utils.src"


while [[ $# -gt 0 ]]; do
  arg="$1"
  case $arg in
    --obj-file)
      arg_obj_file="$2"
      shift
      shift
      ;;
    --obj-file=*)
      arg_obj_file="${arg#*=}"
      shift
      ;;
    --app-args)
      arg_app_args="$2"
      shift
      shift
      ;;
    --app-args=*)
      arg_app_args="${arg#*=}"
      shift
      ;;
    --app-runner)
      arg_app_runner="$2"
      shift
      shift
      ;;
    --app-runner=*)
      arg_app_runner="${arg#*=}"
      shift
      ;;
    --runner-flags)
      arg_runner_flags="$2"
      shift
      shift
      ;;
    --runner-flags=*)
      arg_runner_flags="${arg#*=}"
      shift
      ;;
    --mpirun-flags)
      arg_mpirun_flags="$2"
      shift
      shift
      ;;
    --mpirun-flags=*)
      arg_mpirun_flags="${arg#*=}"
      shift
      ;;
    --flexmalloc-config)
      arg_fm_config="$2"
      shift
      shift
      ;;
    --flexmalloc-config=*)
      arg_fm_config="${arg#*=}"
      shift
      ;;
    --flexmalloc)
      arg_load_fm=1
      shift
      ;;
    *)
      err_msg "Error: Unknown argument $arg"
      exit 1
      ;;
  esac
done

fm_mem_config=${arg_fm_config:-$ECOHMEM_FLEXMALLOC_MEM_CONFIG}
obj_dist_file=${arg_obj_file:-$ECOHMEM_ADVISOR_OUTPUT_FILE}

app_args_str=${arg_app_args:-$ECOHMEM_APP_ARGS}
mpirun_flags_str=${arg_mpirun_flags:-$ECOHMEM_MPIRUN_FLAGS}
app_runner=${arg_app_runner:-$ECOHMEM_APP_RUNNER}
app_runner_flags_str=${arg_runner_flags:-$ECOHMEM_APP_RUNNER_FLAGS}


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
else
    if [[ ! -z $arg_mpirun_flags ]]; then
        msg "Warn: ignoring --mpirun-flags because the app is not configured as an MPI app"
    fi
fi

if [[ $arg_load_fm -eq 1 ]]; then
    export FLEXMALLOC_HOME=$ECOHMEM_FLEXMALLOC_HOME
    export FLEXMALLOC_FALLBACK_ALLOCATOR=$ECOHMEM_FLEXMALLOC_FALLBACK_ALLOCATOR
    export FLEXMALLOC_MINSIZE_THRESHOLD=$ECOHMEM_FLEXMALLOC_MINSIZE_THRESHOLD
    export FLEXMALLOC_MINSIZE_THRESHOLD_ALLOCATOR=$ECOHMEM_FLEXMALLOC_MINSIZE_THRESHOLD_ALLOCATOR

    cmd+=("$ECOHMEM_LOAD_FLEXMALLOC_SCRIPT" "$fm_mem_config" "$obj_dist_file")
fi

cmd+=("$ECOHMEM_APP_BINARY" "${app_args[@]}")

log_exec "${cmd[@]}"
