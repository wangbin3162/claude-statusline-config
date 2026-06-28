# Statusline Config Skill

为 Claude Code 配置 statusline 的 skill。基于模块选择生成 bash 脚本，支持预设布局和自定义组合。

## 当前实现

三行信息布局（可裁剪为 1 行 / 2 行）：

```
🪼 model | 🗂️ dir | 🕐 duration | 🧠 effort
⏳ context: ●●●○○○○○○○ 45% | in: 12.3k | out: 6.8k | 💸 $0.05 | 💾 0%
🍀 branch | ✏️ +10 -3
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

- **精简单行**: model · dir · branch
- **经典两行**: model/dir/duration + context%/tokens/branch
- **完整三行**: 当前配置（默认）
- **最小信息**: model · dir · context%
- **开发者**: [model] dir branch ⚡ pct%
- **全信息**: model/dir/duration/effort + context/tokens/cost/cache + branch/diff

## 使用

在 Claude Code 中运行：

```
/statusline-config
```

按提示选择模块和布局行数，skill 会自动生成并写入脚本。

## 文件结构

```
~/.claude/
├── settings.json                  # 指向 statusline-command.sh
├── statusline-command.sh          # 生成的 statusline 脚本
└── skills/statusline-config/      # 本 skill
    ├── README.md
    ├── INSTALL.md
    ├── SKILL.md                   # 技能定义
    └── scripts/
        ├── setup-statusline.py    # Python 配置工具
        └── statusline-manager.sh  # Bash 配置工具
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

## 常见问题

### 不显示

确保脚本以 exit 0 结束。非 git 目录下最后一行需用 `if` 而非 `&&`：

```bash
# 正确
if [ -n "$line3" ]; then printf "%b\n" "$line3"; fi

# 错误（exit 1）
[ -n "$line3" ] && printf "%b\n" "$line3"
```

### 颜色不显示

终端需支持 24-bit true color（推荐 iTerm2，macOS Terminal.app 不支持）。

### 调试

```bash
# 捕获 Claude Code 实际传入的 JSON
cat > /tmp/debug.sh << 'EOF'
#!/usr/bin/env bash
cat > /tmp/statusline-input.json
EOF
chmod +x /tmp/debug.sh
# settings.json 的 command 改为 bash /tmp/debug.sh
# 重启 claude，cat /tmp/statusline-input.json 即可看到原始数据
```

## 恢复默认

```bash
jq 'del(.statusLine)' ~/.claude/settings.json > ~/.claude/settings.json.tmp && mv ~/.claude/settings.json.tmp ~/.claude/settings.json
```

## License

MIT
