---
name: statusline-config
description: Configure Claude Code statusline — pick modules, choose layout, preview, and generate the bash script.
compatibility:
  required_tools: [Read, Write, Edit, Bash]
---

# Statusline Configuration Skill

## 定位

引导用户配置 Claude Code 的 statusline：选择要显示的模块、布局行数、之后生成并写入 `settings.json`。

## 当前实现基准

用户目前的 `statusline-command.sh` 是三行布局：

```
🪼 model | 🗂️ dir | 🕐 duration | 🧠 effort
⏳ context: ●●●○○○○○○○ 45% | in: 12.3k | out: 6.8k | 💸 $0.05 | 💾 0%
🍀 branch | ✏️ +10 -3
```

第三行（git 信息）仅在 git 仓库中显示。所有段落在无数据时自动隐藏。

> 技能生成的新脚本以此为基础，用户选择模块后裁剪/重排，而非从零手写。

## 配置流程

```
用户请求 → 加载技能 → 读取当前脚本 → 展示可用模块 → 用户选择 → 预览 → 生成 → 验证
```

## 步骤一：读取当前状态

```bash
# 读取当前脚本
cat ~/.claude/statusline-command.sh 2>/dev/null || echo "无现有脚本"

# 检查 settings.json 中的 statusline 配置
jq '.statusLine' ~/.claude/settings.json
```

告知用户当前已启用什么 layout。

## 步骤二：展示可用模块

向用户展示以下模块，让用户选择**显示哪些**。每个模块有默认，用户可以：

- `✓` 保留 / `✗` 去掉
- 或者直接选一个预设布局

### 模块清单

| # | ID | 模块 | 默认行 | 描述 | 条件 |
|---|-----|------|--------|------|------|
| 1 | `model` | 模型名称 | L1 | 显示当前模型名 (deepseek-v4-flash) | 一直显示 |
| 2 | `dir` | 目录 | L1 | 当前目录 basename | 一直显示 |
| 3 | `duration` | 会话耗时 | L1 | 运行时长 (1m / 2h 30m) | >0 时显示 |
| 4 | `effort` | 推理力度 | L1 | low / medium / high / xhigh / max | 非空时显示 |
| 5 | `context_dots` | 上下文圆点 | L2 | 10 级渐变圆点 ●●●○○○○○○○ | 一直显示 |
| 6 | `context_pct` | 上下文百分比 | L2 | 用量百分比 + 颜色分级 | 一直显示 |
| 7 | `tokens_in` | 输入 Token | L2 | 格式化后的输入 token 数 | 一直显示 |
| 8 | `tokens_out` | 输出 Token | L2 | 格式化后的输出 token 数 | 一直显示 |
| 9 | `cost` | 花费 | L2 | 累计花费 USD | >0 时显示 |
| 10 | `cache` | 缓存命中率 | L2 | Prompt caching 命中率 % | 一直显示 |
| 11 | `branch` | Git 分支 | L3 | 当前 git 分支名 | 仅在 git 仓库 |
| 12 | `diff` | 代码改动 | L3 | +added -removed 行数 | 仅在 git 仓库且改动量>0 |

### 预设布局

直接让用户选一个，省去逐项选择。每个布局下方展示其实际渲染效果（基于示例数据：model=deepseek-v4-flash, dir=project, 45%, 12.3k in/6.8k out, $0.05, git=main, +10/-3）：

**1) 完整三行** (当前默认)
```
🪼 deepseek-v4-flash | 🗂️ project | 🕐 2m | 🧠 high
⏳ context: ●●●●○○○○○○ 45% | in: 12.3k | out: 6.8k | 💸 $0.05 | 💾 0%
🍀 main | ✏️ +10 -3
```

**2) 精简单行**
```
🪼 deepseek-v4-flash | 📁 project | 🌿 main
```

**3) 经典两行**
```
🪼 deepseek-v4-flash | 📁 project | 🕐 2m
⏳ 45% · in: 12.3k · out: 6.8k | 🌿 main
```

**4) 最小信息**
```
🪼 deepseek-v4-flash · 📁 project · ⏳ 45%
```

**5) 开发者**
```
[deepseek-v4-flash] project main ⚡ 45%
```

