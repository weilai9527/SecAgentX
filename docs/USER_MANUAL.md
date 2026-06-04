# SecAgentX 使用说明书

版本：0.1.0  
适用对象：安全运营人员、告警分析人员、演示人员、开发调试人员

## 1. 产品简介

SecAgentX 是一个安全运营告警分析工作台。它把原始安全告警转换为安全事件，并通过多阶段 Agent 流程完成研判、证据提取、攻击链分析、处置建议生成和事件报告输出。

典型使用流程是：

1. 载入内置演示案例，或手动新建一条告警。
2. 系统自动创建关联事件。
3. 选择事件并点击“开始分析”。
4. 查看 Agent 执行过程、证据链、攻击路径、处置建议和报告。
5. 对处置建议进行审批、驳回或模拟执行。
6. 生成并下载 Markdown 事件报告。

## 2. 系统组成

项目目录：

```text
secagentx/
  backend/       后端 FastAPI 服务
  frontend/      前端 Vite + React 工作台
  start.bat      Windows 一键启动脚本
  start.sh       Linux/macOS 启动脚本
  docs/          使用说明文档
```

默认访问地址：

| 服务 | 地址 | 说明 |
| --- | --- | --- |
| 前端工作台 | http://127.0.0.1:5173/ | Vite 开发服务，端口占用时会自动切到 5174、5175 等 |
| 后端 API | http://127.0.0.1:8000/ | FastAPI 服务 |
| 健康检查 | http://127.0.0.1:8000/api/health | 判断后端是否启动成功 |

## 3. 环境要求

必需环境：

- Windows 10/11、Linux 或 macOS
- Python 3.10 或更高版本
- Node.js 18 或更高版本
- npm

建议环境：

- Python 虚拟环境，避免污染系统 Python
- 稳定网络，用于首次安装 Python 和 Node 依赖
- 可选的大模型 API Key，用于真实智能分析

## 4. 快速启动

### 4.1 Windows 一键启动

在项目根目录双击：

```text
start.bat
```

脚本会依次执行：

1. 检查 Python。
2. 安装后端依赖。
3. 启动后端服务。
4. 检查 Node.js。
5. 安装前端依赖。
6. 启动前端服务。

如果看到前端输出类似下面内容，说明前端启动成功：

```text
VITE ready
Local: http://127.0.0.1:5173/
```

如果提示 `Port 5173 is in use, trying another one...`，说明 5173 端口已被占用，按终端里显示的新地址访问，例如：

```text
http://127.0.0.1:5174/
```

### 4.2 手动启动后端

打开终端，进入后端目录：

```powershell
cd C:\Users\weilai\Downloads\opencode_副本\secagentx\backend
python -m pip install -r requirements.txt
python run.py
```

启动成功后会看到：

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

