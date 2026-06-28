#!/usr/bin/env python3
"""
Statusline Setup Script
Handles statusline configuration for Claude Code
"""

import json
import os
import shutil
import sys
from pathlib import Path

# Configuration
STATUSLINE_DIR = Path.home() / '.claude'
SCRIPT_FILE = STATUSLINE_DIR / 'statusline-custom.sh'
SETTINGS_FILE = STATUSLINE_DIR / 'settings.json'
THEMES_DIR = STATUSLINE_DIR / 'statusline-themes'
BACKUP_FILE = STATUSLINE_DIR / 'statusline-backup.sh'

# ANSI colors
COLORS = {
    'red': '\033[38;2;245;34;45m',
    'green': '\033[38;2;82;196;26m',
    'yellow': '\033[38;2;250;219;20m',
    'blue': '\033[38;2;94;163;255m',
    'orange': '\033[38;2;250;140;22m',
    'cyan': '\033[38;2;19;194;194m',
    'pink': '\033[38;2;255;20;147m',
    'reset': '\033[0m'
}

# Built-in themes
THEMES = {
    'classic': '🤖 {model} | 📁 {dir} | ⚡️ {ctx}% · {tokens} | 🌿 {branch}',
    'minimal': '[{model}] {dir} {branch} ⚡ {ctx}%',
    'developer': '[{model}] ~/{dir} ({branch}) ⚡ {ctx}% · {tokens_k}',
    'power': '🚀 {model} | 📂 {dir} | 🔋 {ctx}% | 🌿 {branch} | 💰 ${cost}'
}

def load_json_data():
    """Load JSON data from stdin"""
    return json.load(sys.stdin)

def format_tokens(tokens):
    """Format token count with k suffix if >= 1000"""
    if not tokens:
        return "n/a"
    tokens = int(tokens)
    if tokens >= 1000:
        return f"{tokens/1000:.1f}k tokens"
    return f"{tokens} tokens"

