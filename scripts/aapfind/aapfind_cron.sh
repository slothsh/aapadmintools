#!/bin/zsh

updatelatestlog () {
    # 1: latest_log
    echo $1 > ${aapadmintools}/logs/aapfind_history
}

getlatestlog () {
    # 1: log_type
    case $1 in
        "history")
            if [[ -f ${aapadmintools}/logs/aapfind_history ]]; then
                local all_logs=($(ls -t ${aapadmintools}/logs | grep '.log' | sed -e 's/\n/ /'))
                echo ${all_logs[1]}
            else
                echo ""
            fi
            ;;

        "notify")
            if [[ -f ${aapadmintools}/logs/aapfind_notify ]]; then
                local notify_log=$(cat ${aapadmintools}/logs/aapfind_notify | sed -e 's/ /%ws%/g'| tr '\n' ' ')
                echo $notify_log
            else
                echo ""
            fi
            ;;

        *)
            echo ""
            ;;
    esac
}

logresults () {
    # 1: out_path
    # 2: contents
    # 3: new_log
    # 4: new_line

    local day=$(date +"%d")
    local month=$(date +"%m")
    local year=$(date +"%Y")
    local log_ids=($(find $1 -name "*$day-$month-$year*" | sed -e 's/.*_.*_//' -e 's/\.log//'))

    (( ${#log_ids[@]} > 0 )) && max=${log_ids[1]} || max=0
    for n in "${log_ids[@]}"; do
        (( n > max )) && max=$n
    done
    local log_name="aapfind_$(date +"%d-%m-%Y")_$max.log"
    if [[ -f $1/$log_name && $3 = false ]]; then
        if [[ $4 = false ]]; then
            echo -ne "\n$2" >> "$1/$log_name"
        else
            echo "\n$2" >> "$1/$log_name"
        fi
    else
        local log_name="aapfind_$(date +"%d-%m-%Y")_$(( $max + 1 )).log"
        if [[ $4 = false ]]; then
            echo -ne $2 > "$1/$log_name"
        else
            echo $2 > "$1/$log_name"
        fi
    fi

    updatelatestlog $log_name
}

findmissing () {
    # 1: new_results

    # Get previous log history
    local prev_log=$(getlatestlog "history")
    local prev_notify=$(getlatestlog "notify")

    if [[ -z $prev_log ]]; then
        local prev_files=()
    else
        local prev_files=($(egrep -Roh '^/.*$' ${aapadmintools}/logs/${prev_log} | sort | uniq | sed -e 's/ /%ws%/g' | tr '\n' ' '))
    fi

    if [[ -z $prev_notify ]]; then
        local prev_notifications=()
    else
        local prev_notifications=($(echo ${prev_notify}))
    fi

    local new_files=($(echo $1 | sed -e 's/ /%ws%/g' | tr '\n' ' '))
    local collected=""

    for new in "${new_files[@]}"; do
        local found="false"
        for previous in "${prev_files[@]}"; do
            if [[ $new = $previous ]]; then
                local found="true"
                break
            fi
        done
        for previous in "${prev_notifications[@]}"; do
            if [[ $new = $previous ]]; then
                local found="true"
                break
            fi
        done
        if [[ $found = "false" ]]; then
            if [[ -z $collected ]]; then
                collected="$new"
            else
                collected+=" $new"
            fi
        fi
    done

    echo $collected
}

searchserver () {
    # 1: root_path
    # 2: sub_path
    # 3: exclude_path
    # 4: query
    # 5: file_type
    # 6: save_output
    # 7: new_log
    # 8: negation
    # 9: filter

    if [[ -v tmpadmin ]]; then
        local tmp_path=${tmpadmin}
    else
        local tmp_path=.
    fi

    find ${1}/${2} -path ${1}/${2}/${3} -prune -false -o -name ${4} -type f ! -name ${8} > ${tmp_path}/tempbak
    local all_results=$(egrep -v ${9} ${tmp_path}/tempbak)

    if [[ ! -d ${aapadmintools}/logs ]]; then
        mkdir ${aapadmintools}/logs
    fi

    rm ${tmp_path}/tempbak
    local i=0
    local all_files=($(echo $all_results | sed 's/ /%ws%/g' | tr '\n' ' '))
    if [[ ${#all_files[@]} > 0 ]]; then
        echo "${5} files were found in ${2}:"
        for result in "${all_files[@]}"; do
            echo "  $(( $i + 1 )): $(echo $result | sed 's/%ws%/ /g')"
            local i=$(( $i + 1 ))
        done
        echo "A total of $i ${5} files found"
    else
        echo "There were no ${5} files found in ${2}"
    fi

    # Find new files since last log
    local new_files=$(findmissing $all_results)
    
    # Add new files to notification list
    if [[ ! -z $new_files ]]; then
        local notify_files=($(echo $new_files))
        for file in "${notify_files[@]}"; do
            echo "$(echo $file | sed -e 's/%ws%/ /g')" >> ${aapadmintools}/logs/aapfind_notify
        done
    fi

    # Save results to logs
    if [[ $6 = true ]]; then
        description="Results for ${5} files @ ${2}:"
        logresults "${aapadmintools}/logs" "$(date +"%c")" false false
        logresults "${aapadmintools}/logs" $description false false
        logresults "${aapadmintools}/logs" $all_results $7
    fi
}

# Check if user has devmount set in environment
if [[ -v devmount ]]; then
    # Path variables
    share_path="/Volumes/Public"

    # SMB login credentials
    smb_user=AAP_1
    smb_server=AAPSERVER
    smb_share=Public
    smb_pass=Africa\=2018!

    # SMB paths
    smb_path=$devmount
    smb_searchdir1="DROP/1_PRE_PRODUCTION/PENDING"
    smb_exclude1="_OLD"
    smb_searchdir2="DROP/1_PRE_PRODUCTION/SESSION"
    smb_exclude2=" OLD"

    # Search queries
    find_all="*"
    find_all_negation="*.ptx"
    find_all_filter=".DS_Store"
    find_wav="*.wav"
    find_bak="*.bak.*"

    # Verify if SMB is mounted
    if [[ $(df | grep 'AAPSERVER') = "" ]]; then
        # Check if user has .devmount
        if [[ ! -d "${smb_path}/aapserver" ]]; then
            echo "Mount point does not exist, creating new one..."
            mkdir "${smb_path}/aapserver" && echo "Mount point successfully created!" || echo "Could not create new mount point"
            smb_path="$devmount/aapserver"
        fi &&
        echo "Mounting ${smb_server}..."
        mount -t smbfs //${smb_user}:${smb_pass}@${smb_server}/${smb_share} ${smb_path} && echo "${smb_server} successfully mounted!" || echo "Could not mount ${smb_server}"
    else
        smb_status=($(df | grep 'AAPSERVER' | sed 's/  / /g'))
        smb_path=$smb_status[9]
        echo "${smb_server} already mounted @ ${smb_path}"
    fi

    # Handle input parameters
    [ -v $1 ] && 1=true
    [ -v $2 ] && 2=false

    echo ""
    searchserver ${smb_path} ${smb_searchdir1} ${smb_exclude1} ${find_all} "Non-PTX" $1 $2 ${find_all_negation} ${find_all_filter}

    echo ""
    searchserver ${smb_path} ${smb_searchdir2} ${smb_exclude2} ${find_all} "Non-PTX" $1 false ${find_all_negation} ${find_all_filter}

    # Unmount the share according mount point
    if [[ $(echo $smb_path | grep 'Volumes') != "" ]]; then
        echo "\nNot unmounting ${smb_server}"
    else
        echo "\nUnmounting ${smb_server}..."
        diskutil unmount ${smb_path} > /dev/null && rmdir ${smb_path} && echo "Successfully unmounted ${smb_server}!" || "Could not unmount ${smb_server}. Please retry manually"
    fi
else
    echo "Cannot find a user local mount point. Please set it, and try again"
fi

