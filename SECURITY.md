# 安全与隐私说明

此仓库按“源码可迁移、身份与运行状态不可迁移”原则构建。

## 明确排除

- Codex `auth.json`、全局状态文件、安装 ID、浏览器原生主机状态。
- 浏览器资料、Cookie、Local Storage、保存的密码、GitHub/OAuth 会话。
- `.env`、API Key、访问令牌、私钥、许可证文件或许可证服务器凭据。
- Codex 会话、历史、记忆、日志、附件、录音、生成媒体、自动化状态和 SQLite 数据库。
- `.venv`、缓存、`__pycache__`、临时文件、作业/队列/求解结果。
- ANSYS/Abaqus/Windows/Codex 可执行文件与商业软件内容。

## 上传方式

仓库建议设为 **Private**。即使本包已脱敏，个人自动化源码也可能暴露工作流、软件安装习惯或内部工程方法。不要把私有仓库改为公开，除非再次完成人工代码审查并确认所有第三方许可证允许公开再分发。

## 运行风险

- `abaqus-live-bridge` 可在打开的 Abaqus/CAE 内执行 Python。它默认仅监听 `127.0.0.1`；不要改为公网地址。
- ANSYS/Abaqus 工具可以启动求解、写入新文件或改变当前工程。先做环境检查与只读检查，使用新输出目录，并保留源工程。
- Browser Use Enhanced 能操作已登录网页。目标机必须重新授权；不要迁移 Cookie 或浏览器资料来绕过登录。
- 安装脚本的 `-InstallDependencies` 会从 Python 包索引下载依赖。可先用 `-WhatIf` 检查文件迁移，再决定是否安装。

## 发布前检查

运行：

```powershell
.\scripts\Test-CodexPortable.ps1
```

发布资产同时提供 SHA-256 校验值。下载后可运行：

```powershell
Get-FileHash .\codex-portable-architecture-2026.09.02.zip -Algorithm SHA256
```
