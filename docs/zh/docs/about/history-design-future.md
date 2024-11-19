---
comments: true
search:
  exclude: true
---

# 历史、设计、未来

&nbsp;&nbsp;这里记录这个项目的选型、设计还有开发的历史

## 为什么是 FastAPI 和 Broadcaster

&nbsp;&nbsp;在一次项目开发途中，为了扩展我的技术栈，不再重复的书写**Django**、**DRF**框架的项目，同时也想学习不一样的Python后端框架，我偶然接触**FastAPI**并开始学习，并用它完成了一个简单的项目。

&nbsp;&nbsp;我惊奇的发现这个框架的美妙之处，我是很欣喜有这么一个Python的异步WEB框架，它便捷且高效，不仅易于开发还易于生产。我也想为它做一些贡献，我在使用过程中发现了WebSocket接口上大有可为。

&nbsp;&nbsp;而在我开始书写基于Redis的PUB/SUB的流程后，却发现**Fastapi**早在文档中给了一个非常好的WebSocket高级用法的参考<a href="https://docs.pydantic.dev/" class="external-link" target="_blank">**Broadcaster**</a>。

&nbsp;&nbsp;我去仔细阅读和使用了**Broadcaster**后，我盯着我自己写的丑陋的代码陷入了沉思……“就决定是它了！”。🤓




## 调研

&nbsp;&nbsp;正巧那时我在使用channel库，单纯的使用channels库还需要不少理解，于是我又接触了**djangochannelsrestframework**，它的扩展方式给我提供了一种思路。

&nbsp;&nbsp;最终我结合我自己开发的需求，以及对fastapi http 接口编写形式的追求来实现这么一个fastapi 接口的扩展库。


## 设计

主要想通过**action**装饰器上做一些手脚来实现fastapi get()的效果，让他们可以传递相同的参数，哦不，应该说是超集，
它还要处理一些别的请求如权限，我知道这项功能似乎只用**dependencies**、**Depends**就能够实现的，但是你知道的我毕竟也使用过DRF的，我想先保留一些它的影子，
因为我也很喜欢DRF,如果大家不愿意，之后我再删去或者写成单独的模块

## 需求项

<a href="https://docs.pydantic.dev/" class="external-link" target="_blank">**Pydantic**</a>，负责 数据 部分。我将充分利用它的优势，它能够像fastapi的get请求那样对接收的数据做出对应的类型处理

<a href="https://github.com/encode/broadcaster" class="external-link" target="_blank">Broadcaster</a> 负责 通讯 部分。他不仅实现了redis的PUb/SUB还支持了:postgres、kafka、memory，我实在拒绝不了这样一个现成且完善的项目

<a href="https://github.com/long2ice/fastapi-limiter" class="external-link" target="_blank">Fastapi-Limiter</a> 负责 限流 部分。实际上我想提供fastapi常用的限流库的兼容支持，目前就是实现了这么一个。

## 未来

**FastAPI-Channels** 实在是有很多改进的地方，也还需要添加更多的功能，很多我想的也未曾实现或者很好的实现。

希望**FastAPI-Channels**有用武之地，或者这种开发模式能给你们一种参考。

在此，我们衷心感谢[您的帮助](help-fastapi-channels.md){.internal-link target=_blank}。
