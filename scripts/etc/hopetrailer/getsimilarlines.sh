#!/usr/bin/env zsh

while IFS= read -r line; do
    tc=$(echo $line | cut -f 1)
    search=$(echo $line | cut -f 2)
    results=$()
    printf "$results\n"
done < ./output/results.lines