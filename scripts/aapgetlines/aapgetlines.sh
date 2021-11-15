#!/bin/zsh

# Colours for formatting & server search script
if [[ -v aapadmintools ]]; then
    source ${aapadmintools}/scripts/shcolours.sh
    source ${aapadmintools}/scripts/loading.sh
    source ${aapadmintools}/scripts/connectsmb.sh
fi

# Get commandline arguments
args=`getopt jupcle: $*`

if [[ $? != 0 ]]; then
    printf "${red}usage: please pass a path to EDL data, character name, and a line to search for\n${reset}"
    exit 2
fi

for i do
    case "$i" in
        -p)
            shift; inpath="$1";
            shift;;
        -c)
            shift; character=$(echo "$1" | tr '[:lower:]' '[:upper:]')
            shift;;

        -l)
            shift; line="$1"
            shift;;
        -u)
            shift; update_cuefiles="$1"
            shift;;

        -j)
            shift; search_proj="$1"
            shift;;

        -e)
            shift; search_episode="$1"
            shift;;

        --)
            shift; break;;
    esac
done

if [[ $update_cuefiles != "" ]]; then
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

        # Copy all cue files to local machine
        [[ ! -d ${tmpadmin}/aapgetlines/ ]] && mkdir ${tmpadmin}/aapgetlines
        [[ ! -d ${tmpadmin}/aapgetlines/cuefiles ]] && mkdir ${tmpadmin}/aapgetlines/cuefiles
        [[ ! -d ${tmpadmin}/aapgetlines/cuefiles/${current_prod} ]] && mkdir ${tmpadmin}/aapgetlines/cuefiles/${current_prod}

        # Search for V2 .txt files for given show PRE_PRODUCTION/2_CUE_FILES
        find $fetch_path -name '*.txt' -type f -name '*V2*' > $tmp_path/tempbak &
        load $! "Fetching V2 prep files for ${smd_searchprod}"

        printf "${blue}Copying files...${reset}\n"
        i=0
        cat -n ${tmp_path}/tempbak | while read n f; do
            prod_code=$(basename $f | egrep -o '\[\w+\]' | sed -e 's/\[//' -e 's/\]//' | tr '[:upper:]' '[:lower:]')
            ep_n=$(basename $f | egrep -o 'EP\d+' | tr '[:upper:]' '[:lower:]')
            cp -n $f "${tmpadmin}/aapgetlines/cuefiles/${current_prod}/${prod_code}_${ep_n}.txt" 2>/dev/null && i=$(( i + 1 ))
        done

        printf "${blue}Copied $i of %s V2 files${reset}\n" $(cat ${tmp_path}/tempbak | wc -l | sed 's/ *//g')
    fi
    
    rm ${tmp_path}/tempbak

    # Unmount the share according mount point
    disconnectsmb

    exit 0
fi

if [[ $character = "" || $search_proj = "" ]]; then
    [ -v $character ] && printf "${red}Please provide a character name with flag -c${reset}\n" >&2
    [ -v $search_proj ] && printf "${red}Please provide a project to search for with flag -j${reset}\n" >&2
    exit 1
fi

# Check if -e flag is a number
re_numbers='^[0-9]+$'
if [[ ! $search_episode =~ $re_numbers && $search_episode != "" ]]; then
   printf "${red}Please pass a valid number for an episode with flag -e${reset}\n" >&2
   exit 1
fi

# Clear bad characters from search path
search_proj=$(echo $search_proj | sed -E -e "s/'|\"//g")

if [[ $line == "" ]]; then line=".*"; no_colour="true"; else no_colour="false" fi
if [[ $search_episode != "" ]] then file_name="*_ep$search_episode.txt"; else file_name="*.txt"; fi

printf "${blue}Searching for lines for $character in $search_proj...${reset}\n" >&2
if [[ $inpath == "" ]]; then
    # find $tmpadmin/aapgetlines/cuefiles/$(echo $search_proj | sed -e 's/ /_/g') -name '*.txt' -and -type f | xargs -I % aapgetlines % $character 2>/dev/null | egrep "$line" --ignore-case --color=never && printf "\n${green}aapgetlines: search complete${reset}\n" >&2
    # [[ $no_colour == "true" ]] && find $tmpadmin/aapgetlines/cuefiles/$(echo $search_proj | sed -e 's/ /_/g') -name '*.txt' -and -type f
    [[ $no_colour == "true" ]] && find $tmpadmin/aapgetlines/cuefiles/$(echo $search_proj | sed -e 's/ /_/g') -name $file_name -and -type f | xargs -I % aapgetlines % $character 2>/dev/null | egrep "$line" --ignore-case --color=never
    [[ $no_colour == "false" ]] && find $tmpadmin/aapgetlines/cuefiles/$(echo $search_proj | sed -e 's/ /_/g') -name $file_name -and -type f | xargs -I % aapgetlines % $character 2>/dev/null | egrep "\b$line\b" --ignore-case --color=always
else
    find $inpath -name '*V2}.txt' -and -type f | xargs -I % aapgetlines % $character 2>/dev/null | egrep "\b$line\b" --ignore-case --color=always
fi

printf "${green}aapgetlines: search complete${reset}\n" >&2
exit 0
