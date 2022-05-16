# ecoHMEM framework

## Prerequisites

The required external dependencies for the framework are:

- python3
- Extrae
- Paramedir
- Flexmalloc

_Extrae_ is a profiling library and _Paramedir_ a tool to postprocess the _Extrae_ trace data, both developed at BSC's performance tools group.
_Extrae_ is released only as source code, you will have to compile and install it on your system. _Paramedir_ is part of the _Paraver_ package, which is available as source code or precompiled binaries for several operating systems.
You can download the latest released version of them from the [group's website](https://tools.bsc.es/downloads). The minimum _Extrae_ version required to use this framework is 4.0.0.

The Flexmalloc library is developed by Intel. You can download it from its [Github repository](https://github.com/intel/flexmalloc).


## Workflow of the framework

The workflow consists of 3 main steps:
1. Run an instrumented execution of the target application to obtain profiling data
2. Generate a dynamic memory object distribution across the available memory tiers based on the profiling data
3. Run the application with the memory object distribution using the _Flexmalloc_ library 

None of this steps requires any change in the source code of the application. We provide a set of scripts to help handle the execution of each step, as described in the following subsections.


### 0. Setup configuration

Since there are several parameters and variables that are used in more than one of the steps, the scripts we provide are prepared to take get the information from a set of environment variables. To setup these variables, copy the file example\_conf.src to your working directory. This file consists of a list of export commands that setup the variables expected by the scripts, and you will have to load it using the _source_ command. The main variables you will have to modify are the ones describing the application and its arguments, but there are several variables to configure the tools and scripts of the framework.

- ECOHMEM\_HOME: the path of the directory containing the framework.
- ECOHMEM\_EXTRAE\_HOME: the path of the directory where you installed Extrae.
- ECOHMEM\_FLEXMALLOC\_HOME: the path of the directory where Flexmalloc is installed.
- ECOHMEM\_PYTHON: the path of the python interpreter.
- ECOHMEM\_ADVISOR: the path of the *hmem\_advisor* program.
- ECOHMEM\_ALLOCSINFO: the path of the *allocs\_info* program. It is used to extract data from the profiling trace.
- ECOHMEM\_PARAMEDIR\_CFG\_GEN: the path of the *cfg\_gen program*. It is used to generate Paramedir configuration files.
- ECOHMEM\_LOAD\_EXTRAE\_SCRIPT: the path of the helper script that will be used to load Extrae.
- ECOHMEM\_PARAMEDIR: the path of the *Paramedir* program. It is used to extract data from the profiling trace.
- ECOHMEM\_MPI2PRV: the path of the *mpi2prv* program. It converts the intermediate Extrae trace to the usual prv format, if it wasn't done by Extrae at the end of the profiling run.
- ECOHMEM\_MPI2PRV\_EXTRA\_FLAGS: extra flags that will be passed to mpi2prv.
- ECOHMEM\_EXTRAE\_LIB: path of the Extrae dynamic library to use for the profiling run. If this variable is empty, the framework will select a library automatically using variables that describe the application.
- ECOHMEM\_EXTRAE\_XML: path of the Extrae configuration file. There are a couple of example configuration files in the *extrae\_confs* directory.
- ECOHMEM\_TRACE\_TYPE: type of the data being collected. Currently it can be *loads* or *loads\_stores*. It has to match with the PEBS counters configured in the Extrae configuration file.
- ECOHMEM\_TRACE\_NAME: name of the prv trace, without the extension. If Extrae is configured to do the merge step, this should match the name used by Extrae. 
- ECOHMEM\_TRACE\_OUTPUT\_DIR: directory where the profiling trace and postprocessed data will be stored.
- ECOHMEM\_ADVISOR\_EXTRA\_ARGS: extra arguments that will be passed to hmem\_advisor.
- ECOHMEM\_ADVISOR\_MEM\_CONFIG: path to the hmem\_advisor configuration file. This file describes the available memory tiers, the size, the cost weight for loads, the cost weight for stores and the associated flexmalloc allocator.
- ECOHMEM\_ADVISOR\_OUTPUT\_FILE: path of the output file that will contain the memory object distribution.
- ECOHMEM\_FLEXMALLOC\_FALLBACK\_ALLOCATOR: name of the flexmalloc allocator that will be used when the rest of allocators are full.
- ECOHMEM\_FLEXMALLOC\_MINSIZE\_THRESHOLD\_ALLOCATOR: name of the flexmalloc allocator that will be used when the size of the allocation is lower than the threshold.
- ECOHMEM\_FLEXMALLOC\_MINSIZE\_THRESHOLD\: threshold (in number of bytes) for allocations to be considered by flexmalloc.
- ECOHMEM\_FLEXMALLOC\_MEM\_CONFIG: path of the Flexmalloc configuration file.
- ECOHMEM\_LOAD\_FLEXMALLOC\_SCRIPT: path of the script that will be used to load Flexmalloc.
- ECOHMEM\_APP\_BINARY: path of your application program.
- ECOHMEM\_APP\_ARGS: arguments that will be passed to your application.
- ECOHMEM\_IS\_FORTRAN\_APP: describes if your application is written in Fortran or not (set to 1 or 0, respectively).
- ECOHMEM\_IS\_MPI\_APP: set to 1 if your application uses MPI.
- ECOHMEM\_IS\_OMP\_APP: set to 1 if your application uses OpenMP.
- ECOHMEM\_IS\_PTHREAD\_APP: set to 1 if your application uses pthreads.
- ECOHMEM\_MPIRUN: path of the mpirun program. Only used for MPI applications.
- ECOHMEM\_MPIRUN\_FLAGS: arguments that will be passed to mpirun.
- ECOHMEM\_APP\_RUNNER: path of the tool that should be used to run your application (e.g. numactl).
- ECOHMEM\_APP\_RUNNER\_FLAGS: arguments for the runner tool.

To allow passing flags and arguments with whitespace, the quotes and backslashes in the variables \*\_FLAGS and \*\_ARGS are interpreted as the command line shell would. For example, setting ECOHMEM\_APP\_ARGS="a b1\ b2 c" or ECOHMEM\_APP\_ARGS="a 'b1 b2' c" will pass 3 arguments to the application; a, "b1 b2", and c.

The clear\_env.src script can be sourced to clear the framework configuration variables from your command line environment.


### 1. Profiling run

This step is performed using the *profile\_run.sh* script. When executed it performs several substeps:
- run your application under Extrae to generate the profiling trace
- merge the intermediate trace using mpi2prv if Extrae is not configured to do it
- generate the Paramedir configuration files customized for the current Extrae trace
- run Paramedir and allocs\_info to postprocess and extract the data that will be used later on by the hmem\_advisor.

To avoid starting from scratch if any of the substeps fail, this script tries to detect which ones were done in previous runs, and skip them until the first pending substep. This behavior can be changed using the following flags:
- --force: start from scratch.
- --force-cfgs: regenerate the Paramedir configuration files.
- --force-postprocess: redo the trace postprocessing with Paramedir and allocs\_info.

The script can be run without any argument and it will take all the information it needs from the environment variables configured in the previous step. For convenience, some of the environment variables can be overridden using the following command line arguments:
- --trace-name
- --trace-type
- --output-dir
- --app-args
- --app-runner
- --runner-flags
- --mpirun-flags
- --mpi2prv-flags

Once the script finishes the output directory (set by ECOHMEM\_TRACE\_OUTPUT\_DIR or the --output-dir argument) will contain the Extrae trace, the postprocessed data and the application output and error logs.


### 2. Memory object distribution

The second step is done using the *generate\_distribution.sh* script, which is a wrapper around the hmem\_advisor program. This program uses the postprocessed profiling data to compute the cost heuristics for each object, and then distributes the objects across the available memory tiers. The hmem\_advisor accepts several arguments to configure its behavior (set by ECOHMEM\_ADVISOR\_EXTRA\_ARGS or the --extra-args flag accepted by the script):

- --mem-config: path to configuration file describing the available memory tiers, required.
- --loads: path of csv file with load accesses information, required.
- --sizes: path of csv file with memory object size information, required.
- --stores: path of csv file with store accesses information.
- --worst
- --algo
- --metric
- --page: memory page size, defaults to 4KB
- --verbose
- --rank: Use statistics from a given rank instead of aggregating from all ranks.
- --rank-statistics: How are rank statistics aggregated together (Total, Average).
- --visualizer
- --allocs-info: path of json file with memory allocations lifetime information.
- --num-ranks: number of MPI ranks used to run the application.
- --disable-bw-aware: disable the BW-aware distribution refinement step.

Available command line arguments for the *generate\_distribution.sh* script:
- --trace-type
- --output-file
- --input-dir
- --mem-config
- --extra-args
- --force


### 3. Run with automatic object distribution

Finally, you can run your application using the memory object distribution computed in the previous step running the *run.sh* script with the --flexmalloc flag. It will execute your application preloading the Flexmalloc library, which will divert each dynamic memory allocation to the memory tier specified in the file generated by the hmem\_advisor. If you run this script without the --flexmalloc flag it will execute the application without any change or profiling, which may be useful to collect the baseline execution time.
 
Available command line arguments:
- --obj-file
- --app-args
- --app-runner
- --runner-flags
- --mpirun-flags
- --flexmalloc-config
- --flexmalloc

Flexmalloc supports several memory types. You have to specify which ones are available in its configuration file. Here are a few examples on how to do it:

- posix: Allocates data using the standard posix function.
```
# Memory configuration for allocator posix
Size <MB available per process> MBytes
```
- memkind/pmem: Allocates data on persistent memory mounted as FSDAX.
```
# Memory configuration for allocator memkind/pmem-fsdax
@ </path/to/pmem 0> ... @ </path/to/pmem N>
```
- memkind/hbwmalloc: HBW memory available in KNL processors
```
# Memory configuration for allocator memkind/hbwmalloc
Size <MB available per process> MBytes
```

For further information about Flexmalloc features and usage, take a look at its own documentation.


## Licensing

Copyright (C) 2021-2022  Barcelona Supercomputing Center (BSC)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


The full GPLv2 license is available in the LICENSE file.


## Articles

These are the academic papers related to this framework:

- H. Servat, J. Labarta, H. C. Hoppe, J. Giménez, and A. J. Peña, "Understanding memory access patterns using the BSC performance tools", Parallel Computing, Elsevier, vol. 78, pp. 1-14, Oct. 2018.
- H. Servat, A. J. Peña, G. Llort, E. Mercadal, H. C. Hoppe, and J. Labarta, "Automating the application data placement in hybrid memory systems", in IEEE Cluster, Hawaii, USA, Sep. 2017.
- H. Servat, J. Labarta, H. Hoppe, J. Gimenez, and A. J. Peña, "Integrating memory perspective into the BSC performance tools", in Tenth International Workshop on Parallel Programming Models and Systems Software for High-End Computing (P2S2), Bristol, UK, Aug. 2017.
- A. J. Peña and P. Balaji. "A framework for tracking memory accesses in scientific applications", in 43nd International Conference on Parallel Processing Workshops (ICPP-W), Minneapolis, MN, USA, Sep. 2014.
- A. J. Peña and P. Balaji, "Toward the efficient use of multiple explicitly managed memory subsystems", in IEEE Cluster, Madrid, Spain, Sep. 2014.
