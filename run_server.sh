#!/bin/bash

i=1
LOCAL_TEST=1
BYTES_LENGTH=1024
TEXT_LENGTH=1024
INPUT_FILE=./producer/tom-sawyer.txt

if [[ LOCAL_TEST -eq 1 ]] ; then
    CONFIG_PATH="--configPath ./conf/localConf.yaml"
else
    CONFIG_PATH="--configPath ./conf/remoteConf.yaml"
fi

if [[ -f "child_pids" ]] ; then
    rm child_pids
fi

run_cmd() {
    local cmd=$1
    echo $cmd
    eval $cmd
    child_pid=$!
    # parent_pid=$$
    echo ${child_pid} >> child_pids
}

ad-events-producer() {
    while read line; do
        echo "# Starting ad-events producer ($i) with throughput = $line "
        run_cmd "java -cp .:./producer/* setup.core -r -t $line ${CONFIG_PATH} &"
        i=$((i+1))
    done < "${1:-/dev/stdin}"
}

bytes-producer() {
    while read line; do
        echo "# Starting bytes producer ($i) with throughput = $line "
        run_cmd "java -cp .:./producer/* setup.core --bytes --throughput $line --length ${BYTES_LENGTH} ${CONFIG_PATH} &"
        i=$((i+1))
    done < "${1:-/dev/stdin}"
}

rand-text-producer() {
    while read line; do
        echo "# Starting rand-text producer ($i) with throughput = $line "
        run_cmd "java -cp .:./producer/* setup.core --rand-text --throughput $line --length ${TEXT_LENGTH} ${CONFIG_PATH} &"
        i=$((i+1))
    done < "${1:-/dev/stdin}"
}

file-producer() {
    while read line; do
        echo "# Starting file producer ($i) with throughput = $line "
        run_cmd "java -cp .:./producer/* setup.core --file --input-file ${INPUT_FILE} --throughput $line ${CONFIG_PATH} &"
        i=$((i+1))
    done < "${1:-/dev/stdin}"
}

case "$1" in
    ad)
        echo "Starting ad-events server"
        nc -vv -l 7777 | ad-events-producer
        ;;
    bytes)
        echo "Starting bytes server"
        nc -vv -l 7777 | bytes-producer
        ;;
    rand)
        echo "Starting rand-text server"
        nc -vv -l 7777 | rand-text-producer
        ;;
    file)
        echo "Starting file server"
        nc -vv -l 7777 | file-producer
        ;;
    *)
        echo "Usage: $0 {ad|bytes|rand|file}"
        exit 1
esac

