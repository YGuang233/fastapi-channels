---
comments: true
search:
  exclude: true
---

# 特性

## FastAPI-Channels 的特性

**FastAPI-Channels** 提供以下功能：

FastAPI-Channels 是基于 FastAPI 开发的扩展库，用于 WebSocket 接口通讯，旨在提供快捷方便的解决方案，保持与 FastAPI 风格一致，相当于一个子应用。

### 功能性

考虑了常见使用场景和基础频道构建需求，包括权限验证、限流和最大连接数限制。

第三方库集成：

- **Broadcaster**：利用 Broadcaster 库实现高效的实时消息传递，支持多种后端。
- **FastAPI-Limiter**、**limits**： 实现速率限制，控制 WebSocket接口和action的使用频率。

### 简洁

提供简洁的API和配置方式，减少开发者的学习成本和开发时间。

### Action

action就像fastapi的get、post...的装饰器一样，用户只需专注于编写 `action` 来实现做出响应的动作，传输目标，并定义相应的权限类、限流器等，简化开发流程。

### 可扩展

- 设计时考虑了可扩展性，开发者可以轻松定制和扩展库以适应特定用例。
- 所有类型都有合理的默认值，并提供可选配置。参数经过微调，以满足不同需求。

### 文档和示例

提供全面的文档和示例，帮助用户快速高效地上手。

---

## FastAPI 的特性

FastAPI-Channels 基于 FastAPI 的核心理念开发：

<center>推崇高性能、易于学习、快速编码，适用于生产环境。</center>

- **更主流的 Python**：全部基于标准的 Python 3.6 类型声明，无需学习新语法。
- **类型注释**：提供明确直观的提示，提升代码可读性和维护性。
- **依赖注入**：简化复杂依赖关系的管理，增强代码的模块化和可测试性。


