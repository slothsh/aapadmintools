#!/bin/zsh

if [[ $(cat ${aapadmintools}/logs/aapfind_notify | wc -w) -gt 0 ]]; then 
    notifications=$(cat ${aapadmintools}/logs/aapfind_notify)
    cat ${aapadmintools}/logs/aapfind_notify
    echo "" > ${aapadmintools}/logs/aapfind_notify
fi