验证后端：

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/health
```

正常返回：

```json
{"ok": true, "app": "SecAgentX", "version": "0.1.0"}
```

### 4.3 手动启动前端

另开一个终端，进入前端目录：

```powershell
cd C:\Users\weilai\Downloads\opencode_副本\secagentx\frontend
npm install
npm run dev
```

启动成功后，在浏览器打开终端显示的 Local 地址。

## 5. 首次使用流程

### 5.1 打开工作台

访问前端地址，例如：

```text
http://127.0.0.1:5173/
```

如果 5173 被占用，就访问 Vite 输出的新端口，例如：

```text
http://127.0.0.1:5174/
```

页面主要分为三栏：

| 区域 | 位置 | 用途 |
| --- | --- | --- |
| 告警/案例列表 | 左侧 | 加载演示案例、筛选告警、选择事件 |
| 事件详情 | 中间 | 查看原始告警、风险等级、事件摘要、启动分析 |
| 分析面板 | 右侧 | 查看 Agent、证据、攻击链、处置建议、报告 |

### 5.2 使用内置演示案例

左侧顶部是内置演示案例。点击任意案例后，系统会自动：

1. 创建一条告警。
2. 创建一条关联事件。
3. 选中该事件并显示详情。

当前内置案例包括：

| 案例 | 严重性 | 适用场景 |
| --- | --- | --- |
| SSH 暴力破解后疑似入侵 | high | 登录爆破、异常脚本执行 |
| Web SQL 注入攻击告警 | critical | WAF 告警、SQL 注入、疑似数据泄露 |
| Log4j 高危漏洞利用 | critical | RCE、反连、漏洞利用 |
| 主机异常进程与外联行为 | medium | 挖矿、异常进程、持久化 |
| 可疑账号横向登录行为 | high | 凭证滥用、横向移动 |

### 5.3 手动新建告警

点击右上角 `New Alert` 按钮。

在弹窗中粘贴告警日志或描述，例如：

```text
[EDR Alert] Suspicious PowerShell
Host: win-server-01
User: admin
Command: powershell -enc ...
Network: outbound connection to 203.0.113.10:443
```

点击 `Create` 后，系统会：

1. 保存该告警。
2. 自动创建关联事件。
3. 在左侧列表中显示该告警。
4. 自动选中新事件。

## 6. 事件分析

### 6.1 选择事件

在左侧告警队列中点击一条告警。只有已经关联事件的告警可以进入事件详情。

中间区域会显示：

- 事件 ID
- 告警 ID
- 创建时间
- 事件类型
- 风险等级
- 置信度
- 攻击阶段
- 当前状态
- 原始告警内容

### 6.2 开始分析

点击中间区域右上方的“开始分析”按钮。

分析会依次执行以下 Agent：

| 阶段 | Agent | 作用 |
| --- | --- | --- |
| 1 | Parser | 解析原始告警，提取告警类型、目标、来源、关键字段 |
| 2 | Triage | 判断风险等级、置信度和初步研判结论 |
| 3 | Evidence | 提取证据项，例如日志、IOC、资产、漏洞、工具痕迹 |
| 4 | Attack Chain | 分析攻击阶段和攻击路径 |
| 5 | Response | 生成处置建议 |
| 6 | Report | 生成安全事件报告 |

分析完成后，事件状态会进入 `review`，表示等待人工复核。

## 7. 右侧分析面板说明

右侧面板包含五个页签。

### 7.1 Agent Runs

用于查看每个 Agent 的执行记录。

可查看信息：

- Agent 名称
- 执行状态：pending、running、success、failed
- 执行耗时
- 输出结果
- 错误信息

如果某个 Agent 失败，先查看该卡片中的错误信息。常见原因包括模型 API 配置错误、网络不可达、输入数据异常。

### 7.2 Evidence

用于查看系统提取出的证据项。

证据类型包括：

| 类型 | 含义 |
| --- | --- |
| log | 日志证据 |
| ioc | IOC 指标，例如 IP、域名、哈希 |
| asset | 资产信息 |
| vuln | 漏洞信息 |
| tool | 攻击工具或可疑工具 |

每条证据包含：

- 标题
- 来源
- 内容
- 置信度百分比

置信度越高，表示该证据越可能支持当前研判结论。

### 7.3 Attack Chain

用于查看攻击链分析结果。

主要包含：

- 攻击路径，例如 `Initial Access -> Execution -> C2`
- 最可疑成功点
- 分阶段证据
- 各阶段置信度

这个页面适合用于复盘攻击过程，判断攻击是否已经进入执行、持久化、横向移动、命令控制等阶段。

### 7.4 Actions

用于查看和处理系统生成的处置建议。

每条处置建议包含：

- 动作类型
- 动作描述
- 风险等级
- 是否需要人工审批
- 当前状态

可执行操作：

| 操作 | 含义 |
| --- | --- |
| Approve / 审批 | 同意该处置建议 |
| Reject / 驳回 | 不采纳该处置建议 |
| Simulate / 模拟执行 | 不真正下发动作，只把状态标记为模拟执行 |

注意：当前版本的“模拟执行”只更新状态，不会真正隔离主机、封禁 IP 或调用外部安全设备。

### 7.5 Report

用于生成、查看和下载事件报告。

功能：

- 没有报告时，可点击“立即生成”。
- 已有报告时，可点击“重新生成”。
- 可点击“下载”导出 Markdown 文件。

报告内容通常包括：

- 告警标题
- 风险等级
- 研判摘要
- 证据列表
- 攻击链
- 处置建议
- 人工复核参考

下载后的文件名类似：

```text
report-1.md
```

## 8. 大模型配置

SecAgentX 支持两种运行方式：

1. 本地模拟模式：无需 API Key，适合演示和功能验证。
2. 真实模型模式：配置 API Key 后获得更完整的智能分析结果。

### 8.1 默认行为

后端默认读取：

```text
LLM_TYPE=deepseek
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-flash
```

如果没有配置 `DEEPSEEK_API_KEY`，系统会自动切换到 `local` 模式。

local 模式不会调用外部模型，只返回模拟分析内容，适合确认流程是否跑通。

### 8.2 配置 DeepSeek

PowerShell 示例：

```powershell
$env:LLM_TYPE="deepseek"
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:DEEPSEEK_BASE_URL="https://api.deepseek.com"
$env:LLM_MODEL="deepseek-v4-flash"
python run.py
```

### 8.3 配置 OpenAI 兼容服务

```powershell
$env:LLM_TYPE="openai"
$env:OPENAI_API_KEY="你的 OpenAI API Key"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"
$env:LLM_MODEL="gpt-4o"
python run.py
```

### 8.4 配置 Ollama 本地模型

先启动 Ollama 服务，然后设置：

```powershell
$env:LLM_TYPE="ollama"
$env:OLLAMA_BASE_URL="http://localhost:11434"
$env:LLM_MODEL="llama2"
python run.py
```

## 9. 数据存储

默认数据库为 SQLite，位置：

```text
backend/data/secagentx.db
```

数据库中保存：

- 告警
- 事件
- Agent 执行记录
- 证据项
- 处置建议
- 事件报告

如需使用其他数据库，可设置：

```powershell
$env:DATABASE_URL="sqlite:///自定义路径/secagentx.db"
```

或使用 SQLAlchemy 支持的其他数据库连接串。

## 10. API 简表

常用后端接口：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/health` | 健康检查 |
| GET | `/api/alerts` | 获取告警列表 |
| POST | `/api/alerts` | 创建告警 |
| DELETE | `/api/alerts/{alert_id}` | 删除告警 |
| POST | `/api/alerts/from-case/{case_id}` | 从内置案例创建告警 |
| GET | `/api/incidents` | 获取事件列表 |
| POST | `/api/incidents` | 创建事件 |
| GET | `/api/incidents/{incident_id}` | 获取事件详情 |
| POST | `/api/incidents/{incident_id}/analyze` | 启动分析 |
| GET | `/api/incidents/{incident_id}/actions` | 获取处置建议 |
| POST | `/api/incidents/{incident_id}/actions/{action_id}/approve` | 审批处置建议 |
| POST | `/api/incidents/{incident_id}/actions/{action_id}/reject` | 驳回处置建议 |
| POST | `/api/incidents/{incident_id}/actions/{action_id}/simulate` | 模拟执行处置建议 |
| GET | `/api/incidents/{incident_id}/report` | 获取最新报告 |
| POST | `/api/incidents/{incident_id}/report` | 生成新报告 |

