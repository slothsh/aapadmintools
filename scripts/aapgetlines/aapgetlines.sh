#!/usr/bin/env zsh

# Colours for formatting & server search script
disable_colours=true
if [[ -v aapadmintools ]]; then
    [[ ! -f /dev/stdout ]] && source ${aapadmintools}/scripts/shcolours.sh && disable_colours=false
    source ${aapadmintools}/scripts/shcoloursdbg.sh
    source ${aapadmintools}/scripts/loading.sh
    source ${aapadmintools}/scripts/connectsmb.sh
fi

# Save IFS
IFS_=$IFS

# Parse input flags
report_errors=false
error_list=()
re_valid_name="^[A-z0-9]+$"
re_numbers="^[0-9]+$"

# Parse input arguments
while getopts 'j:u:p:c:l:e:s:f' arg 2>/dev/null; do
    case $arg in
        p)
            inpath="$OPTARG";
            # TODO: error reporting
            ;;
        c)
            character_list=()
            re_character_flag="(-c|^)[A-z0-9_, \-]*$"
            skip=false
            IFS=","
            for i in ${@}; do
                if [[ ${i} =~ $re_character_flag ]]; then
                    [[ ${i:0:2} =~ "-[^c]" ]] && skip=true
                    [[ ${i:0:2} = "-c" ]] && i=$(echo $i | sed -e 's/-c//g') && skip=false
                    [[ $skip = false ]] && for j in $(echo $i | sed -e 's/,$//g' -e 's/,/ /g'); do character_list+=$j; done
                fi
            done
            IFS=$IFS_

            # Ensure that at least 1 character was specified
            [[ $#character_list[@] = 0 ]] && error_list+="please specify at least one character to search with flag -c" && report_errors=true

            character_list=($(for v in $character_list[@]; do
                echo $v
            done | xargs))
            character_list=($(for v in $character_list[@]; do echo $(echo $v | tr '[:lower:]' '[:upper:]' | sed -e 's/^[[:space:]]*//g' -e 's/ *$//g'); done | sort -n | uniq))
            ;;

        l)
            line="$OPTARG"
            # printf "$OPTARG\n"
            ;;
        u)
            update_cuefiles="$OPTARG"
            report_errors=false
            ;;

        j)
            search_proj="$OPTARG"

            # Clear bad characters from search path
            search_proj=$(echo $search_proj | sed -E -e "s/'|\"//g")

            # Error check
            [[ ! $search_proj =~ $re_valid_name ]] && error_list+="please provide a valid project name to search for with flag -j" && report_errors=true
            [[ ! -d "$tmpadmin/aapgetlines/cuefiles/$(echo $search_proj | sed -e 's/ /_/g')" ]] && error_list+="no local EDL files found for $search_proj" && report_errors=true
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

            # Ensure that at least 1 episode was specified
            [[ $#episode_list[@] = 0 ]] && error_list+="please specify at least one episode to search with flag -e" && report_errors=true

            episode_list=($(for v in $episode_list[@]; do
                re_colon='^[0-9]+:[0-9]+$'
                [[ $v =~ $re_colon ]] && pair=(${(s(:))v}) && range=($(seq $pair[1] $pair[2])) && echo $range || echo $v
            done | xargs))
            episode_list=($(for v in $episode_list[@]; do echo $v; done | sort -n | uniq))
            ;;

        f)
            [[ ${(P)$(( OPTIND + 1)):0:1} = "-" || ${(P)$(( OPTIND + 1)):0:1} = "" ]] && flush_local="all" || flush_local=${(P)$(( OPTIND + 1))}
            report_errors=false
            ;;

        s)
            ;;

        :)
            printf "${_red}aapgetlines: please provide an arguments for flag -${arg}${_reset}\n" >&2
            exit 1
            ;;

        ?)
            printf "${red:-""}aapgetlines: no options for flag ${(P)OPTIND}\n${reset:-""}"
            exit 1
            ;;
    esac
done
shift $((OPTIND -1))

# Check if essential flags were set
if [[ ! -v update_cuefiles && ! -v flush_local ]]; then 
    [[ ! -v character_list ]] && error_list+="flag -c must be specified${reset:-""}" && report_errors=true
    [[ ! -v search_proj ]] && error_list+="flag -j must be specified" && report_errors=true
fi

# Error reporting for essential flags
if [[ $report_errors = true ]]; then
    for v in $error_list[@]; do printf "${_red}aapgetlines: $v${_reset}\n" >&2; done;
    exit 1
fi

