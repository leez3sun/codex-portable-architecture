# Codex 底层架构迁移包

这是 2026-09-02 对当前电脑所安装 Codex 架构进行盘点、脱敏和便携化后的迁移包。目标电脑无需 Git 命令：在 GitHub 网页下载 Release ZIP（或 **Code > Download ZIP**），解压后运行安装脚本即可。

## 家用主机安装

1. 在家用主机登录 GitHub，打开本仓库的 **Releases** 页面。
2. 下载 `codex-portable-architecture-2026.09.02.zip`，解压到纯英文路径，例如 `C:\CodexPortableBundle`。
3. 打开 PowerShell，先预览将执行的操作：

   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\scripts\Install-CodexPortable.ps1 -InstallDependencies -WhatIf
   ```

4. 确认后正式安装：

   ```powershell
   .\scripts\Install-CodexPortable.ps1 -InstallDependencies
   ```

5. 重启 Codex。打开“插件”，选择 `Codex Portable` 来源，核对六个个人插件。七个独立技能会复制到 `%USERPROFILE%\.codex\skills`，在新任务中生效。
6. 运行结构检查：

   ```powershell
   .\scripts\Test-CodexPortable.ps1
   ```

若目标位置已有同名技能或旧迁移包，脚本默认保留它们并停止/跳过覆盖。确实要替换时使用 `-Force`；旧内容会先移动到带时间戳的备份目录，不会直接删除。

## 已迁移内容

- 4 个原有个人插件：Abaqus/CAE、Ansys Fluent、Browser Use Enhanced、Scientific Media Studio。
- 7 个个人技能：ARS-Codex、Browser Use、Ppt Master、ResearchPilot CrossRef、OpenAlex Expand、OpenAlex Search、Router。
- 2 个原独立 MCP 已封装成插件：Abaqus Live Bridge、Ansys Workbench。
- 一个符合 Codex 规范的仓库级插件市场：`.agents/plugins/marketplace.json`。
- 可选的 Codex 用户偏好模板、迁移清单、安全说明、验证脚本和依赖重建脚本。

完整版本与来源见 [INVENTORY.md](INVENTORY.md)。

## 不会迁移的内容

以下内容要么由 Codex 自动生成，要么含登录态/个人数据，因此只记录、不上传：

- `auth.json`、浏览器 Cookie/配置、GitHub/OAuth 登录态、API Key、密码和 `.env`。
- 会话、任务历史、记忆、日志、SQLite 数据库、附件、生成图片和自动化运行状态。
- Python `.venv`、`__pycache__`、插件缓存、Codex 自带 `node_repl` 和应用内部路径。
- ANSYS、Abaqus、FFmpeg、Node、Python 本体及商业软件许可证。
- Fluent/Workbench/Abaqus 工程、ODB/CAS/DAT/项目数据库、队列与求解结果。

官方或精选插件也不复制其缓存；它们应在家用主机的 Codex 插件目录重新安装。账号型应用必须重新授权。

## 运行环境说明

- Windows 10/11 与已安装的 Codex。
- Python 3.11+；依赖安装会在 `%LOCALAPPDATA%\CodexPortable\runtimes` 下重建隔离环境。
- Browser Use Enhanced 需要 Chrome/Chromium 与相应浏览器控制设置。
- Ansys 插件需要目标机已合法安装并授权 ANSYS。启动器会查找 `AWP_ROOT###`、`ANSYS_ROOT` 或常见 `C:/D:/E:\Program Files\ANSYS Inc\v###` 路径。
- Abaqus 插件需要目标机已合法安装并授权 Abaqus。若命令未进入 `PATH`，请设置环境变量 `ABAQUS_COMMAND`。
- Scientific Media Studio 的视频能力还需要 `ffmpeg`、`ffprobe` 和 `node` 在 `PATH` 中。

## 可选参数

```powershell
# 只迁移文件，不安装 Python 依赖
.\scripts\Install-CodexPortable.ps1

# 指定 Python
.\scripts\Install-CodexPortable.ps1 -InstallDependencies -Python C:\Python312\python.exe

# 不自动调用 Codex CLI 安装插件
.\scripts\Install-CodexPortable.ps1 -InstallDependencies -SkipPluginInstall

# 备份并替换已有同名内容
.\scripts\Install-CodexPortable.ps1 -InstallDependencies -Force
```

## 迁移后的人工步骤

- 在 Codex 插件目录重新安装 13 个官方/精选插件，并重新连接 GitHub 等账号应用。
- Abaqus Live Bridge：在 Abaqus/CAE 中通过 **File > Run Script** 运行插件目录内的 `scripts/abaqus_mcp_bridge.py`，保持 CAE 会话开启。
- Ansys Workbench：按 `plugins/ansys-workbench/server/README.zh-CN.md` 安装或加载 Mechanical ACT 桥，并先调用环境/就绪检查工具。
- 对照 `config/codex-user-settings.example.toml` 手工选择要恢复的界面偏好；不要覆盖目标机完整的 `config.toml`。

安全边界和未上传数据详见 [SECURITY.md](SECURITY.md)。
