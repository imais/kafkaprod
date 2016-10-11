#!/bin/bash

i=1
while read line
do
  echo "# Starting network-test producer ($i) with throughput = $line "
  java -cp .:./producer/* setup.core -b -t $line -l 1024 &
  i=$((i+1))
done < "${1:-/dev/stdin}"

