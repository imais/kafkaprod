#!/bin/bash

case "$1" in
    ad-events)
        echo "Starting 'ad-events' server"
        nc -vv -l 7777 | ./ad-events_producer.sh
        ;;
    network-test)
        echo "Starting 'network-test' server"
        nc -vv -l 7777 | ./network-test_producer.sh
        ;;
    *)
        echo "Usage: $0 {ad-events|network-test}"
        exit 1
esac
