#!/usr/bin/env zsh

# Colours for formatting & server search script
disable_colours=true
if [[ -v aapadmintools ]]; then
    [[ ! -f /dev/stdout ]] && source ${aapadmintools}/scripts/shcolours.sh && disable_colours=false
    source ${aapadmintools}/scripts/shcoloursdbg.sh
    source ${aapadmintools}/scripts/loading.sh
    source ${aapadmintools}/scripts/connectsmb.sh
fi

# Handle command-line
IFS_=$IFS
while getopts 'n:c:e:' arg 2>/dev/null; do
    case $arg in
        n)
            proj_name=$OPTARG
            ;;
        c)
            proj_code=$OPTARG
            ;;
        e)
            episode_list=()
            re_episode_flag="(-e|^)[0-9]+((,|, +| +|:|$)[0-9]+)*"
            skip=false
            IFS=","
            for i in ${@}; do
                if [[ ${i} =~ $re_episode_flag ]]; then
                    [[ ${i:0:2} =~ "-[^e]" ]] && skip = true
                    [[ ${i:0:2} = "-e" ]] && i=$(echo $i | sed -e 's/-e//g') && skip = false
                    [[ $skip = false ]] && for j in $(echo $i | sed -e 's/,$//g' -e 's/,/ /g'); do episode_list+=$j; done
                fi
            done
            IFS=$IFS_

            episode_list=($(for v in $episode_list[@]; do
                re_colon='^[0-9]+:[0-9]+$'
                [[ $v =~ $re_colon ]] && pair=(${(s(:))v}) && range=($(seq $pair[1] $pair[2])) && echo $range || echo $v
            done | xargs))
            episode_list=($(for v in $episode_list[@]; do echo $v; done | sort -n | uniq))
            ;;
    esac
done

do_exit=false
if [[ -z $proj_name ]]; then
    printf "${_red}error: please specify a project name with flag -n\n${_reset}"
    do_exit=true
fi

if [[ -z $proj_code ]]; then
    printf "${_red}error: please specify a project code with flag -c\n${_reset}"
    do_exit=true
fi

[[ $#episode_list[@] = 0 ]] && printf "${_red}error: please specify an episode range with flag -e\n${_reset}" && do_exit=true

if [[ $do_exit = true ]]; then
    exit 1
fi

IFS=
for e in $episode_list[@]; do
    printf "P_${proj_name} [${proj_code}] {EP${e} V1}\n";
done
