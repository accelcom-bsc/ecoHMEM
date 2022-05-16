#!/bin/bash -e

if [[ -z $ECOHMEM_HOME ]]; then
    echo "Error: ECOHMEM_HOME is not set, maybe you forgot to source the config file?"
    exit 1
fi

source "$ECOHMEM_HOME/scripts/utils.src"

arg_advisor_extra_args=()

while [[ $# -gt 0 ]]; do
  arg="$1"
  case $arg in
    --trace-type)
      arg_trace_type="$2"
      shift
      shift
      ;;
    --trace-type=*)
      arg_trace_type="${key#*=}"
      shift
      ;;
    --output-file)
      arg_output_file="$2"
      shift
      shift
      ;;
    --output-file=*)
      arg_output_file="${key#*=}"
      shift
      ;;
    --input-dir)
      arg_input_dir="$2"
      shift
      shift
      ;;
    --input-dir=*)
      arg_input_dir="${key#*=}"
      shift
      ;;
    --mem-config)
      arg_mem_config="$2"
      shift
      shift
      ;;
    --mem-config=*)
      arg_mem_config="${key#*=}"
      shift
      ;;
    --extra-arg)
      arg_advisor_extra_args+=("$2")
      shift
      shift
      ;;
    --extra-arg=*)
      arg_advisor_extra_args+=("${key#*=}")
      shift
      ;;
    --force)
      arg_force=y
      shift
      ;;
    *)
      ercho "Error: Unknown argument $arg"
      exit 1
      ;;
  esac
done

force=${arg_force:-n}

trace_type=${arg_trace_type:-$ECOHMEM_TRACE_TYPE}
mem_config=${arg_mem_config:-$ECOHMEM_ADVISOR_MEM_CONFIG}
output_file=${arg_output_file:-$ECOHMEM_ADVISOR_OUTPUT_FILE}

input_dir=${arg_input_dir:-$ECOHMEM_TRACE_OUTPUT_DIR}
postprocess_data_dir="$input_dir/postprocessed_data"


do_it=y
if [[ -e $output_file ]]; then
    if [[ -f $output_file ]]; then
        if [[ $force == "n" ]]; then
            do_it=n
            echo "Info: output file '$output_file' already exists, skipping processing (use --force to redo it)"
        fi
    else
        ercho "Error: the path '$output_file' already exists but is not a regular file."
        exit 1
    fi
fi

if [[ $do_it == "y" ]]; then
    if [[ $trace_type == "loads" ]]; then
        stores_arg=()
    elif [[ $trace_type == "loads_stores" ]]; then
        stores_arg=("--stores" "$postprocess_data_dir/$trace_type.store_miss_L1.csv")
    else
        ercho "Error: unknown trace type: $trace_type"
        exit 1
    fi

    # parse quotes and backslashes
    advisor_extra_args=()
    shlex_split "$ECOHMEM_ADVISOR_EXTRA_ARGS" advisor_extra_args

    "$ECOHMEM_PYTHON" "$ECOHMEM_ADVISOR" "${advisor_extra_args[@]}" "${arg_advisor_extra_args[@]}" --mem-config "$mem_config" --sizes "$postprocess_data_dir/$trace_type.sizes.csv" --loads "$postprocess_data_dir/$trace_type.load_miss.csv" "${stores_arg[@]}" --allocs-info "$postprocess_data_dir/$trace_type.allocsinfo.json" > $output_file
fi
