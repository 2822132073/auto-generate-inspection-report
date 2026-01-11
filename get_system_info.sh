#!/bin/bash

# =============================================================================
# System Information Collection Script
# =============================================================================
# Description: Collects system information and uploads to server
# Usage: ./get_system_info.sh <server_url> <project_id>
# Parameters:
#   server_url: Server address (e.g., http://localhost:5000)
#   project_id: Project identifier
# Author: Generated Script
# Version: 3.0
# =============================================================================

# Script configuration
set -euo pipefail  # Exit on error, undefined variables, and pipe failures
# 强制全部为英文
export LANG=C


# Define system commands to execute (using simple arrays for compatibility)
COMMAND_NAMES=(
    "df -Th |egrep -v 'overlay|tmpfs|nfs'"
    "top -b -n 1|head -6"
    "free -h"
    "ps -ef|grep mysql"
)

COMMAND_EXECS=(
    "df -Th |egrep -v 'overlay|tmpfs|nfs'"
    "top -b -n 1 | head -6"
    "free -h"
    "ps -ef | grep mysql | grep -v grep"
)


# Global variables
TMP_FILE=""
IP_ADDRESS=""
PS1_VALUE=""
PROJECT_ID=""
SERVER_URL=""




# =============================================================================
# Utility Functions
# =============================================================================

# Initialize script environment
init_script() {
    TMP_FILE=$(mktemp)
    trap 'cleanup_and_exit' EXIT
}

# Cleanup function
cleanup_and_exit() {
    [[ -f "$TMP_FILE" ]] && rm -f "$TMP_FILE"
}

# Enhanced JSON escape function
escape_json() {
    local input="$1"
    
    # Handle special characters in proper order (backslash first)
    input="${input//\\/\\\\}"   # Backslash -> \\
    input="${input//\"/\\\"}"   # Double quote -> \"
    input="${input//$'\t'/\\t}" # Tab -> \t
    input="${input//$'\n'/\\n}" # Newline -> \n
    input="${input//$'\r'/\\r}" # Carriage return -> \r
    
    echo "$input"
}

# Safe command execution with error handling and return code capture
execute_command() {
    local cmd="$1"
    local default_msg="${2:-Command execution failed}"
    local result
    local return_code
    
    # Execute command and capture both output and return code
    result=$(eval "$cmd" 2>&1)
    return_code=$?
    
    # If command failed or output is empty, use default message
    if [[ $return_code -ne 0 || -z "$result" ]]; then
        [[ -z "$result" ]] && result="$default_msg"
    fi
    
    # Return both output and return code in a format we can parse
    echo "${return_code}|${result}"
}

# =============================================================================
# System Information Collection Functions
# =============================================================================

# Get network IP address with fallback methods
get_ip_address() {
    local ip=""

    # Method 1: macOS - use route and ifconfig
    if [[ "$(uname)" == "Darwin" ]]; then
        ip=$(ifconfig | awk '/inet / && !/127.0.0.1/ {print $2; exit}')
    fi

    # Method 2: Linux - use hostname -I
    if [[ -z "$ip" ]]; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi

    # Method 3: Linux - use ip route with awk (compatible)
    if [[ -z "$ip" ]]; then
        ip=$(ip route get 8.8.8.8 2>/dev/null | awk '/src/ {for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}' | head -1)
    fi

    # Method 4: Use route and ifconfig
    if [[ -z "$ip" ]]; then
        local default_interface
        default_interface=$(route -n 2>/dev/null | grep '^0.0.0.0' | awk '{print $8}' | head -1)
        if [[ -n "$default_interface" ]]; then
            ip=$(ifconfig "$default_interface" 2>/dev/null | awk '/inet / && !/127.0.0.1/ {gsub(/addr:/,"",$2); print $2; exit}')
        fi
    fi

    echo "${ip:-unknown}"
}