**6) 全信息**
```
🪼 deepseek-v4-flash | 🗂️ project | 🕐 2m | 🧠 high
⏳ ●●●●○○○○○○ | in: 12.3k | out: 6.8k | 💸 $0.05 | 💾 0%
🍀 main | ✏️ +10 -3
```

## 步骤三：选择布局行数

在模块确定后，让用户选择分几行：

- **1 行** — 紧凑，所有模块塞一行
- **2 行** — 均衡，按分界线拆两组
- **3 行** — 宽松，当前方式

如果用户选的模块少于 4 个，推荐 1 行。如果选了 git 模块，推荐至少 2 行。

## 步骤四：预览

用示例输入模拟渲染，展示给用户确认。

生成命令：

```bash
# 用一份示例 JSON 测试新脚本
echo '{"model":{"display_name":"deepseek-v4-flash"},"workspace":{"current_dir":"/Users/wangbin/project"},"context_window":{"used_percentage":45,"total_input_tokens":12345,"total_output_tokens":6789},"cost":{"total_cost_usd":0.05,"total_duration_ms":120000,"total_lines_added":10,"total_lines_removed":3},"effort":{"level":"high"},"version":"1.0"}' | bash ~/.claude/statusline-command.sh
```

展示输出给用户，确认要写入。

> 注意：预览在终端中执行，ANSI 颜色码会直接转义。向用户展示纯文本版本或提示 "颜色码已生效"。

## 步骤五：生成脚本

根据用户选择的模块，拼接新的 `statusline-command.sh`。

### 脚本结构模板

固定部分（不随选择变）：

```bash
#!/usr/bin/env bash
input=$(cat)

# === 数据解析 ===
declare -a fields=()
while IFS= read -r val; do fields+=("$val"); done < <(
  echo "$input" | jq -r '[
    .model.display_name // "unknown",
    (.workspace.current_dir // .cwd // ""),
    (.context_window.used_percentage // "n/a"),
    (.context_window.total_input_tokens // 0),
    (.context_window.total_output_tokens // 0),
    (.cost.total_cost_usd // 0),
    (.cost.total_duration_ms // 0),
    (.cost.total_lines_added // 0),
    (.cost.total_lines_removed // 0),
    (.effort | if type == "object" then .level else . end) // "",
    (.context_window.current_usage.cache_read_input_tokens // 0)
  ] | .[]'
)
model="${fields[0]}"
cwd_dir="${fields[1]}"
used_pct="${fields[2]}"
total_input="${fields[3]}"
total_output="${fields[4]}"
cost_usd="${fields[5]}"
duration_ms="${fields[6]}"
lines_added="${fields[7]}"
lines_removed="${fields[8]}"
effort_level="${fields[9]}"
cache_read="${fields[10]}"
dir=$(basename "$cwd_dir")
```

颜色定义（24-bit true color），全量保留，脚本中用到的就保留：

```bash
RESET='\033[0m'
LIGHT_BLUE='\033[38;2;94;163;255m'  # model
DIR_COLOR='\033[38;2;250;140;22m'    # directory
GREEN='\033[38;2;82;196;26m'         # ok / added
ORANGE='\033[38;2;250;140;22m'       # warning
RED='\033[38;2;245;34;45m'           # danger
SOFT_RED='\033[38;2;245;110;110m'    # removed
YELLOW='\033[38;2;250;219;20m'       # cost
BRANCH_COLOR='\033[38;2;19;194;194m' # git branch
DIM_GRAY='\033[38;2;67;67;67m'       # unused dots
CYAN='\033[38;2;0;204;204m'          # duration
LABEL='\033[38;2;120;120;120m'       # labels
CACHE_COLOR='\033[38;2;0;217;130m'   # cache
LIGHT_PURPLE='\033[38;2;180;130;255m'# effort high
PURPLE='\033[38;2;139;92;246m'       # effort xhigh
PINK='\033[38;2;255;105;180m'        # effort max
```

### 模块代码段

每个模块对应一段代码，根据用户选择**拼入或跳过**：

#### model_segment
```bash
model_seg=$(printf "${LIGHT_BLUE}%s${RESET}" "$model")
```

