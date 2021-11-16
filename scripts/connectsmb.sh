#!/usr/bin/env zsh

# Path variables
local share_path="/Volumes/Public"

# SMB login credentials
local smb_user=AAP_1
local smb_server=AAPSERVER
local smb_share=Public
local smb_pass=Africa\=2018!

# SMB paths
local smb_path=$devmount

connectsmb() {
    if [[ -v devmount ]]; then

        # Verify if SMB is mounted
        if [[ $(df | grep 'AAPSERVER') = "" ]]; then
            # Check if user has .devmount
            if [[ ! -d "${smb_path}/aapserver" ]]; then
                echo "${blue}Mount point does not exist, creating new one...${reset}"
                mkdir "${smb_path}/aapserver" && echo "${green}Mount point successfully created!${reset}" || echo "${red}Could not create new mount point${reset}"
                smb_path="$devmount/aapserver"
            fi &&
            echo "${blue}Mounting ${smb_server}...${reset}"
            mount -t smbfs //${smb_user}:${smb_pass}@${smb_server}/${smb_share} ${smb_path} && echo "${green}${smb_server} successfully mounted!${reset}" || echo "${red}Could not mount ${smb_server}${reset}"
        else
            smb_status=($(df | grep 'AAPSERVER' | sed 's/  / /g'))
            smb_path=$smb_status[9]
            echo "${blue}${smb_server} already mounted @ ${smb_path}${reset}"
        fi
    fi
}

disconnectsmb() {
    # Unmount the share according mount point
    if [[ -v devmount ]]; then
        if [[ $(echo $smb_path | grep 'Volumes') != "" ]]; then
            echo "${blue}\nNot unmounting ${smb_server}${reset}"
        else
            echo "${blue}\nUnmounting ${smb_server}...${reset}"
            diskutil unmount ${smb_path} > /dev/null && rmdir ${smb_path} && echo "${green}Successfully unmounted ${smb_server}!${reset}" || "${red}Could not unmount ${smb_server}. Please retry manually${reset}"
        fi
    else
        echo "${red}Cannot find a user local mount point. Please set it, and try again${reset}"
    fi
}