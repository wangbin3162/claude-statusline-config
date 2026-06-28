#!/usr/bin/env bash

# Statusline Manager Script
# Handles statusline configuration and theme management

set -e

# Configuration
STATUSLINE_DIR="$HOME/.claude"
SCRIPT_FILE="$STATUSLINE_DIR/statusline-custom.sh"
SETTINGS_FILE="$STATUSLINE_DIR/settings.json"
THEMES_DIR="$STATUSLINE_DIR/statusline-themes"
BACKUP_FILE="$STATUSLINE_DIR/statusline-backup.sh"

# ANSI colors
RED='\033[38;2;245;34;45m'
GREEN='\033[38;2;82;196;26m'
YELLOW='\033[38;2;250;219;20m'
BLUE='\033[38;2;94;163;255m'
ORANGE='\033[38;2;250;140;22m'
CYAN='\033[38;2;19;194;194m'
PINK='\033[38;2;255;20;147m'
RESET='\033[0m'

# Create themes directory if it doesn't exist
mkdir -p "$THEMES_DIR"

# Define themes
declare -A THEMES=(
    ["classic"]="🤖 {model} | 📁 {dir} | ⚡️ {ctx}% · {tokens} | 🌿 {branch}"
    ["minimal"]="[{model}] {dir} {branch} ⚡ {ctx}%"
    ["developer"]="[{model}] ~/{dir} ({branch}) ⚡ {ctx}% · {tokens_k}"
    ["power"]="🚀 {model} | 📂 {dir} | 🔋 {ctx}% | 🌿 {branch} | 💰 ${cost}"
)

# Initialize or backup existing configuration
init_config() {
    # Backup existing configuration
    if [ -f "$SCRIPT_FILE" ]; then
        cp "$SCRIPT_FILE" "$BACKUP_FILE"
    fi

    # Create themes directory
    mkdir -p "$THEMES_DIR"

    # Create default themes if they don't exist
    for theme in "${!THEMES[@]}"; do
        theme_file="$THEMES_DIR/$theme.sh"
        if [ ! -f "$theme_file" ]; then
            create_theme_script "$theme" "${THEMES[$theme]}"
        fi
    done
}

# Create theme script
create_theme_script() {
    local theme_name="$1"
    local template="$2"
    local theme_file="$THEMES_DIR/$theme_name.sh"

    cat > "$theme_file" << 'EOF'
#!/usr/bin/env bash
# Auto-generated statusline script

input=$(cat)

# Model name
model=$(echo "$input" | jq -r '.model.display_name // "unknown"')

# Directory info
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
dir=$(basename "$cwd")
full_dir="$cwd"

# Context window
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
total_input=$(echo "$input" | jq -r '.context_window.total_input_tokens // empty')
ctx_window=$(echo "$input" | jq -r '.context_window.context_window_size // 0')

# Git branch
branch=""
if [ -n "$cwd" ] && [ -d "$cwd" ]; then
    branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
fi

# Cost and duration
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // "0.00"')
duration=$(echo "$input" | jq -r '.cost.total_duration_ms // "0"')
version=$(echo "$input" | jq -r '.version // "unknown"')

# Format tokens
if [ -n "$total_input" ] && [ "$total_input" -ge 1000 ]; then
    tokens_k=$(awk "BEGIN { printf \"%.1fk tokens\", $total_input / 1000 }")
else
    tokens_k="${total_input} tokens"
fi

# Format context percentage
if [ -n "$used_pct" ]; then
    ctx_pct=$(printf "%.0f" "$used_pct")
else
    ctx_pct="n/a"
fi

# Apply color variables
apply_colors() {
    local text="$1"
    text="${text//\{red\}/$RED}"
    text="${text//\{green\}/$GREEN}"
    text="${text//\{yellow\}/$YELLOW}"
    text="${text//\{blue\}/$BLUE}"
    text="${text//\{orange\}/$ORANGE}"
    text="${text//\{cyan\}/$CYAN}"
    text="${text//\{pink\}/$PINK}"
    text="${text//\{reset\}/$RESET}"
    echo -n "$text"
}

# Replace variables in template
replace_vars() {
    local template="$1"
    template="${template//\{model\}/$(printf "%s" "$(apply_colors "$model")")}"
    template="${template//\{dir\}/$(printf "%s" "$(apply_colors "$dir")")}"
    template="${template//\{full_dir\}/$(printf "%s" "$(apply_colors "$full_dir")")}"
    template="${template//\{ctx\}/$(printf "%s" "$(apply_colors "$ctx_pct")")}"
    template="${template//\{ctx_percent\}/$(printf "%s" "$(apply_colors "$ctx_pct")")}"
    template="${template//\{tokens\}/$(printf "%s" "$(apply_colors "$total_input")")}"
    template="${template//\{tokens_k\}/$(printf "%s" "$(apply_colors "$tokens_k")")}"
    template="${template//\{branch\}/$(printf "%s" "$(apply_color "$branch")")}"
    template="${template//\{cost\}/$(printf "%s" "$(apply_color "$cost")")}"
    template="${template//\{cost_usd\}/$(printf "%s" "$(apply_color "$cost")")}"
    template="${template//\{duration\}/$(printf "%s" "$(apply_color "$duration")")}"
    template="${template//\{duration_ms\}/$(printf "%s" "$(apply_color "$duration")")}"
    template="${template//\{version\}/$(apply_color "$version")}"

    # Remove color reset from the end if present
    if [[ "$template" == *"$RESET"* ]]; then
        # Add reset at the very end
        printf "%s%s" "$template" "$RESET"
    else
        echo "$template"
    fi
}

# Apply theme template
EOF

    # Add the specific theme template
    cat >> "$theme_file" << EOF
template="$template"
output="\$(replace_vars "\$template")"

echo -e "\$output"
EOF

    chmod +x "$theme_file"
}

