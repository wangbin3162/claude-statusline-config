# Statusline Config Skill 安装指南

## 方式一：本地已有

skill 已在 `~/.claude/skills/statusline-config/`，Claude Code 自动加载，无需额外安装。

在 Claude Code 中直接运行：

```
/statusline-config
```

## 方式二：通过 npx skills 安装（TODO）

当前 skill 尚未发布到公开 registry，所以 `npx skills add` 还搜不到。

### 如果要让 npx skills 可安装

`npx skills` 支持两种安装源：

**1. GitHub 仓库**（推荐）

```bash
# 把 skill 推送到 GitHub
cd ~/.claude/skills/statusline-config
git init
git add .
git commit -m "init statusline-config skill"
# 在 GitHub 上创建仓库，然后：
git remote add origin git@github.com:<你的用户名>/<仓库名>.git
git push -u origin main

# 之后在任何机器上安装：
npx skills add <你的用户名>/<仓库名>
```

**2. 直链 URL**

把整个 `~/.claude/skills/statusline-config/` 目录托管到任意 HTTP 服务器，然后：

```bash
npx skills add https://你的域名/statusline-config/SKILL.md
```

### 发布到 npm

如果需要让更多人通过 `npm install` 安装：

```bash
# 在技能目录创建 package.json
npx skills init

# 发布到 npm
npm publish

# 安装
npx skills add @你的用户名/statusline-config
# 或
npm install @你的用户名/statusline-config
```

### 发布前检查清单

- [ ] `SKILL.md` 有正确的 frontmatter（name、description）
- [ ] 所有路径使用 `~/.claude/` 而非硬编码绝对路径
- [ ] 脚本不依赖本机特有工具（仅需 bash、jq、git 等通用工具）
- [ ] README 更新完毕

## 本地手动安装

如果技能在别处（比如另一台机器），可以手动复制：

```bash
# 把技能目录复制到 Claude Code skills 目录
cp -r /path/to/statusline-config ~/.claude/skills/
```

然后重启 Claude Code，就可以用 `/statusline-config` 命令了。

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
