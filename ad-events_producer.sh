#!/bin/bash

i=1
while read line
do
  echo "# Starting ad-events producer ($i) with throughput = $line "
  java -cp .:./producer/* setup.core -r -t $line &
  i=$((i+1))
done < "${1:-/dev/stdin}"

