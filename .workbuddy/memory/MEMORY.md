# MEMORY.md

## 项目概况
- **健康打卡 App**: `C:\Users\01\WorkBuddy\Claw\health-app.html`
- **代理服务**: `C:\Users\01\WorkBuddy\Claw\proxy-server.js`（端口 7890）
- **技术栈**: 单 HTML + Vanilla JS + TailwindCSS CDN + localStorage
- **AI 平台**: 公司内部 `tc-paperhub.diezhi.net`，模型 `qwen3-vl-plus`（图文）

## 数据结构（water 字段演进）
- **旧格式**: `water: 500`（纯数字，单位 ml）
- **新格式**: `waterEntries: [{time: "16:22", amount: 500}, ...]`（带时间戳数组）
- **兼容处理**: `saveRecordToData` 自动识别旧数据并迁移

## 确认卡片数据流
`AI返回结构化数据` → `buildConfirmCard(data)` → `data-record属性存储JSON` → `confirmRecord读取data-record` → `saveRecordToData`

## 关键函数
- `buildSystemPrompt()`: 系统提示词（小草健康助手），包含饮水/运动/时间格式规则
- `parseAIResponse()`: 解析【】包裹的 JSON，支持无【】fallback
- `buildConfirmCard()`: 构建确认卡片，`data-record` 属性存储原始结构化数据
- `confirmRecord()`: 从 `data-record` 直接读取，不再用文本解析
- `saveRecordToData()`: 写入 localStorage，`waterEntries` 累加模式
- `refreshDashboard()`: 从 `waterEntries` 累加计算总水量

## 启动方式
```bash
# 终端1: CORS 代理
node C:\Users\01\WorkBuddy\Claw\proxy-server.js

# 终端2: 静态文件服务器
node -e "require('http').createServer((req,res)=>{const fs=require('fs');const path=require('path');const url=req.url==='/'?'/health-app.html':req.url;res.writeHead(200,{'Content-Type':'text/html'});res.end(fs.readFileSync(path.join(__dirname,url)));}).listen(3000)"

# 访问 http://localhost:3000
```