def get_git_branch(cwd):
    """Get git branch if in git repo"""
    if not cwd or not os.path.exists(cwd):
        return ""
    try:
        import subprocess
        result = subprocess.run(
            ['git', '-C', cwd, 'symbolic-ref', '--short', 'HEAD'],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except:
        return ""

def apply_colors(text):
    """Apply color codes to text"""
    for color, code in COLORS.items():
        text = text.replace(f'{{{color}}}', code)
    return text

def render_template(template, data):
    """Render template with data and colors"""
    # Replace variables
    template = template.replace('{model}', apply_colors(data.get('model', {}).get('display_name', 'unknown')))
    template = template.replace('{dir}', apply_colors(os.path.basename(data.get('workspace', {}).get('current_dir', ''))))
    template = template.replace('{full_dir}', apply_colors(data.get('workspace', {}).get('current_dir', '')))

    # Context window
    ctx_data = data.get('context_window', {})
    ctx_pct = ctx_data.get('used_percentage', 'n/a')
    template = template.replace('{ctx}', apply_colors(str(int(float(ctx_pct)) if ctx_pct != 'n/a' else 'n/a')))
    template = template.replace('{ctx_percent}', apply_colors(str(int(float(ctx_pct)) if ctx_pct != 'n/a' else 'n/a')))

    # Tokens
    tokens = ctx_data.get('total_input_tokens', '')
    template = template.replace('{tokens}', apply_colors(str(tokens)))
    template = template.replace('{tokens_k}', apply_colors(format_tokens(tokens)))

    # Git branch
    cwd = data.get('workspace', {}).get('current_dir', '')
    branch = get_git_branch(cwd)
    template = template.replace('{branch}', apply_colors(branch))

    # Cost
    cost = data.get('cost', {}).get('total_cost_usd', '0.00')
    template = template.replace('{cost}', apply_colors(f"${cost}"))
    template = template.replace('{cost_usd}', apply_colors(f"${cost}"))

    # Duration
    duration = data.get('cost', {}).get('total_duration_ms', '0')
    template = template.replace('{duration}', apply_colors(str(duration)))
    template = template.replace('{duration_ms}', apply_colors(str(duration)))

    # Version
    version = data.get('version', 'unknown')
    template = template.replace('{version}', apply_colors(version))

    # Add reset at the end if colors were applied
    if any(f'{{{c}}}' in template for c in COLORS):
        template += COLORS['reset']

    return template

def create_theme_script(theme_name, template):
    """Create a theme script file"""
    theme_file = THEMES_DIR / f"{theme_name}.sh"

    script = f'''#!/usr/bin/env bash
# Auto-generated statusline script for {theme_name}

input=$(cat)

# Extract data
model=$(echo "$input" | jq -r '.model.display_name // "unknown"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // ""')
dir=$(basename "$cwd")
ctx_pct=$(echo "$input" | jq -r '.context_window.used_percentage // "n/a"')
tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // ""')
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // "0.00"')
version=$(echo "$input" | jq -r '.version // "unknown"')

# Format tokens
if [ "$tokens" != "" ] && [ "$tokens" -ge 1000 ]; then
    tokens_k=$(awk "BEGIN {{ printf \"%.1fk tokens\", $tokens / 1000 }}")
else
    tokens_k="$tokens tokens"
fi

# Get git branch
branch=""
if [ -n "$cwd" ] && [ -d "$cwd" ]; then
    branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null || true)
fi

# Color codes
'''

    for color, code in COLORS.items():
        script += f"{color.upper()}='{code}'\n"

    script += '''
# Apply template
template="''' + template + '''"
output="$(echo "$template" | sed -e "s/{model}/$(printf "%s" "$model")/g" \\
                                  -e "s/{dir}/$(printf "%s" "$dir")/g" \\
                                  -e "s/{full_dir}/$(printf "%s" "$cwd")/g" \\
                                  -e "s/{ctx}/$(printf "%s" "$ctx_pct")/g" \\
                                  -e "s/{ctx_percent}/$(printf "%s" "$ctx_pct")/g" \\
                                  -e "s/{tokens}/$(printf "%s" "$tokens")/g" \\
                                  -e "s/{tokens_k}/$(printf "%s" "$tokens_k")/g" \\
                                  -e "s/{branch}/$(printf "%s" "$branch")/g" \\
                                  -e "s/{cost}/$(printf "%s" "$cost")/g" \\
                                  -e "s/{cost_usd}/$(printf "%s" "$cost")/g" \\
                                  -e "s/{duration}/$(printf "%s" "0")/g" \\
                                  -e "s/{duration_ms}/$(printf "%s" "0")/g" \\
                                  -e "s/{version}/$(printf "%s" "$version")/g")"

echo -e "$output"
'''

    with open(theme_file, 'w') as f:
        f.write(script)

    os.chmod(theme_file, 0o755)

def apply_theme(theme_name):
    """Apply a built-in theme"""
    if theme_name not in THEMES:
        print(f"Error: Theme '{theme_name}' not found")
        print("Available themes:", ', '.join(THEMES.keys()))
        return False

    # Create theme script
    create_theme_script(theme_name, THEMES[theme_name])

    # Copy to main script
    shutil.copy(THEMES_DIR / f"{theme_name}.sh", SCRIPT_FILE)

    # Update settings
    update_settings()

    return True

def create_custom_template(template):
    """Create a custom statusline script"""
    theme_file = THEMES_DIR / "custom.sh"

    script = f'''#!/usr/bin/env bash
# Custom statusline script

input=$(cat)

# Extract data
model=$(echo "$input" | jq -r '.model.display_name // "unknown"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // ""')
dir=$(basename "$cwd")
ctx_pct=$(echo "$input" | jq -r '.context_window.used_percentage // "n/a"')
tokens=$(echo "$input" | jq -r '.context_window.total_input_tokens // ""')
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // "0.00"')
version=$(echo "$input" | jq -r '.version // "unknown"')

# Format tokens
if [ "$tokens" != "" ] && [ "$tokens" -ge 1000 ]; then
    tokens_k=$(awk "BEGIN {{ printf \"%.1fk tokens\", $tokens / 1000 }}")
else
    tokens_k="$tokens tokens"
fi

# Get git branch
branch=""
if [ -n "$cwd" ] && [ -d "$cwd" ]; then
    branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null || true)
fi

# Color codes
'''

    for color, code in COLORS.items():
        script += f"{color.upper()}='{code}'\n"

    script += f'''
# Apply custom template
template="{template}"
output="$(echo "$template" | sed -e "s/{{model}}/$(printf "%s" "$model")/g" \\
                                  -e "s/{{dir}}/$(printf "%s" "$dir")/g" \\
                                  -e "s/{{full_dir}}/$(printf "%s" "$cwd")/g" \\
                                  -e "s/{{ctx}}/$(printf "%s" "$ctx_pct")/g" \\
                                  -e "s/{{ctx_percent}}/$(printf "%s" "$ctx_pct")/g" \\
                                  -e "s/{{tokens}}/$(printf "%s" "$tokens")/g" \\
                                  -e "s/{{tokens_k}}/$(printf "%s" "$tokens_k")/g" \\
                                  -e "s/{{branch}}/$(printf "%s" "$branch")/g" \\
                                  -e "s/{{cost}}/$(printf "%s" "$cost")/g" \\
                                  -e "s/{{cost_usd}}/$(printf "%s" "$cost")/g" \\
                                  -e "s/{{duration}}/$(printf "%s" "0")/g" \\
                                  -e "s/{{duration_ms}}/$(printf "%s" "0")/g" \\
                                  -e "s/{{version}}/$(printf "%s" "$version")/g")"

echo -e "$output"
'''

    with open(theme_file, 'w') as f:
        f.write(script)

    os.chmod(theme_file, 0o755)

    # Copy to main script
    shutil.copy(theme_file, SCRIPT_FILE)

    # Update settings
    update_settings()

def update_settings():
    """Update settings.json with new statusline configuration"""
    if SETTINGS_FILE.exists():
        # Backup existing
        shutil.copy(SETTINGS_FILE, SETTINGS_FILE.with_suffix('.json.bak'))

        # Load existing settings
        with open(SETTINGS_FILE) as f:
            settings = json.load(f)
    else:
        settings = {}

    # Update statusline config
    settings['statusLine'] = {
        'type': 'command',
        'command': str(SCRIPT_FILE)
    }

    # Write back
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 setup-statusline.py <command> [args]")
        print("\nCommands:")
        print("  init              Initialize statusline configuration")
        print("  theme <name>      Apply a built-in theme")
        print("  custom <tmpl>    Create custom statusline template")
        print("  list              List available themes")
        print("  current           Show current theme")
        print("  test              Test current statusline")
        print("  help              Show this help")
        sys.exit(1)

    cmd = sys.argv[1]

    # Create directories if they don't exist
    THEMES_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_FILE.parent.mkdir(parents=True, exist_ok=True)

    if cmd == 'init':
        # Initialize themes
        for name, template in THEMES.items():
            create_theme_script(name, template)

        # Backup existing script if it exists
        if SCRIPT_FILE.exists():
            shutil.copy(SCRIPT_FILE, BACKUP_FILE)

        update_settings()
        print("Statusline configuration initialized")

    elif cmd == 'theme':
        if len(sys.argv) < 3:
            print("Usage: python3 setup-statusline.py theme <name>")
            print("Available themes:", ', '.join(THEMES.keys()))
            sys.exit(1)

        theme_name = sys.argv[2]
        if apply_theme(theme_name):
            print(f"Applied theme: {theme_name}")

    elif cmd == 'custom':
        if len(sys.argv) < 3:
            print("Usage: python3 setup-statusline.py custom <template>")
            sys.exit(1)

        template = sys.argv[2]
        create_custom_template(template)
        print("Created custom statusline")

    elif cmd == 'list':
        print("Available themes:")
        for name, template in THEMES.items():
            print(f"  {name}: {template}")

    elif cmd == 'current':
        if SCRIPT_FILE.exists():
            print(f"Current script: {SCRIPT_FILE}")
            # Try to detect theme
            if (THEMES_DIR / "classic.sh").exists():
                print("Current theme: classic")
            elif (THEMES_DIR / "minimal.sh").exists():
                print("Current theme: minimal")
            elif (THEMES_DIR / "developer.sh").exists():
                print("Current theme: developer")
            elif (THEMES_DIR / "power.sh").exists():
                print("Current theme: power")
            else:
                print("Current theme: custom")
        else:
            print("No statusline configuration found")

    elif cmd == 'test':
        if SCRIPT_FILE.exists():
            # Test with sample data
            test_data = {
                "model": {"display_name": "Opus"},
                "workspace": {"current_dir": "/test/project"},
                "context_window": {
                    "used_percentage": 75.5,
                    "total_input_tokens": 45000
                },
                "cost": {"total_cost_usd": 0.12},
                "version": "1.0.80"
            }
            print("Testing statusline with sample data:")
            json_input = json.dumps(test_data)
            result = subprocess.run(['bash', str(SCRIPT_FILE)],
                                  input=json_input,
                                  text=True,
                                  capture_output=True)
            if result.returncode == 0:
                print(result.stdout)
            else:
                print("Error:", result.stderr)
        else:
            print("No statusline script found to test")

    elif cmd == 'help':
        print("Usage: python3 setup-statusline.py <command> [args]")
        print("\nCommands:")
        print("  init              Initialize statusline configuration")
        print("  theme <name>      Apply a built-in theme")
        print("  custom <tmpl>    Create custom statusline template")
        print("  list              List available themes")
        print("  current           Show current theme")
        print("  test              Test current statusline")
        print("  help              Show this help")

    else:
        print(f"Unknown command: {cmd}")
        print("Use 'help' for usage")
        sys.exit(1)

if __name__ == '__main__':
    import subprocess
    main()