# Get PS1 value with multiple fallback methods
get_ps1_value() {
    local ps1
    
    # Method 1: Current PS1 from interactive bash
    ps1=$(bash -i -c 'echo "$PS1"' 2>/dev/null)
    
    # Method 2: From environment
    if [[ -z "$ps1" && -n "${PS1:-}" ]]; then
        ps1="$PS1"
    fi
    
    # Method 3: From configuration files
    if [[ -z "$ps1" ]]; then
        if [[ -f "$HOME/.bashrc" ]]; then
            ps1=$(grep -m1 '^PS1=' "$HOME/.bashrc" 2>/dev/null | cut -d '=' -f2- | sed 's/^"//;s/"$//;s/^'\''//;s/'\''$//')
        elif [[ -f "$HOME/.bash_profile" ]]; then
            ps1=$(grep -m1 '^PS1=' "$HOME/.bash_profile" 2>/dev/null | cut -d '=' -f2- | sed 's/^"//;s/"$//;s/^'\''//;s/'\''$//')
        fi
    fi
    
    # Default fallback
    echo "${ps1:-\\u@\\h:\\w\\$ }"
}

# Collect environment variables
collect_env_data() {
    local env_json
    
    env_json="{"
    env_json="$env_json\"USER\": \"$(escape_json "$(whoami)")\","
    env_json="$env_json\"PWD\": \"$(escape_json "$(pwd)")\","
    env_json="$env_json\"HOME\": \"$(escape_json "$HOME")\","
    env_json="$env_json\"HOSTNAME\": \"$(escape_json "$(hostname)")\","
    env_json="$env_json\"UID\": \"$(escape_json "${UID:-$(id -u)}")\","
    env_json="$env_json\"HISTORY\": \"1\","
    env_json="$env_json\"CMD_NUM\": \"1\","
    env_json="$env_json\"SHELL\": \"$(escape_json "$SHELL")\","
    env_json="$env_json\"BASH_VERSION\": \"$(escape_json "$(bash --version 2>/dev/null | head -n 1 | awk '{print $4}' || echo 'unknown')")\","
    env_json="$env_json\"BASH_RELEASE\": \"$(escape_json "$(bash --version 2>/dev/null | head -n 1 | awk '{print $4}' || echo 'unknown')")\","
    env_json="$env_json\"PS1\": \"$(escape_json "$PS1_VALUE")\""
    env_json="$env_json}"
    
    echo "$env_json"
}



# Collect command execution results
collect_commands_data() {
    local commands_json="{"
    local first=true
    local i cmd_name cmd_exec cmd_result return_code output escaped_output

    for i in "${!COMMAND_NAMES[@]}"; do
        cmd_name="${COMMAND_NAMES[$i]}"
        cmd_exec="${COMMAND_EXECS[$i]}"

        # Add comma separator except for first item
        [[ "$first" == "false" ]] && commands_json="$commands_json,"
        first=false

        cmd_result=$(execute_command "$cmd_exec" "Command failed: $cmd_name")

        # Parse return code and output
        return_code="${cmd_result%%|*}"
        output="${cmd_result#*|}"

        # Escape output for JSON
        escaped_output=$(escape_json "$output")

        # Build JSON structure for this command
        commands_json="$commands_json\"$cmd_name\": {"
        commands_json="$commands_json\"command\": \"$(escape_json "$cmd_exec")\","
        commands_json="$commands_json\"return_code\": $return_code,"
        commands_json="$commands_json\"output\": \"$escaped_output\""
        commands_json="$commands_json}"
    done

    commands_json="$commands_json}"
    echo "$commands_json"
}

# Collect system metadata
collect_metadata() {
    local metadata_json
    
    metadata_json="{"
    metadata_json="$metadata_json\"project_id\": \"$PROJECT_ID\",\"ip\": \"$IP_ADDRESS\","
    metadata_json="$metadata_json\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
    metadata_json="$metadata_json\"hostname\": \"$(escape_json "$(hostname)")\","
    metadata_json="$metadata_json\"os\": \"$(uname -s)\","
    metadata_json="$metadata_json\"kernel\": \"$(uname -r)\","
    metadata_json="$metadata_json\"arch\": \"$(uname -m)\"}"
    
    echo "$metadata_json"
}

# =============================================================================
# Main Execution Functions
# =============================================================================

# Initialize all required data
init_data() {
    # Get server_url from first argument, project_id from second
    SERVER_URL="${1:-}"
    PROJECT_ID="${2:-}"

    # Validate required parameters
    if [[ -z "$SERVER_URL" ]]; then
        echo "Error: Server URL is required" >&2
        echo "Usage: $0 <server_url> <project_id>" >&2
        exit 1
    fi

    if [[ -z "$PROJECT_ID" ]]; then
        echo "Error: Project ID is required" >&2
        echo "Usage: $0 <server_url> <project_id>" >&2
        exit 1
    fi

    IP_ADDRESS=$(get_ip_address)
    PS1_VALUE=$(get_ps1_value)
}

# Generate final JSON output
generate_output() {
    local env_data commands_data metadata_data final_output

    echo "# Collecting environment data..." >&2
    env_data=$(collect_env_data)

    echo "# Collecting command execution results..." >&2
    commands_data=$(collect_commands_data)

    echo "# Collecting system metadata..." >&2
    metadata_data=$(collect_metadata)

    # Combine all data into final JSON structure
    final_output="{"
    final_output="$final_output\"data\": {"
    final_output="$final_output\"env\": $env_data,"
    final_output="$final_output\"commands\": $commands_data"
    final_output="$final_output},"
    final_output="$final_output\"metadata\": $metadata_data"
    final_output="$final_output}"

    echo "$final_output"
}

# Upload data to server
upload_to_server() {
    local json_data="$1"
    local api_url="${SERVER_URL}/api/v1/inspections"

    echo "# Uploading to server: $api_url" >&2

    local response
    local http_code

    # Use curl to upload, capture response and http code
    response=$(curl -s -w "\n%{http_code}" -X POST "$api_url" \
        -H "Content-Type: application/json" \
        -d "$json_data" 2>&1)

    http_code=$(echo "$response" | tail -n1)
    response=$(echo "$response" | sed '$d')

    if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
        echo "# Upload successful (HTTP $http_code)" >&2
        echo "$response"
        return 0
    else
        echo "# Upload failed (HTTP $http_code)" >&2
        echo "# Response: $response" >&2
        return 1
    fi
}

# =============================================================================
# Main Script Execution
# =============================================================================

main() {
    echo "# Starting system information collection..." >&2

    # Initialize script environment
    init_script

    # Initialize required data with command line arguments
    init_data "$@"

    # Generate JSON data
    local json_data
    json_data=$(generate_output)

    # Upload to server
    upload_to_server "$json_data"

    echo "# System information collection completed." >&2
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