#### dir_segment
```bash
dir_seg=$(printf "${DIR_COLOR}%s${RESET}" "$dir")
```

#### duration_segment
```bash
duration_fmt=""
if [ -n "$duration_ms" ] && [ "$duration_ms" -gt 0 ]; then
  if [ "$duration_ms" -lt 60000 ]; then duration_fmt="<1m"
  else
    mins=$(( duration_ms / 60000 ))
    if [ "$mins" -ge 60 ]; then
      hours=$(( mins / 60 )); rem_mins=$(( mins % 60 ))
      duration_fmt="${hours}h${rem_mins:+ }${rem_mins}m"
    else duration_fmt="${mins}m"; fi
  fi
fi
duration_seg=""
[ -n "$duration_fmt" ] && duration_seg=$(printf " | 🕐 ${CYAN}%s${RESET}" "$duration_fmt")
```

#### effort_segment
```bash
effort_seg=""
if [ -n "$effort_level" ]; then
  case "$effort_level" in
    low)    ec="$YELLOW" ;;
    medium) ec="$GREEN" ;;
    high)   ec="$LIGHT_PURPLE" ;;
    xhigh)  ec="$PURPLE" ;;
    max)    ec="$PINK" ;;
    *)      ec="$DIM_GRAY" ;;
  esac
  effort_seg=$(printf " | 🧠 ${ec}%s${RESET}" "$effort_level")
fi
```

#### context_dots_segment（L2）
```bash
DOT_COLORS=(
  '\033[38;2;76;175;80m' '\033[38;2;121;187;76m' '\033[38;2;166;199;72m'
  '\033[38;2;210;211;67m' '\033[38;2;255;223;63m' '\033[38;2;255;200;31m'
  '\033[38;2;255;160;0m' '\033[38;2;250;113;27m' '\033[38;2;244;67;54m'
  '\033[38;2;183;28;28m'
)
if [ -n "$used_pct" ] && [ "$used_pct" != "n/a" ]; then
  pct_int=$(printf "%.0f" "$used_pct"); filled=$(( pct_int / 10 )); rem_val=$(( pct_int % 10 ))
  bar=""; for ((i=0; i<10; i++)); do
    if [ "$i" -lt "$filled" ]; then bar+="${DOT_COLORS[$i]}●${RESET}"
    elif [ "$i" -eq "$filled" ] && [ "$rem_val" -gt 0 ]; then bar+="${DOT_COLORS[$i]}●${RESET}"
    else bar+="${DIM_GRAY}○${RESET}"; fi
  done
else
  bar=""; for ((i=0; i<10; i++)); do bar+="${DIM_GRAY}○${RESET}"; done
fi
```

#### context_pct_segment
```bash
if [ -n "$used_pct" ] && [ "$used_pct" != "n/a" ]; then
  pct_int=$(printf "%.0f" "$used_pct")
  if [ "$pct_int" -ge 80 ]; then ctx_c="$RED"
  elif [ "$pct_int" -ge 50 ]; then ctx_c="$ORANGE"
  else ctx_c="$GREEN"; fi
  ctx_pct_seg=$(printf "${ctx_c}%d%%${RESET}" "$pct_int")
fi
```

#### tokens_in/tokens_out_segments
```bash
fmt_tok() {
  local n=$1
  [ -z "$n" ] && echo "0" && return
  if [ "$n" -ge 1000000 ]; then awk "BEGIN { printf \"%.1fM\", $n / 1000000 }"
  elif [ "$n" -ge 1000 ]; then awk "BEGIN { printf \"%.1fk\", $n / 1000 }"
  else printf "%s" "$n"; fi
}
in_fmt=$(fmt_tok "$total_input"); out_fmt=$(fmt_tok "$total_output")
```

#### cost_segment
```bash
cost_seg=""
if [ -n "$cost_usd" ] && [ "$(awk "BEGIN { print ($cost_usd > 0) ? 1 : 0 }")" = "1" ]; then
  cost_seg=$(printf " | ${YELLOW}💸 \$%.2f${RESET}" "$cost_usd")
fi
```

