#!/usr/bin/env zsh

if [[ $(cat ${aapadmintools}/scripts/aapfind/logs/aapfind_notify | wc -w) -gt 0 ]]; then 
    notifications=$(cat ${aapadmintools}/scripts/aapfind/logs/aapfind_notify)
    cat ${aapadmintools}/scripts/aapfind/logs/aapfind_notify
    echo "" > ${aapadmintools}/scripts/aapfind/logs/aapfind_notify
fi