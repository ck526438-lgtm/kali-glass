# Autocomplétion bash pour kali-glass
_kali_glass() {
    local cur prev cmds
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    cmds="apply wallpaper list mode blur panel-opacity dock dynamic install-themes login restore status doctor live"

    if [[ $COMP_CWORD -eq 1 ]]; then
        mapfile -t COMPREPLY < <(compgen -W "$cmds -v --verbose --version --help" -- "$cur")
        return
    fi
    if [[ "${COMP_WORDS[1]}" == "live" ]]; then
        case "$prev" in
            live) mapfile -t COMPREPLY < <(compgen -W "set stop toggle list download add options thumb" -- "$cur") ;;
            set|thumb)
                local vids
                vids=$(kali-glass live list 2>/dev/null | sed -n 's/^[ ●]*\([^ ]*\) .*Mo.*/\1/p')
                mapfile -t COMPREPLY < <(compgen -W "$vids" -- "$cur")
                mapfile -t -O "${#COMPREPLY[@]}" COMPREPLY < <(compgen -f -- "$cur") ;;
            add) mapfile -t COMPREPLY < <(compgen -f -- "$cur") ;;
            --quality) mapfile -t COMPREPLY < <(compgen -W "auto 2160p 1080p" -- "$cur") ;;
            --audio|--pause-fullscreen|--pause-battery) mapfile -t COMPREPLY < <(compgen -W "on off" -- "$cur") ;;
            download) mapfile -t COMPREPLY < <(compgen -W "--quality --only --force" -- "$cur") ;;
            options) mapfile -t COMPREPLY < <(compgen -W "--audio --pause-fullscreen --pause-battery --speed" -- "$cur") ;;
        esac
        return
    fi
    case "$prev" in
        wallpaper|--wallpaper)
            local names
            names=$(kali-glass list 2>/dev/null | awk '{print $(NF-1)}')
            mapfile -t COMPREPLY < <(compgen -W "$names" -- "$cur")
            mapfile -t -O "${#COMPREPLY[@]}" COMPREPLY < <(compgen -f -- "$cur")
            ;;
        mode)    mapfile -t COMPREPLY < <(compgen -W "dark light" -- "$cur") ;;
        dock|dynamic) mapfile -t COMPREPLY < <(compgen -W "on off" -- "$cur") ;;
        blur)    mapfile -t COMPREPLY < <(compgen -W "0 3 5 7 9 12 15 20" -- "$cur") ;;
        panel-opacity) mapfile -t COMPREPLY < <(compgen -W "0 15 25 35 50 75 100" -- "$cur") ;;
        apply)   mapfile -t COMPREPLY < <(compgen -W "--light --wallpaper --no-themes --keep-mode" -- "$cur") ;;
        login)   mapfile -t COMPREPLY < <(compgen -W "--wallpaper" -- "$cur") ;;
    esac
}
complete -F _kali_glass kali-glass
