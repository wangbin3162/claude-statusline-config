# Statusline Config Skill

为 Claude Code 配置 statusline 的 skill。基于模块选择生成 bash 脚本，支持预设布局和自定义组合。

## 快速安装

### 方式一：GitHub 安装

```bash
# 直接安装到 Claude Code skills 目录
git clone https://github.com/wangbin3162/claude-statusline-config.git ~/.claude/skills/statusline-config
```

或通过 `npx skills`：

```bash
npx skills add wangbin3162/claude-statusline-config
```

### 方式二：手动复制

```bash
cp -r /path/to/statusline-config ~/.claude/skills/
```

### 方式三：npm

```bash
npm install -g @wangbin3162/statusline-config
npx skills add @wangbin3162/statusline-config
```

## 使用

在 Claude Code 中运行：

```
/statusline-config
```

按提示选择模块和布局行数，skill 会自动生成并写入脚本。

详细安装说明见 [INSTALL.md](INSTALL.md)。

## 预览

6 种预设布局的渲染效果（基于示例数据：model=deepseek-v4-flash, dir=project, 45%, 12.3k in/6.8k out, $0.05, git=main, +10/-3）：

### 完整三行（默认）
```
🪼 deepseek-v4-flash | 🗂️ project | 🕐 2m | 🧠 high
⏳ context: ●●●●○○○○○○ 45% | in: 12.3k | out: 6.8k | 💸 $0.05 | 💾 0%
🍀 main | ✏️ +10 -3
```

### 精简单行
```
🪼 deepseek-v4-flash | 📁 project | 🌿 main
```

### 经典两行
```
🪼 deepseek-v4-flash | 📁 project | 🕐 2m
⏳ 45% · in: 12.3k · out: 6.8k | 🌿 main
```

### 最小信息
```
🪼 deepseek-v4-flash · 📁 project · ⏳ 45%
```

### 开发者
```
[deepseek-v4-flash] project main ⚡ 45%
```

### 全信息
```
🪼 deepseek-v4-flash | 🗂️ project | 🕐 2m | 🧠 high
⏳ ●●●●○○○○○○ | in: 12.3k | out: 6.8k | 💸 $0.05 | 💾 0%
🍀 main | ✏️ +10 -3
```

- 第三行仅在 git 仓库中显示
- 所有段落在无数据时自动隐藏
- 24-bit true color 配色

## 可用模块（12 个）

| # | 模块 | 默认行 | 说明 |
|---|------|--------|------|
| 1 | 模型名 | L1 | 当前模型 |
| 2 | 目录 | L1 | 工作目录 basename |
| 3 | 会话耗时 | L1 | 运行时长 |
| 4 | 推理力度 | L1 | low / high / max |
| 5 | 上下文圆点 | L2 | 10 级渐变 ●●●○○ |
| 6 | 上下文百分比 | L2 | 颜色编码 |
| 7 | 输入 Token | L2 | 格式化计数 |
| 8 | 输出 Token | L2 | 格式化计数 |
| 9 | 花费 | L2 | 累计 USD |
| 10 | 缓存命中率 | L2 | Prompt cache % |
| 11 | Git 分支 | L3 | 仅 git repo |
| 12 | 代码改动 | L3 | +/- 行数 |

## 预设布局

- **完整三行**: model/dir/duration/effort + context/tokens/cost/cache + branch/diff（当前默认）
- **精简单行**: model · dir · branch
- **经典两行**: model/dir/duration + context%/tokens/branch
- **最小信息**: model · dir · context%
- **开发者**: [model] dir branch ⚡ pct%
- **全信息**: model/dir/duration/effort + context/tokens/cost/cache + branch/diff

> 以上布局的完整渲染效果见 [预览](#预览) 章节。

## 验证安装

```bash
# 确认技能已加载
ls ~/.claude/skills/ | grep statusline-config

# 测试 statusline 脚本
echo '{"model":{"display_name":"deepseek-v4-flash"},"workspace":{"current_dir":"/test"},"context_window":{"used_percentage":45,"total_input_tokens":12345,"total_output_tokens":6789},"cost":{"total_cost_usd":0.05,"total_duration_ms":120000,"total_lines_added":10,"total_lines_removed":3},"effort":{"level":"high"}}' | bash ~/.claude/statusline-command.sh
```

## 依赖

- bash
- jq（用于解析 JSON）
- git（可选，用于 git 分支显示）

## 文件结构

```
~/.claude/
├── settings.json                  # 指向 statusline-command.sh
├── statusline-command.sh          # 生成的 statusline 脚本
└── skills/statusline-config/      # 本 skill
    ├── LICENSE
    ├── README.md
    ├── INSTALL.md
    ├── SKILL.md                   # 技能定义
    ├── docs/lessons.md            # 开发经验记录
    └── scripts/
        ├── setup-statusline.py    # Python 配置工具
        └── statusline-manager.sh  # Bash 配置工具
```

## 调试

```bash
# 捕获 Claude Code 实际传入的 JSON
cat > /tmp/debug.sh << 'EOF'
#!/usr/bin/env bash
cat > /tmp/statusline-input.json
EOF
chmod +x /tmp/debug.sh
```

然后将 `settings.json` 的 `command` 改为 `bash /tmp/debug.sh`，重启 claude 后查看 `/tmp/statusline-input.json`。

## 恢复默认

```bash
jq 'del(.statusLine)' ~/.claude/settings.json > ~/.claude/settings.json.tmp && mv ~/.claude/settings.json.tmp ~/.claude/settings.json
```

## 颜色方案

| 用途 | 色值 |
|------|------|
| 模型名 | #5EA3FF |
| 目录 | #FA8C16 |
| 正常 / 新增行 | #52C41A |
| 警告 / 花费 | #FA8C16 / #FADB14 |
| 危险 | #F5222D |
| Git 分支 | #13C2C2 |
| 时长 | #00CCCC |
| 缓存 | #00D982 |
| Effort 级别 | 黄/绿/紫/粉 |

## 许可证

[MIT](LICENSE) © 2025 wangbin3162
