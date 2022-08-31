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
while getopts 'n:c:' arg 2>/dev/null; do
    case $arg in
        n)
            proj_name=$OPTARG
            ;;
        c)
            proj_code=$OPTARG
            ;;
    esac
done

files=($(find . -name '*_Ep*' -type d -depth 1 | egrep -o '_Ep\d+_' | sed -e 's/^_Ep//' -e 's/_$//' | uniq | sort))

if [[ ${#files[@]} -eq 0 ]]; then
    printf "${_red}error: no directories with correct format found${_reset}\n"
    exit 0;
fi 

ver=1
for f in $files; do
    v0="P_${proj_name} [${proj_code}] {EP${f} V0}"
    v1="${v0}/P_${proj_name} [${proj_code}] {EP${f} V1}"
    adr_files="${v1}/G_${proj_code}_Ep${f}_ADR_Files"
    ptx_file="G_${proj_code}_Ep${f}_ADR_PTX_File"
    mkdir "./${v0}" && mkdir "./${v1}" && mkdir "./${adr_files}"
    mv "./${ptx_file}" "./${adr_files}"
done
