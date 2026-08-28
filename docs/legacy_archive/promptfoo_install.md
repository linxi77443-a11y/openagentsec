# promptfoo 安装说明

## 当前状态

当前环境未检测到 `promptfoo` 命令。

第二阶段不会自动安装 promptfoo，避免未经确认引入外部依赖或触发网络访问。

## 人工确认后安装

如确认需要安装，可在项目目录外或当前项目目录中手动执行：

```bash
npm install -g promptfoo
```

安装后检查版本：

```bash
promptfoo --version
```

## 本项目允许的使用范围

仅允许使用 promptfoo 测试本地 sandbox：

```text
sandbox/chatbot_demo/chatbot.py
```

禁止配置：

- 真实模型 API
- 真实企业系统
- 外部网络目标
- 生产系统
- 真实凭证

## 执行方式

默认 dry-run：

```bash
bash runners/run_promptfoo.sh
```

确认后执行本地测试：

```bash
bash runners/run_promptfoo.sh --execute
```

测试结果应写入：

```text
reports/evidence/promptfoo_chatbot_result.json
```