# Apply theme
apply_theme() {
    local theme_name="$1"
    local theme_file="$THEMES_DIR/$theme_name.sh"

    if [ ! -f "$theme_file" ]; then
        echo "Error: Theme '$theme_name' not found"
        exit 1
    fi

    # Copy theme script to main script
    cp "$theme_file" "$SCRIPT_FILE"

    # Update settings.json
    update_settings
}

# Create custom script
create_custom() {
    local template="$1"

    # Create a custom script file
    cat > "$SCRIPT_FILE" << 'EOF'
#!/usr/bin/env bash
# Custom statusline script

input=$(cat)

# Model name
model=$(echo "$input" | jq -r '.model.display_name // "unknown"')

# Directory info
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
dir=$(basename "$cwd")
full_dir="$cwd"

# Context window
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
total_input=$(echo "$input" | jq -r '.context_window.total_input_tokens // empty')

# Git branch
branch=""
if [ -n "$cwd" ] && [ -d "$cwd" ]; then
    branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
fi

# Cost and duration
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // "0.00"')
duration=$(echo "$input" | jq -r '.cost.total_duration_ms // "0"')

# Format tokens
if [ -n "$total_input" ] && [ "$total_input" -ge 1000 ]; then
    tokens_k=$(awk "BEGIN { printf \"%.1fk tokens\", $total_input / 1000 }")
else
    tokens_k="${total_input} tokens"
fi

# Format context percentage
if [ -n "$used_pct" ]; then
    ctx_pct=$(printf "%.0f" "$used_pct")
else
    ctx_pct="n/a"
fi

# Color codes
EOF

    # Add color codes
    cat >> "$SCRIPT_FILE" << EOF
RED='\033[38;2;245;34;45m'
GREEN='\033[38;2;82;196;26m'
YELLOW='\033[38;2;250;219;20m'
BLUE='\033[38;2;94;163;255m'
ORANGE='\033[38;2;250;140;22m'
CYAN='\033[38;2;19;194;194m'
PINK='\033[38;2;255;20;147m'
RESET='\033[0m'

# Apply colors and template
apply_colors() {
    local text="$1"
    text="${text//\{red\}/$RED}"
    text="${text//\{green\}/$GREEN}"
    text="${text//\{yellow\}/$YELLOW}"
    text="${text//\{blue\}/$BLUE}"
    text="${text//\{orange\}/$ORANGE}"
    text="${text//\{cyan\}/$CYAN}"
    text="${text//\{pink\}/$PINK}"
    text="${text//\{reset\}/$RESET}"
    echo -n "$text"
}

replace_vars() {
    local template="$1"
    template="${template//\{model\}/$(apply_colors "$model")}"
    template="${template//\{dir\}/$(apply_colors "$dir")}"
    template="${template//\{full_dir\}/$(apply_colors "$full_dir")}"
    template="${template//\{ctx\}/$(apply_colors "$ctx_pct")}"
    template="${template//\{ctx_percent\}/$(apply_colors "$ctx_pct")}"
    template="${template//\{tokens\}/$(apply_colors "$total_input")}"
    template="${template//\{tokens_k\}/$(apply_colors "$tokens_k")}"
    template="${template//\{branch\}/$(apply_color "$branch")}"
    template="${template//\{cost\}/$(apply_color "$cost")}"
    template="${template//\{cost_usd\}/$(apply_color "$cost")}"
    template="${template//\{duration\}/$(apply_color "$duration")}"
    template="${template//\{duration_ms\}/$(apply_color "$duration")}"

    # Remove color reset from the end if present
    if [[ "$template" == *"$RESET"* ]]; then
        printf "%s%s" "$template" "$RESET"
    else
        echo "$template"
    fi
}

# Apply custom template
template="$template"
output="\$(replace_vars "\$template")"

echo -e "\$output"
EOF

    chmod +x "$SCRIPT_FILE"
    update_settings
}

