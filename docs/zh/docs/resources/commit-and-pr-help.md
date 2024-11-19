---
search:
  exclude: true
---

# 开发 - PR 和 commit message

## label 列表

| label    | Title            | desc                                   |
|----------|------------------|----------------------------------------|
| breaking | Breaking Changes |                                        |
| security | Security Fixes   |                                        |
| feature  | Features         |                                        |
| bug      | Fixes            | Something isn't working                |
| refactor | Refactors        |                                        |
| upgrade  | Upgrades         |                                        |
| docs     | Docs             | Documentation about how to use FastAPI |
| lang-all | Translations     | Translations                           |
| internal | Internal         |                                        |

有很多`label`不被`latest_changes`收录，但是被使用着，如下面的

| label           | desc                                                         |
|-----------------|--------------------------------------------------------------|
| lang-en         | English translations                                         |
| lang-zh         | Traditional Chinese translations                             |
| lang-zh-hant    | Traditional Chinese translations                             |
| awaiting-review | Comments from those who understand this language are needed. |

## 提交gitmoji前缀参考

| emoji | 描述            | label参考           | commit message 语句参考                                                                     |
|-------|---------------|-------------------|-----------------------------------------------------------------------------------------|
| 📝    | 修改更新已经存在的文档   | docs              | 📝 Update includes for in `docs/zh/xx.md`                                               |
| ✏️    | 修改更新已经存在的文档错误 | docs、lang-all     | ✏️ Fix error in `docs/zh/xx.md`                                                         |
| 🎨    | 修改主要语言、测试案例   | docs、fix、internal | 比较自由                                                                                    |
| 🌐    | 新增翻译          | lang-all          | 🌐 Add English translation for `docs/en/xx.md`                                          |
| ♻️    | 重构            | refactor、internal | 比较自由                                                                                    |
| 🐛    | 修复            | bug               | 🐛 Fix 修复内容                                                                             |
| 🔧    | 修复            | refactor、internal | 比较自由                                                                                    |
| ⬆️    | 升级依赖          | internal          | ⬆️ ⬆ Upgrade docs development dependency on to >=0.0.12 to fix conflicts.               |
| 👷    | 工作流、机器人相关操作   | internal          | 👷Switch from Codecov to Smokeshow plus pytest-cov to pure coverage for internal tests. |
| 👥    | 修改更新内部开发人员文档  | internal          | 👥 Update Dev People                                                                    |
| ✨     | 修改更新内部开发人员文档  | feature           | ✨ Introduce new features                                                                |

> [更多gitmoji](https://gitmoji.dev/) 请直接使用表情符号