#### cache_segment
```bash
if [ -n "$total_input" ] && [ "$total_input" -gt 0 ]; then
  cache_pct=$(awk "BEGIN { p=int($cache_read*100/$total_input); if(p>100)p=100; print p }")
else cache_pct=0; fi
cache_seg=$(printf "${CACHE_COLOR}💾 %s%%${RESET}" "$cache_pct")
```

#### branch_segment
```bash
branch=""
if [ -n "$cwd_dir" ] && [ -d "$cwd_dir" ]; then
  branch=$(git -C "$cwd_dir" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
fi
[ -n "$branch" ] && branch_seg=$(printf "${BRANCH_COLOR}%s${RESET}" "$branch")
```

#### diff_segment
```bash
diff_seg=""
if [ -n "$branch" ]; then
  if [ "$lines_added" -gt 0 ] || [ "$lines_removed" -gt 0 ]; then
    a_seg=$(printf "${GREEN}+%s${RESET}" "$lines_added")
    r_seg=$(printf "${SOFT_RED}-%s${RESET}" "$lines_removed")
    diff_seg=$(printf " | ✏️ ${a_seg} ${r_seg}")
  fi
fi
```

### 拼装输出

根据行数选择，拼接 `line1`、`line2`、`line3` 变量：

```bash
# === 1 行 ===
line1="🪼 ${model_seg} | 🗂️ ${dir_seg}${duration_seg}${effort_seg}${context_part} | ${tokens_part}${cost_seg} | ${cache_part}"
[ -n "$branch_seg" ] && line1+=" | 🍀 ${branch_seg}${diff_seg}"
printf "%b\n" "$line1"

# === 2 行 ===
line1="🪼 ${model_seg} | 🗂️ ${dir_seg}${duration_seg}${effort_seg}"
line2="${ctx_part} | ${tokens_part}${cost_seg} | ${cache_part}"
[ -n "$branch_seg" ] && line2+=" | 🍀 ${branch_seg}${diff_seg}"
printf "%b\n" "$line1"
printf "%b\n" "$line2"

# === 3 行 ===
line1="🪼 ${model_seg} | 🗂️ ${dir_seg}${duration_seg}${effort_seg}"
line2="${ctx_part} | ${tokens_part}${cost_seg} | ${cache_part}"
line3=""
[ -n "$branch_seg" ] && line3="🍀 ${branch_seg}${diff_seg}"
printf "%b\n" "$line1"
printf "%b\n" "$line2"
if [ -n "$line3" ]; then printf "%b\n" "$line3"; fi
```

**关键规则**：
- `if [ -n "$line3" ]; then printf "%b\n" "$line3"; fi` — 必须以 `if` 而非 `&&` 结束，保证非 git 目录下 exit code 0。
- 所有条件段落在数据为空时自动隐藏（`-n "$var"` 检查）。
- 颜色变量只保留被选中模块需要用到的。

## 步骤六：写入并配置

```bash
# 写入脚本
cp /dev/null ~/.claude/statusline-command.sh   # 清空
# 用 Write 工具写入

# 确认 settings.json 指向正确
jq '.statusLine' ~/.claude/settings.json
# 期待: {"type": "command", "command": "bash /Users/wangbin/.claude/statusline-command.sh"}

# 如果 settings.json 没有 statusLine 配置，添加：
# jq '.statusLine = {"type":"command","command":"bash ~/.claude/statusline-command.sh"}' ~/.claude/settings.json
```

## 步骤七：验证

```bash
# 1) 非 git 目录测试
echo '{"model":{"display_name":"deepseek-v4-flash"},"workspace":{"current_dir":"/Users/wangbin"},"context_window":{"used_percentage":45,"total_input_tokens":12345,"total_output_tokens":6789},"cost":{"total_cost_usd":0.05,"total_duration_ms":120000,"total_lines_added":0,"total_lines_removed":0},"effort":{"level":"high"},"version":"1.0"}' | bash ~/.claude/statusline-command.sh; echo "exit: $?"

# → 必须有输出，exit code 0，没有 git 行

# 2) git 目录测试
cd /tmp && git init test-statusline 2>/dev/null && cd /tmp/test-statusline && echo '{"model":{"display_name":"deepseek-v4-flash"},"workspace":{"current_dir":"/tmp/test-statusline"},"context_window":{"used_percentage":45,"total_input_tokens":12345,"total_output_tokens":6789},"cost":{"total_cost_usd":0.05,"total_duration_ms":120000,"total_lines_added":10,"total_lines_removed":3},"effort":{"level":"high"},"version":"1.0"}' | bash ~/.claude/statusline-command.sh; echo "exit: $?"

# → 必须三行完整，exit code 0
```