# Update settings.json
update_settings() {
    if [ -f "$SETTINGS_FILE" ]; then
        # Backup existing settings
        cp "$SETTINGS_FILE" "$SETTINGS_FILE.bak"

        # Update statusline configuration
        jq --arg script "$SCRIPT_FILE" '
            if .statusLine then
                .statusLine.command = $script
            else
                .statusLine = {
                    "type": "command",
                    "command": $script
                }
            end
        ' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
    else
        # Create new settings file
        cat > "$SETTINGS_FILE" << EOF
{
  "statusLine": {
    "type": "command",
    "command": "$SCRIPT_FILE"
  }
}
EOF
    fi
}

# List available themes
list_themes() {
    echo "Available themes:"
    for theme in "${!THEMES[@]}"; do
        echo "  $theme: ${THEMES[$theme]}"
    done
}

# Show current configuration
show_current() {
    if [ -f "$SCRIPT_FILE" ]; then
        echo "Current statusline script: $SCRIPT_FILE"
        echo "Current theme/template:"
        head -n 20 "$SCRIPT_FILE" | grep -E "template|output" || echo "  Custom template"
    else
        echo "No statusline configuration found"
    fi
}

# Restore backup
restore_backup() {
    if [ -f "$BACKUP_FILE" ]; then
        cp "$BACKUP_FILE" "$SCRIPT_FILE"
        update_settings
        echo "Restored from backup"
    else
        echo "No backup found"
    fi
}

# Main logic
case "${1:-help}" in
    init)
        init_config
        echo "Statusline configuration initialized"
        ;;
    theme)
        if [ -z "$2" ]; then
            echo "Usage: $0 theme <theme-name>"
            list_themes
            exit 1
        fi
        apply_theme "$2"
        echo "Applied theme: $2"
        ;;
    custom)
        if [ -z "$2" ]; then
            echo "Usage: $0 custom <template>"
            exit 1
        fi
        create_custom "$2"
        echo "Created custom statusline"
        ;;
    list)
        list_themes
        ;;
    current)
        show_current
        ;;
    restore)
        restore_backup
        ;;
    test)
        if [ -f "$SCRIPT_FILE" ]; then
            # Test with sample JSON
            echo '{"model":{"display_name":"Opus"},"workspace":{"current_dir":"/test/project"}}' | "$SCRIPT_FILE"
        else
            echo "No statusline script found to test"
        fi
        ;;
    help|--help|-h)
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  init           Initialize statusline configuration"
        echo "  theme <name>   Apply a built-in theme"
        echo "  custom <tmpl>  Create custom statusline template"
        echo "  list           List available themes"
        echo "  current        Show current configuration"
        echo "  restore        Restore from backup"
        echo "  test           Test current statusline"
        echo "  help           Show this help message"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage"
        exit 1
        ;;
esac