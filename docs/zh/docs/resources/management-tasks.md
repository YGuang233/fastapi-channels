---
comments: true
search:
  exclude: true
---

# 开发 - 存储库管理任务

[//]: # (这些是团队成员[team members]&#40;../dev-people.md#team&#41;{.internal-link target=_blank}可以执行的管理 FastAPI 存储库的任务。)
这些是团队成员可以执行的管理 FastAPI-Channels 存储库的任务。

!!! tip
    此部分仅对少数人有用，即具有管理存储库权限的团队成员。你可以跳过它。😉


[//]: # (...so, you are a [team member of FastAPI-Channels]&#40;../dev-people.md#team&#41;{.internal-link target=_blank}? Wow, you are so cool! 😎)

您可以在[帮助 FastAPI-Channels 与求助](help-fastapi-channels.md){.internal-link target=_blank}上以与外部贡献者相同的方式提供所有帮助。但此外，有些任务只有您（作为团队的一员）才能执行。

以下是您可以执行的任务的一般说明。

非常感谢你的帮助。🙇

## 友善

首先，要友善一点。😊

如果你被加入团队，你可能会非常友善，但值得一提。🤓

### 当事情变得困难时

当事情顺利时，一切都会变得容易，因此不需要太多指导。但当事情困难时，这里有一些指导方针。

尝试寻找好的一面。一般来说，如果人们不是不友好，请尝试感谢他们的努力和兴趣，即使您不同意主要主题（讨论，PR），也只需感谢他们对项目感兴趣，或者花一些时间尝试做某事。

用文字很难传达情感，可以使用表情符号来帮助。😅

在讨论和公关中，很多情况下，人们会毫无顾忌地表达自己的挫败感，很多情况下会夸大其词、抱怨、自以为是等等。这真的不好，而且当这种情况发生时，我们会降低我们解决他们问题的优先级。但还是要试着呼吸，并温柔地回答问题。

尽量避免使用尖刻的讽刺或潜在的消极攻击性评论。如果有什么不对劲，最好直接（尽量温和）而不是讽刺。

尽量做到尽可能具体和客观，避免泛泛而谈。

对于更困难的对话，例如拒绝 PR，您可以直接请我（@YGuang233）处理。

## 编辑 PR 标题

* 编辑 PR 标题，以<a href="https://gitmoji.dev/" class="external-link" target="_blank">gitmoji</a>表情符号开头。
    * 使用表情符号，而不是 GitHub 代码。因此，请使用 `🐛` 而不是 `:bug:`。这样它才能在 GitHub 之外正确显示，例如在发行说明中。
    * 翻译时请使用 `🌐` 表情符号（“带有子午线的地球仪”
* 标题以动词开头。例如 `Add`, `Refactor`, `Fix`, 等. 这种命名方式的标题将会说明这个PR贡献人员做了哪些操作。 例如 `Add support for teleporting`, 而不是 `Teleporting wasn't working, so this PR fixes it`.
* 编辑PR标题的文本，以“命令式”开头, 就像下达命令一样。所以将 `Adding support for teleporting` 改为使用 `Add support for teleporting`更好。
* 试着让标题描述它所取得的成就。 如果这是一个特征，试着描述它， 就比如 `Add support for teleporting` 而不是 `Create TeleportAdapter class`.
* 不要使用 (`.`)结束标题.
* 当 PR 是针对翻译的，请以 `🌐` 开头，`Add {language} translation for` 然后是翻译的文件路径。例如：

```Markdown
🌐 Add Spanish translation for `docs/es/docs/teleporting.md`
```

PR 合并后，GitHub Action (<a href="https://github.com/tiangolo/latest-changes" class="external-link" target="_blank">latest-changes</a>)  将根据 PR 标题自动更新 `release-notes`。


因此，一个好的 PR 标题不仅在 GitHub 上看起来不错，而且在`release-notes`中也很好看。📝

## 为 PR 添加标签

相同的 GitHub Action <a href="https://github.com/tiangolo/latest-changes" class="external-link" target="_blank">latest-changes</a> 使用 PR 中的一个标签来决定将此 PR 放入发行说明中的哪个部分。

确保使用受支持的标签 <a href="https://github.com/tiangolo/latest-changes#using-labels" class="external-link" target="_blank">latest-changes list of labels</a>:

* `breaking`: 重大变更
    * 如果现有代码在不更改代码的情况下更新版本，则会中断。这种情况很少发生，所以这个标签并不常用。
* `security`: 安全修复
    * 这是为了修复安全漏洞。它几乎从来没被使用过。
* `feature`: 特征
    * 新功能，增加了对以前不存在的事物的支持。
* `bug`: 修复
    * 支持的东西不起作用，这可以修复它。有许多PR声称是错误修复，因为用户以一种不受支持的意外方式做了一些事情，但他们认为这是默认情况下应该支持的。其中许多实际上是功能或重构。但在某些情况下，确实存在一个错误。
* `refactor`: 重构
    * 这通常用于更改内部代码，但不会改变行为。通常它可以提高可维护性，或启用未来功能等。
* `upgrade`: 升级
    * 这用于升级来自项目的直接依赖项或额外的可选依赖项，通常在 `pyproject.toml` 中。 因此，对最终用户有影响的事情，一旦更新，他们最终会在代码库中收到升级。但这并不适用于升级用于开发、测试、文档等的内部依赖关系。这些内部依赖关系，通常在 `requirements.txt` 文件或 GitHub Action 版本中，应标记为 `internal`, 而不是 `upgrade`.
* `docs`: 文档
    * 文档中的更改。这包括更新文档、修复拼写错误。但它不包括对翻译的更改。
    * 您通常可以通过访问 PR 中 "Files changed" 的 tab 来 检查更新的文件是否以开头 `docs/zh/docs`. 文档的原始版本始终是简体中文的，因此是`docs/zh/docs`。
* `lang-all`: 翻译
    * 您通常可以通过访问 PR 中 "Files changed" 的 tab 来 检查更新的文件是否以开头 `docs/{some lang}/docs` 而不是 `docs/zh/docs`。比如， `docs/en/docs`。
* `internal`: 内部
    * 将其用于仅影响仓库管理方式的更改。例如，内部依赖关系的升级、GitHub Actions或脚本的更改等。

!!! tip

    一些工具，如Dependabot，会添加一些标签，如 `dependencies`, 但请记住，这个标签 `latest-changes` GitHub Action 不会使用, 因此，它不会更新 release notes. 请确保添加了`latest-changes`标签。

!!! warning

    目前不支持提供 **简体中文** 、**繁体中文**、 **英文** 之外的翻译和文档修改PR，没有过多的精力处理这些

[//]: # (## 为翻译PR添加标签)

[//]: # ()
[//]: # (当有翻译的 PR 时，除了添加 `lang-all` 标签外，还要添加语言的标签。)

[//]: # ()
[//]: # (每种语言都会有一个使用语言代码的标签，就像 `lang-{lang code}` 这样的形式, 列如, `lang-en` 英语, `lang-zh-hant` 繁体中文，等等。)

[//]: # ()
[//]: # (* 添加特定的语言标签。)

[//]: # (* 添加 `awaiting-review` 标签。)

[//]: # ()
[//]: # (`awaiting-review` 标签很特殊，仅用于翻译。GitHub Action 会检测到它，然后读取语言标签，并更新管理该语言翻译的 GitHub Discussions，通知人们有新的翻译需要审阅。)

[//]: # ()
[//]: # (一旦有母语人士出现，审查并批准 PR，GitHub Action 就会来删除标签`awaiting-review` 然后添加 `approved-1` 标签.)

[//]: # ()
[//]: # (这样，我们就可以注意到何时有新的翻译准备好，因为它们有 `approved-1` 标签。)

[//]: # (## 合并翻译PR)

[//]: # (对于中文，由于我是母语人士，而且这是一种与我关系密切的语言，我会自己对它进行最后的审查，在大多数情况下，在合并之前会稍微调整一下PR。)

[//]: # (对于其他语言请确认：)

[//]: # ()
[//]: # (* 按照上述说明，标题是正确的)

[//]: # (* 它拥有 `lang-all` 和 `lang-{lang code}`的标签.)

[//]: # (* PR只更改了一个Markdown文件，并添加了翻译。)

[//]: # (    * 或者在某些情况下，同一语言最多只能有两个文件（如果它们很小），人们会对它们进行审查。)

[//]: # (    * 如果这是该语言的第一个翻译，它将有额外的`mkdocs.yml`文件，在这些情况下，请按照以下说明进行操作。)

[//]: # (* PR不会添加额外的无关文件。)

[//]: # (* 译文的结构似乎与简体中文原文相似。)

[//]: # (* 翻译似乎没有改变原始内容，例如明显的额外文档部分。)

[//]: # (* 翻译中没有使用不同的Markdown结构，例如在原文没有HTML标签时添加HTML标签。)

[//]: # (* 那些"admonition" 语法块, 如 `tip`, `info`等，没有更改或翻译。例如：)

[//]: # ()
[//]: # (```markdown)

[//]: # (!!! tip)

[//]: # ()
[//]: # (    This is a tip.)

[//]: # ()
[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (效果就像下面这样)

[//]: # ()
[//]: # (!!! tip)

[//]: # ()
[//]: # (    This is a tip.)

[//]: # ()
[//]: # ()
[//]: # (...它可以被翻译为西班牙语的内容:)

[//]: # ()
[//]: # (```markdown)

[//]: # (!!! tip)

[//]: # ()
[//]: # (    Esto es un consejo.)

[//]: # ()
[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (...但需要保留确切的 `tip` 关键字。如果它被翻译成 `consejo`，就像)

[//]: # ()
[//]: # (```markdown)

[//]: # (!!! consejo)

[//]: # ()
[//]: # (    Esto es un consejo.)

[//]: # ()
[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (它会将样式更改为默认样式，如下所示：)

[//]: # ()
[//]: # (!!! consejo)

[//]: # ()
[//]: # (    Esto es un consejo.)

[//]: # ()
[//]: # ()
[//]: # (这些不必翻译，但如果是，它们需要写成：)

[//]: # ()
[//]: # (```)

[//]: # (!!! tip "consejo")

[//]: # ()
[//]: # (    Esto es un consejo.)

[//]: # ()
[//]: # ()
[//]: # (```)

[//]: # ()
[//]: # (它看起来像：)

[//]: # ()
[//]: # (!!! tip  "consejo")

[//]: # ()
[//]: # (    Esto es un consejo.)

[//]: # ()
[//]: # ()
[//]: # (如果你要更改文档，并且想要使用本文档常用的模板语法，这里有很好的开发参考[开发 - Docs 开发文档]&#40;docs-dev.md&#41;)

[//]: # ()
[//]: # (如果你觉得上面文本看起来还是很费解，不愿意看着改文档，可以直接从[开发 - PR 和 commit message]&#40;commit-and-pr-help.md&#41;浏览关键的信息)

[//]: # (## First Translation PR)

[//]: # ()
[//]: # (当一种语言有第一次翻译时，它会有一个 `docs/{lang code}/docs/index.md` 翻译文件和一个 `docs/{lang code}/mkdocs.yml`.)

[//]: # ()
[//]: # (例如，对于波斯尼亚语，它将是：)

[//]: # ()
[//]: # (* `docs/bs/docs/index.md`)

[//]: # (* `docs/bs/mkdocs.yml`)

[//]: # ()
[//]: # (这个 `mkdocs.yml` 文件将仅包含以下内容：)

[//]: # ()
[//]: # (```YAML)

[//]: # (INHERIT: ../en/mkdocs.yml)

[//]: # (```)

[//]: # (语言代码通常位于 <a href="https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes" class="external-link" target="_blank">ISO 639-1 的语言代码列表</a>。)

[//]: # ()
[//]: # (无论如何，语言代码都应该是 <a href="https://github.com/YGuang233/fastapi-channels/blob/master/docs/language_names.yml" class="external-link" target="_blank">docs/language_names.yml</a>文件中的代码。)

[//]: # ()
[//]: # (语言代码还没有标签，例如，如果它是波斯尼亚语，就不会有 `lang-bs`。 语言代码还没有标签，例如，如果它是波斯尼亚语，就不会有, 创建对应的 GitHub Discussion:)

[//]: # ()
[//]: # (* 转到 <a href="https://github.com/YGuang233/fastapi-channels/discussions/categories/translations" class="external-link" target="_blank">Translations GitHub Discussions</a>)

[//]: # (* 创建带有 `Bosnian Translations` 标题（或英文语言名称）的新讨论)

[//]: # (* 添加描述:)

[//]: # ()
[//]: # (```Markdown)

[//]: # (## Bosnian translations)

[//]: # ()
[//]: # (This is the issue to track translations of the docs to Bosnian. 🚀)

[//]: # ()
[//]: # (Here are the [PRs to review with the label `lang-bs`]&#40;https://github.com/YGuang233/fastapi-channels/pulls?q=is%3Apr+is%3Aopen+sort%3Aupdated-desc+label%3Alang-bs+label%3A%22awaiting-review%22&#41;. 🤓)

[//]: # (```)

[//]: # ()
[//]: # (使用新语言更新“波斯尼亚语”。)

[//]: # ()
[//]: # (并更新搜索链接以指向将要创建的新语言标签，例如  `lang-bs`.)

[//]: # ()
[//]: # (创建标签并将其添加到刚刚创建的新 Discussion 中，例如 `lang-bs`.)

[//]: # ()
[//]: # (Th然后返回 PR，并添加标签，如 `lang-bs`， `lang-all` 和 `awaiting-review`.)

[//]: # ()
[//]: # (现在 GitHub action 将自动检测 `lang-bs` 标签，并将在该 Discussion 中发布此 PR 正在等待审核)

[//]: # ()
[//]: # (## Review PRs)

[//]: # ()
[//]: # (如果 PR 没有解释它的作用或原因，请询问更多信息。)

[//]: # ()
[//]: # (PR 应该有一个它正在解决的特定用例。)

[//]: # ()
[//]: # (* 如果 PR 是针对某个功能的，它应该有 docs。)

[//]: # (    * 除非这是我们想要阻止的功能，例如支持我们不希望用户使用的极端情况。)

[//]: # (* 文档应包含源示例文件，而不是直接在 Markdown 中编写 Python。)

[//]: # (* 如果源示例文件可以具有 Python 3.8、3.9、3.10 的不同语法，则文件应该有不同的版本，并且它们应该显示在文档的选项卡中。)

[//]: # (* 应该有测试测试源示例。)

[//]: # (* 在应用 PR 之前，新测试应失败。)

[//]: # (* 应用 PR 后，新测试应通过。)

[//]: # (* 覆盖率应保持在 100%。)

[//]: # (* 如果你认为 PR 有意义，或者我们讨论了它并认为它应该被接受，你可以在 PR 之上添加提交来调整它，添加文档、测试、格式化、重构、删除额外的文件等。)

[//]: # (* 欢迎在 PR 中发表评论以询问更多信息、提出更改建议等。)

[//]: # (* 一旦您认为 PR 已准备就绪，请将其移动到内部 GitHub 项目中供我审查。)

[//]: # ()
[//]: # (## 开发人员 PRs)

[//]: # ()
[//]: # (每个月，GitHub Action 都会更新 **开发人员** 数据. 这些 PR 如下所示： <a href="https://github.com/fastapi/fastapi/pull/11669" class="external-link" target="_blank">👥 Update Dev People</a>.)

[//]: # ()
[//]: # (如果测试通过，您可以立即合并它。)

[//]: # ()
[//]: # (## 外部链接 PR)

[//]: # ()
[//]: # ()
[//]: # (当人们添加外部链接时，他们会编辑此文件<a href="https://github.com/fastapi/fastapi/blob/master/docs/en/data/external_links.yml" class="external-link" target="_blank">external_links.yml</a>.)

[//]: # ()
[//]: # (* 确保新链接位于正确的类别 &#40;例如 "Podcasts"&#41; 和 语言 &#40;例如 "Chinese"&#41;.)

[//]: # ()
[//]: # (* 新链接应位于其列表的顶部。)

[//]: # ()
[//]: # (* 链接 URL 应该有效（它不应该返回 404）。)

[//]: # ()
[//]: # (* 链接的内容应该是关于 FastAPI-Channels 的。)

[//]: # ()
[//]: # (* 新添加的字段应包含以下字段：)

[//]: # ()
[//]: # (    * `author`: 作者名字。)

[//]: # ()
[//]: # (    * `link`: 包含内容的 URL。)

[//]: # ()
[//]: # (    * `title`: 链接的标题（文章、播客等的标题）。)

[//]: # ()
[//]: # (在检查了所有这些内容并确保 PR 具有正确的标签后，您可以合并它。)

## Dependabot PRs

Dependabot将创建PR来更新几件事的依赖关系，这些PR看起来都很相似，但有些比其他PR更微妙。

* 如果PR是直接依赖关系，那么Dependabot正在进行修改 `pyproject.toml`, **不要合并它**. 😱 让我先检查一下。 很有可能需要一些额外的调整或更新。
* 如果PR更新了一个内部依赖关系，例如它正在修改 `requirements.txt` 文件, 或者 GitHub Action 的版本, 如果测试通过，发布说明（在PR的摘要中显示）没有显示任何明显的潜在破坏性更改，您可以合并它。 😎

## 标记 GitHub Discussions 答案

当GitHub Discussions讨论中的问题得到回答后，单击"Mark as answer"标记答案。

你可以在 GitHub discussions 中筛选 哪些<a href="https://github.com/YGuang233/fastapi-channels/discussions/categories/questions?discussions_q=category:Questions+is:open+is:unanswered" class="external-link" target="_blank">`Questions` 还没有被 `Unanswered`的</a>。
