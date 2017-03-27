#!/bin/bash

i=1
LOCAL_TEST=1
BYTES_LENGTH=1024
TEXT_LENGTH=1024
BOOK_FILE=./resources/tom-sawyer.txt
PAGEVIEW_FILE=./resources/page-views.txt

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
        run_cmd "java -cp .:./producer/* setup.core --bytes --throughput $line --length ${BYTES_LENGTH} --kafka-topic bytes ${CONFIG_PATH} &"
        i=$((i+1))
    done < "${1:-/dev/stdin}"
}

rand-text-producer() {
    while read line; do
        echo "# Starting rand-text producer ($i) with throughput = $line "
        run_cmd "java -cp .:./producer/* setup.core --rand-text --throughput $line --length ${TEXT_LENGTH} --kafka-topic rand ${CONFIG_PATH} &"
        i=$((i+1))
    done < "${1:-/dev/stdin}"
}

book-text-producer() {
    while read line; do
        echo "# Starting file producer ($i) with throughput = $line "
        run_cmd "java -cp .:./producer/* setup.core --file --input-file ${BOOK_FILE} --throughput $line --kafka-topic book ${CONFIG_PATH} &"
        i=$((i+1))
    done < "${1:-/dev/stdin}"
}

page-view-producer() {
    while read line; do
        echo "# Starting file producer ($i) with throughput = $line "
        run_cmd "java -cp .:./producer/* setup.core --file --input-file ${PAGEVIEW_FILE} --throughput $line --kafka-topic view ${CONFIG_PATH} &"
        i=$((i+1))
    done < "${1:-/dev/stdin}"
}

case "$1" in
    ad)
        echo "Starting ad-events producer"
        nc -vv -l 7777 | ad-events-producer
        ;;
    bytes)
        echo "Starting bytes producer"
        nc -vv -l 7777 | bytes-producer
        ;;
    rand)
        echo "Starting rand-text producer"
        nc -vv -l 7777 | rand-text-producer
        ;;
    book)
        echo "Starting book-text producer"
        nc -vv -l 7777 | book-text-producer
        ;;
    view)
        echo "Starting page-view producer"
        nc -vv -l 7777 | page-view-producer
        ;;
    *)
        echo "Usage: $0 {ad|bytes|rand|book|view}"
        exit 1
esac