清理临时目录：
```bash
rm -rf /tmp/test-statusline
```

## 常见问题

### statusline 不显示

1. **exit code 非 0** — 以 `[ -n "$var" ] && ...` 结尾的脚本在 false 时 exit 1。必须改用 `if [ -n "$var" ]; then ...; fi` 包裹。
2. **jq 路径不对** — Claude Code 传给 statusline 脚本的 JSON 可能版本不同。用 `cat` 调试（见下方）。
3. **脚本不可执行** — 虽然 `settings.json` 里是 `bash ~/.claude/statusline-command.sh`，更安全的是 `chmod +x`。

### 调试方法

```bash
# 查看 Claude Code 实际传了什么给 statusline
# 方法：写一个日志脚本
cat > /tmp/debug-statusline.sh << 'EOF'
#!/usr/bin/env bash
cat > /tmp/statusline-input.json
EOF
chmod +x /tmp/debug-statusline.sh
# 然后把 settings.json 的 command 指向这个
# restart claude, 然后 cat /tmp/statusline-input.json
```

### 颜色不显示

- Claude Code 终端支持 24-bit true color 时才能显示。
- 确认终端设置：`echo $TERM` 应为 `xterm-256color` 或 `tmux-256color`。
- macOS Terminal.app 默认不支持 24-bit 色，推荐 iTerm2。

## 恢复默认

```bash
# 从 settings.json 删除 statusLine 配置
jq 'del(.statusLine)' ~/.claude/settings.json > ~/.claude/settings.json.tmp && mv ~/.claude/settings.json.tmp ~/.claude/settings.json

# 或备份现有脚本
mv ~/.claude/statusline-command.sh ~/.claude/statusline-command.sh.bak
```

## 快速参考

### 所有可用字段（Claude Code 传递的 JSON）

| JSON 路径 | 变量名 | 用途 |
|-----------|--------|------|
| `.model.display_name` | `$model` | 模型名 |
| `.workspace.current_dir` / `.cwd` | `$cwd_dir` | 工作目录 |
| `.context_window.used_percentage` | `$used_pct` | 上下文用量 % |
| `.context_window.total_input_tokens` | `$total_input` | 输入 token |
| `.context_window.total_output_tokens` | `$total_output` | 输出 token |
| `.cost.total_cost_usd` | `$cost_usd` | 累计花费 |
| `.cost.total_duration_ms` | `$duration_ms` | 会话时长 ms |
| `.cost.total_lines_added` | `$lines_added` | 新增行数 |
| `.cost.total_lines_removed` | `$lines_removed` | 删除行数 |
| `.effort.level` / `.effort` | `$effort_level` | 推理力度 |
| `.context_window.current_usage.cache_read_input_tokens` | `$cache_read` | 缓存读取 token |

### 颜色方案

| 变量名 | 色值 | 用途 |
|--------|------|------|
| `LIGHT_BLUE` | #5EA3FF | 模型名 |
| `DIR_COLOR` | #FA8C16 | 目录 |
| `GREEN` | #52C41A | 正常 / 新增 |
| `ORANGE` | #FA8C16 | 警告 |
| `RED` | #F5222D | 危险 |
| `SOFT_RED` | #F56E6E | 删除行 |
| `YELLOW` | #FADB14 | 花费 |
| `BRANCH_COLOR` | #13C2C2 | Git 分支 |
| `CYAN` | #00CCCC | 时长 |
| `DIM_GRAY` | #434343 | 未用圆点 |
| `LABEL` | #787878 | 标签文本 |
| `CACHE_COLOR` | #00D982 | 缓存 |
| `LIGHT_PURPLE` | #B482FF | effort high |
| `PURPLE` | #8B5CF6 | effort xhigh |
| `PINK` | #FF69B4 | effort max |
