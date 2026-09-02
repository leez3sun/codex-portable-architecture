# 本机 Codex 架构盘点（2026-09-02）

## 1. 插件

截图显示 17 个启用插件。实际缓存和清单核对如下。

### 个人插件（源码已迁移）

| 插件 | 版本 | 迁移处理 |
| --- | --- | --- |
| Abaqus/CAE | 0.1.0 | 已复制源码；将硬编码 Abaqus/Python 路径改为自动检测与环境变量覆盖 |
| Ansys Fluent | 0.1.0 | 已复制源码；将 v241 绝对路径改为多版本自动检测 |
| Browser Use Enhanced | 0.1.0+codex.20260812062338 | 已复制封装与技能；排除 327 MB `.venv`，用 `browser-use==0.13.7` 重建 |
| Scientific Media Studio | 0.1.0+codex.20260811051206 | 已复制源码/技能/资产；Python 路径改为隔离运行时 |

### 官方/精选插件（记录版本，目标机重新安装）

| UI 名称 | 本机缓存标识/版本 |
| --- | --- |
| Data | data-analytics 0.2.35-13ceeea1f599 |
| Remotion | remotion 1.0.7 |
| GitHub | github 0.1.12-5f7cd798dc99 |
| Default templates | openai-templates 0.1.1 |
| Plugin Management | plugin-management 0.1.0 |
| Documents | documents 26.826.12353 |
| PDF | pdf 26.826.12353 |
| Spreadsheets | spreadsheets 26.826.12353 |
| Presentations | presentations 26.826.12353 |
| Template Creator | template-creator 26.826.12353 |
| Sites | sites 0.1.52 |
| Computer Use | computer-use 26.831.20005 |
| Visualize | visualize 1.0.27 |

Codex 内部还存在 Browser/Chrome、Codex App Tools 等运行组件；这些由应用版本管理，不作为用户插件缓存迁移。

## 2. Apps / 连接器

截图显示 6 个：Sites、GitHub、Codex Document Control、Hotline、Plugin Management、Safety Settings。它们的代码/授权由 Codex 服务或应用管理；本包只记录名称，不复制 OAuth、Cookie 或连接状态。目标机需逐项重新连接。

## 3. MCP

| MCP | 本机状态 | 迁移处理 |
| --- | --- | --- |
| ansys-workbench | 独立本地服务器 | 源码已封装为 `ansys-workbench` 插件；排除 `.venv`、jobs、queue、`.env` |
| node_repl | Codex 内置运行组件 | 不迁移；随目标机 Codex 自动生成 |
| abaqus（CLI 清单中发现） | 独立 Abaqus/CAE 实时桥 | 已封装为 `abaqus-live-bridge` 插件，并移除用户名绝对路径 |
| abaqus-cae | 来自个人插件 | 随插件迁移 |
| ansys-fluent | 来自个人插件 | 随插件迁移 |
| browser-use-enhanced | 来自个人插件 | 随插件迁移；运行时重建 |
| scientific-media-studio | 来自个人插件 | 随插件迁移；运行时重建 |
| codex_apps | Codex 应用连接器聚合服务 | 不迁移；目标机重新连接 Apps |
| cua_repl | 已禁用的应用内部配置 | 不迁移 |

## 4. 个人技能

| 技能 | 来源/版本信息 | 迁移处理 |
| --- | --- | --- |
| academic-research-suite（ARS-Codex） | Codex adapter 0.1.22；上游 ARS commit `828ef3b...` | 完整复制；保留 CC BY-NC 4.0 许可证与上游归属 |
| browser-use | 本地技能封装 | 完整复制 |
| ppt-master | 4.8.0，MIT | 完整复制（含模板与参考资产） |
| thesis-crossref-validate | ResearchPilot 免费 API 技能 | 完整复制 |
| thesis-openalex-expand | ResearchPilot 免费 API 技能 | 完整复制 |
| thesis-openalex-search | ResearchPilot 免费 API 技能 | 完整复制 |
| thesis-research-router | ResearchPilot 路由技能 | 完整复制 |

系统技能 Image Gen、OpenAI Docs、Plugin Creator 随 Codex 安装提供，不复制其系统目录。

## 5. 配置与本地状态

当前配置中的模型/界面偏好已转写为安全示例；机器专属 `notify`、内置 marketplace 路径、项目信任目录、`node_repl` 路径、管道 ID、应用哈希和 elevated sandbox 设置均未复制。完整 `config.toml` 不应跨机器覆盖。
