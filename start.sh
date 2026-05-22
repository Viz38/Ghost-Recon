#!/bin/bash

# Ghost Unified Engine: Standalone Control Script
# 💀 "Reviving the Dead with Spectral Precision"

# --- CONFIGURATION ---
if [ -f ".env" ]; then
    GHOST_SHEET_ID=$(grep '^GHOST_SHEET_ID=' .env | cut -d '=' -f2)
fi

DEFAULT_SHEET="$GHOST_SHEET_ID"

if [ -z "$DEFAULT_SHEET" ]; then
    echo -e "\n\033[93m   [FIRST LAUNCH] Please enter your Google Sheet ID or full URL >> \033[0m"
    read -p "   >> " user_sheet
    
    if [[ "$user_sheet" == *"spreadsheets/d/"* ]]; then
        DEFAULT_SHEET=$(echo "$user_sheet" | sed -n 's/.*spreadsheets\/d\/\([a-zA-Z0-9-_]*\).*/\1/p')
    else
        DEFAULT_SHEET="$user_sheet"
    fi
    
    echo "GHOST_SHEET_ID=$DEFAULT_SHEET" >> .env
    echo -e "\033[92m   [SUCCESS] Sheet ID saved to .env!\033[0m"
fi
ENGINE_DIR=$(dirname "$0")
VENV_DIR="$ENGINE_DIR/.venv"

# --- LOGO & UI ---
print_banner() {
    clear
    echo -e "\033[1;94m"
    cat << "EOF"
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠃⠹⠄⠀⠸⣿⣿⣧⠀⠀⠘⠙⠛⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣯⡏⠁⠀⠀⠀⠀⠀⠀⠐⣿⣿⠷⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⣅⡄⠸⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠘⠉⣽⡏⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⣸⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠙⠗⠋⣿⣇⣹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣗⣀⢠⣀⣠⣤⣤⡀⠐⠀⢹⣿⠀⠔⠠⣄⣤⣤⣠⣄⣀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⣿⣿⡄⠀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠈⣿⣿⠃⠀⢿⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠒⢌⠉⠻⠿⠿⠟⠋⠀⢀⣽⣿⣄⠀⠈⠙⠻⠿⠟⠋⠛⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠑⢄⠀⠀⠀⠀⢰⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣤⣄⠀⠀⠈⠑⠉⠓⢆⠸⠿⢻⣿⠻⠿⠀⠀⠀⠀⠀⢀⣠⠀⣀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⠁⢹⠢⡀⠀⠀⠀⠈⠓⢢⠸⡏⠀⠀⠀⠀⠀⠀⠀⠀⢸⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣴⡈⢑⠢⢄⡀⠀⠀⢹⣿⣄⠀⢀⣀⣀⣸⢹⡟⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⠳⣮⡀⠄⠀⢱⡦⢼⣿⡬⣯⡍⠀⠀⣉⢙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣿⣿⣿⣰⡄⣸⣷⣾⣿⣿⣿⠀⣤⣸⣿⣿⣯⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⣿⣿⣏⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
EOF
    echo -e "\033[0m"
    echo -e "\033[1;97m   GHOST RECON \033[0m\033[90m| \033[96mSingularity v15.0\033[0m"
    echo -e "\033[90m   "$(printf '─%.0s' {1..54})"\033[0m"
    echo -e "\033[3;37m   \"Recon team ready for dead domain revival!\"\033[0m"
    echo ""
}

# --- FUNCTIONS ---
setup_env() {
    echo -e "\033[93m[START] Setting up Integrated Environment (uv)...\033[0m"
    if ! command -v uv &> /dev/null; then
        echo -e "\033[91m[ERROR] 'uv' not found. Installing...\033[0m"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
    fi
    
    cd "$ENGINE_DIR"
    uv venv --python 3.12
    source .venv/bin/activate
    uv pip install -r requirements.txt
    python3 -m playwright install chromium
    echo -e "\033[92m[SUCCESS] Environment ready.\033[0m"
    sleep 2
}

run_engine() {
    local mode=$1
    local data_type=${2:-text}
    echo -e "\033[94m[START] Launching Ghost Unified Engine (Mode: ${mode:-full}, Format: ${data_type})...\033[0m"
    if [ ! -d "$VENV_DIR" ]; then
        setup_env
    fi
    
    cd "$ENGINE_DIR"
    source .venv/bin/activate
    
    if [ -n "$mode" ] && [ "$mode" != "full" ]; then
        python3 ghost.py "$DEFAULT_SHEET" --mode "$mode" --data-type "$data_type"
    else
        python3 ghost.py "$DEFAULT_SHEET" --data-type "$data_type"
    fi
    read -p "Press Enter to return to menu..."
}

# --- MAIN MENU ---
while true; do
    print_banner
    echo -e "\033[97m   [1] Full Run         \033[90m(Full Single-Pass Strategy)\033[0m"
    echo -e "\033[97m   [2] Live Recon Only  \033[90m(Skip archives | Fast sweep)\033[0m"
    echo -e "\033[97m   [3] Archival Recon Only\033[90m(Skip live | Deep history)\033[0m"
    echo -e "\033[97m   [4] Web Recon Only   \033[90m(Skip live and archives | Deep Web Search)\033[0m"
    echo -e "\033[97m   [5] SMART RESUME     \033[90m(Continue from GSheet Status)\033[0m"
    echo -e "\033[97m   [6] SETUP ENGINE     \033[90m(Reinstall Dependencies)\033[0m"
    echo -e "\033[97m   [7] DIAGNOSTICS      \033[90m(System Health Check)\033[0m"
    echo -e "\033[97m   [8] CLEAR LOGS       \033[90m(Truncate log files)\033[0m"
    echo -e "\033[91m   [9] EXIT             \033[90m(Close Hub)\033[0m"
    echo ""
    read -p "   [GHOST] Select Strategy >> " choice

    case $choice in
        1|2|3|4|5)
            echo ""
            read -p "   [GHOST] Select Output Format [1] Text Only (Faster) [2] HTML >> " dtype_choice
            data_type="text"
            if [ "$dtype_choice" == "2" ]; then
                data_type="html"
            fi
            ;;
    esac

    case $choice in
        1)
            run_engine "full" "$data_type"
            ;;
        2)
            run_engine "live" "$data_type"
            ;;
        3)
            run_engine "archival" "$data_type"
            ;;
        4)
            run_engine "search_only" "$data_type"
            ;;
        5)
            run_engine "full" "$data_type" # Smart Resume is just a full run starting from sheet status
            ;;
        6)
            setup_env
            ;;
        7)
            echo -e "\033[97m[DIAGNOSTICS] Checking system...\033[0m"
            sysctl -n hw.memsize | awk '{print "RAM: " $1/1024/1024/1024 " GB"}'
            sysctl -n hw.ncpu | awk '{print "Cores: " $1}'
            python3 --version
            uv --version
            read -p "Press Enter to return..."
            ;;
        8)
            echo -e "\033[93m[LOGS] Clearing log files...\033[0m"
            > ghost.log
            > spectral.log
            echo -e "\033[92m[SUCCESS] Logs cleared.\033[0m"
            sleep 1
            ;;
        9)
            echo -e "\033[90mTerminating session...\033[0m"
            exit 0
            ;;
        *)
            echo -e "\033[91mInvalid selection.\033[0m"
            sleep 1
            ;;
    esac
done
