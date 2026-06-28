# Lessons

记录本项目开发过程中的经验。

## 项目结构

- `SKILL.md` — 技能定义，Claude Code 通过它加载 skill 行为
- `README.md` — 面向用户的说明文档
- `INSTALL.md` — 安装指南
- `scripts/` — 配置脚本，支持 Python 和 Bash 两套实现
- 生成的 statusline 脚本写入 `~/.claude/statusline-command.sh`

## Skills 的加载方式

Claude Code 自动从 `~/.claude/skills/` 子目录加载 skill。每个 skill 目录下有 `SKILL.md` 作为入口，其中包含 frontmatter（name、description、compatibility）。在 Claude Code 中通过 `/skill-name` 调用。

一个 project 级别的 skill（在项目 `.claude/skills/` 下）优先级高于全局的 `~/.claude/skills/`，同名时 project skill 覆盖全局。

## Statusline 要点

### 数据输入

Claude Code 通过 stdin 向 statusline 脚本传入 JSON，关键字段：

| 字段 | 路径 | 说明 |
|------|------|------|
| 模型名 | `.model.display_name` | 如 deepseek-v4-flash |
| 工作目录 | `.workspace.current_dir` 或 `.cwd` | 两者兼容 |
| 上下文用量 | `.context_window.used_percentage` | 百分比 0-100 |
| 输入 token | `.context_window.total_input_tokens` | 数值 |
| 输出 token | `.context_window.total_output_tokens` | 数值 |
| 花费 | `.cost.total_cost_usd` | 浮点数 |
| 时长 | `.cost.total_duration_ms` | 毫秒 |
| 新增/删除行 | `.cost.total_lines_added` / `total_lines_removed` | 数值 |
| 推理力度 | `.effort.level` 或 `.effort` | 字符串或对象 |
| 缓存读取 | `.context_window.current_usage.cache_read_input_tokens` | 数值 |

### Exit Code 陷阱

statusline 脚本**必须以 exit 0 结束**。常见错误：

```bash
# ❌ 错误：当 branch 为空时 [ -n "" ] 返回 false，&& 短路导致 exit 1
[ -n "$line3" ] && printf "%b\n" "$line3"

# ✅ 正确：if 语句保证 eixit 0
if [ -n "$line3" ]; then printf "%b\n" "$line3"; fi
```

### 颜色兼容性

- macOS Terminal.app 不支持 24-bit true color → 推荐 iTerm2
- 终端模拟器需要设置 `TERM=xterm-256color` 或 `tmux-256color`
- 所有颜色使用 `\033[38;2;R;G;Bm` 格式

### 配置方式

在 `~/.claude/settings.json` 中设置：

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash /Users/wangbin/.claude/statusline-command.sh"
  }
}
```

## 调试技巧

1. 写一个缓存脚本截获 Claude Code 传过来的原始 JSON：

```bash
#!/usr/bin/env bash
cat > /tmp/statusline-input.json
```

2. 指向这个脚本，重启 Claude Code，查看 `/tmp/statusline-input.json`
3. 用这份数据离线调试 statusline 脚本

## npx skills 发布

虽然本项目中有 `package.json`，但 skills 不一定要走 npm 发布。推荐方式：

1. GitHub 仓库 → `npx skills add wangbin3162/claude-statusline-config`
2. 需要 `SKILL.md` 在仓库根目录
3. 发布前确认 frontmatter 完整、路径使用 `~/.claude/` 相对路径

## 跨平台注意

- statusline 脚本依赖 bash（macOS 预装）、jq（需安装）、git（需安装）
- `brew install jq` 可补全依赖
- 脚本中避免 Linux-only 命令（如 `awk` 的 GNU 扩展），保证 macOS 兼容