## 11. 常见问题排查

### 11.1 前端打不开

检查前端服务是否启动：

```powershell
cd frontend
npm run dev
```

如果看到：

```text
Port 5173 is in use, trying another one...
Local: http://127.0.0.1:5174/
```

请访问实际显示的地址，而不是固定访问 5173。

### 11.2 后端打不开

检查后端：

```powershell
cd backend
python run.py
```

然后访问：

```text
http://127.0.0.1:8000/api/health
```

如果 8000 被占用，需要关闭占用该端口的进程，或修改 `backend/run.py` 中的端口。

### 11.3 页面能打开，但分析按钮无反应

按顺序检查：

1. 后端是否启动。
2. 前端是否通过 Vite 代理访问 `/api`。
3. 浏览器开发者工具 Console 是否有报错。
4. 后端终端是否有异常堆栈。

### 11.4 分析结果比较简单

如果没有配置 API Key，系统会自动使用 local 模拟模式。此时结果主要用于演示流程，不代表真实模型能力。

需要更完整结果时，配置 DeepSeek、OpenAI 或 Ollama。

### 11.5 页面文字出现乱码

当前部分源码中的中文文案曾经被错误编码保存，可能导致页面显示乱码。功能本身仍可用。

如果要彻底修复，需要统一把前端组件和后端内置案例中的中文文案按 UTF-8 重新保存。

### 11.6 CORS 或接口请求失败

默认 CORS 配置为：

```text
http://localhost:5173,http://127.0.0.1:5173
```

如果前端运行在 5174 或其他端口，Vite 代理通常仍能工作。若直接跨域访问后端，需要设置：

```powershell
$env:CORS_ORIGINS="http://localhost:5174,http://127.0.0.1:5174"
python run.py
```

### 11.7 npm install 失败

可尝试：

```powershell
cd frontend
npm cache verify
npm install
```

如果网络受限，请配置 npm 镜像源或代理。

### 11.8 Python 依赖安装失败

可尝试升级 pip：

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

建议使用 Python 3.10、3.11 或 3.12；过新的 Python 版本可能遇到少数依赖兼容问题。

## 12. 日常使用建议

- 演示时优先使用内置案例，最容易跑通完整流程。
- 做真实分析前先配置大模型 API Key。
- 每次演示前先打开 `/api/health` 确认后端正常。
- 若前端端口变化，以 Vite 终端输出为准。
- 处置建议在当前版本不会真正调用外部安全设备，适合作为工作流演示和人工复核参考。
- 报告为 Markdown 格式，适合复制到工单、知识库或日报系统。

## 13. 推荐演示脚本

可按以下步骤进行一次完整演示：

1. 启动后端和前端。
2. 打开前端工作台。
3. 点击左侧 `Web SQL 注入攻击告警` 演示案例。
4. 在中间事件详情区点击“开始分析”。
5. 切到 `Agent Runs`，展示多 Agent 执行过程。
6. 切到 `Evidence`，展示提取出的证据。
7. 切到 `Attack Chain`，展示攻击路径。
8. 切到 `Actions`，审批或模拟执行一条处置建议。
9. 切到 `Report`，生成并下载报告。
10. 打开下载的 Markdown 报告，展示最终输出。

## 14. 当前版本限制

- 处置动作只支持审批、驳回和模拟执行，不会真实调用防火墙、EDR、SOAR 等外部系统。
- 内置案例和部分界面文案可能存在中文乱码，需要后续统一修复编码。
- 分析流程当前是同步执行，请等待按钮 loading 结束后再查看结果。
- 报告下载为 Markdown，不是 PDF 或 Word。
- 默认数据库为本地 SQLite，不适合多人并发生产环境。

## 15. 联系维护

如果出现无法启动或分析失败，请优先提供以下信息：

- 操作系统版本
- Python 版本：`python --version`
- Node 版本：`node --version`
- 后端启动日志
- 前端启动日志
- 浏览器 Console 报错
- 触发问题的告警内容或案例名称
