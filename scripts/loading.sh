#!/bin/zsh

load() {
    tput civis
    local text="${blue}$2\033[0K\r${reset}"
    echo -ne $text
    while kill -0 $1 2>/dev/null; do
        local dot=""
        for i in {0..3}; do
            local text="${blue}$2$dot\033[0K\r${reset}"
            local dot="$dot."
            echo -ne $text
            sleep 0.5
        done
    done
    echo -ne "\033[0K\r"
    tput cnorm
}