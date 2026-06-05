#!/bin/bash

for f in /workspace/images/*; do
    name=$(basename "$f")

    hdfs dfs -test -e "/project/images/raw/$name"

    if [ $? -ne 0 ]; then
        echo "Uploading $name"
        hdfs dfs -put "$f" "/project/images/raw/$name"
    else
        echo "Skipping $name"
    fi
done