# Flush if a flag has been set
if [[ $flush_local = "all" ]]; then
    printf "${blue:-""}Flushing all local EDL files...${reset:-""}\n"
    rmpath=$tmpadmin/aapgetlines/cuefiles
    rm $rmpath/*/**
    rmdir $rmpath/**
    printf "${green:-""}Flushing complete!${reset:-""}\n"
    exit 0
elif [[ -v flush_local && -d $tmpadmin/aapgetlines/cuefiles/$(echo $flush_local | sed -e "s/ /_/g") ]]; then
    printf "${blue:-""}Flushing EDL files for $flush_local...${reset:-""}\n"
    rmpath=$tmpadmin/aapgetlines/cuefiles/$(echo $flush_local | sed -e "s/ /_/g")
    rm $rmpath/**
    rmdir $rmpath
    printf "${green:-""}Flushing complete!${reset:-""}\n"
    exit 0
fi

# Update local EDL files from remote if a flag is set
if [[ -v update_cuefiles && $update_cuefiles != "" ]]; then
    # Path variables
    share_path="/Volumes/Public"

    # SMB paths
    smb_path=$devmount
    smb_searchdir1="DROP/2_CUE_FILES"
    [[ $update_cuefiles != "all" ]] && smd_searchprod=$update_cuefiles 

    # Verify if SMB is mounted
    connectsmb

    if [[ -v tmpadmin ]]; then
        local tmp_path=${tmpadmin}
    else
        local tmp_path=.
    fi

    # Check if path exists
    fetch_path=$(find ${smb_path}/${smb_searchdir1} -type d -iname ${smd_searchprod} -maxdepth 2)

    if [[ $fetch_path != "" ]]; then
        # Get folder names for local directory
        current_prod=$(basename $fetch_path | sed -e "s/ /_/g" | tr '[:upper:]' '[:lower:]' | sed -E -e "s/'|\"//g")

        # Create local directories
        [[ ! -d ${tmpadmin}/aapgetlines/ ]] && mkdir ${tmpadmin}/aapgetlines
        [[ ! -d ${tmpadmin}/aapgetlines/cuefiles ]] && mkdir ${tmpadmin}/aapgetlines/cuefiles
        [[ ! -d ${tmpadmin}/aapgetlines/cuefiles/${current_prod} ]] && mkdir ${tmpadmin}/aapgetlines/cuefiles/${current_prod}

        # Search for V2 .txt files for given show PRE_PRODUCTION/2_CUE_FILES
        find $fetch_path -name '*.txt' -type f -name '*V2*' > $tmp_path/tempbak &
        load $! "Fetching V2 prep files for ${smd_searchprod}"

        # Copy all cue files to local machine
        printf "${blue:-""}Copying files...${reset:-""}\n"
        i=0
        cat -n ${tmp_path}/tempbak | while read n f; do
            prod_code=$(basename $f | egrep -o '\[\w+\]' | sed -e 's/\[//' -e 's/\]//' | tr '[:upper:]' '[:lower:]')
            ep_n=$(basename $f | egrep -o 'EP\d+' | tr '[:upper:]' '[:lower:]')
            season=$(basename $f | egrep -o '\bS\d\d' | tr '[:upper:]' '[:lower:]')
            [[ $season = "" ]] && season='S01'
            cp -n $f "${tmpadmin}/aapgetlines/cuefiles/${current_prod}/${prod_code}_${season}_${ep_n}.txt" 2>/dev/null && i=$(( i + 1 ))
        done

        printf "${blue:-""}Copied $i of %s V2 files${reset:-""}\n" $(cat ${tmp_path}/tempbak | wc -l | sed 's/ *//g')
    fi
    
    rm ${tmp_path}/tempbak

    # Unmount the share according mount point
    disconnectsmb

    exit 0
fi

# Remove grep search colours for all lines search
[[ $line = "" ]] && line=".*" && no_colour=true || no_colour=false
[[ $disable_colours = true || $no_colour = true ]] && grep_colour=never || grep_colour=always

count_results=0
suppress_final_matches=true
# Prepare episode list & queries for searching
total_episodes=$(find "$tmpadmin/aapgetlines/cuefiles/$(echo $search_proj | sed -e 's/ /_/g')" -type f | wc -l)
[[ ${#episode_list[@]} = 0 ]] && episode_list=($(seq 1 $total_episodes)) && all_search=true && suppress_final_matches=false || all_search=false
# TODO : Loading text for long searches
episode_files=($(for n in $episode_list[@]; do find "$tmpadmin/aapgetlines/cuefiles/$(echo $search_proj | sed -e 's/ /_/g')" -name "*_ep$(printf "%02d" $n).txt" -and -type f; done))


printf "${_blue}results for $character_list in $search_proj:${_reset}\n" >&2

# Build aapgetlines binary query string
characters=""
i=0
for c in $character_list[@]; do
    (( i < $#character_list[@] - 1 )) && characters+="$c," || characters+="$c"
    i=$(( i + 1 ))
done

for f in $episode_files[@]; do
    [[ $no_colour = true ]] && results=$(echo $f | xargs -I % aapgetlines % $characters 2>/dev/null | egrep "$line" --ignore-case --color=never)
    [[ $no_colour = false ]] && results=$(echo $f | xargs -I % aapgetlines % $characters 2>/dev/null | egrep "\b$line\b" --ignore-case --color=${grep_colour})
    # [[ ! $results = "" || $all_search = false ]] && printf "${blue:-""}$(basename $f):${reset:-""}\n"
    [[ ! $results = "" || $all_search = false ]] && printf "${blue:-""}$(sed -e '1q' $f | cut -f 2):${reset:-""}\n"
    [[ $results = "" && $all_search = false ]] && printf "${yellow:-""}no matches${reset:-""}\n\n"
    [[ ! $results = "" ]] && printf "$results\n"
    [[ ! $results = "" ]] && printf "${yellow:-""}total lines matched: %s${reset:-""}\n\n" $(echo $results | wc -l)
done

[[ ${#results[@]} = 0 && $suppress_final_matches = false ]] && printf "${_yellow}no matched lines${_reset}\n"
printf "${_green}aapgetlines: search complete${_reset}\n" >&2
exit 0
