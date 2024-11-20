---
comments: true
---

# 开始使用

让我们开始使用吧。

使用fastapi-channels不需要你做什么过多的操作，只需通过简单的几步就可以快速开始使用，并且方便的定制你的频道

```Python
{!> ../../docs_src/setup/tutorial001.py!}
```

就像上面这段代码这么简单，你就实现了一个简易的频道的搭建

接下来让我们仔细讲一讲这个代码吧😀

## 全局注册fastapi-channels

```Python hl_lines="3 7-12"
{!> ../../docs_src/setup/tutorial001.py!}
```

- *add_exception_handlers 设置为True将为我封装的`WebSocketException`添加异常捕获的处理机制，如果你不想使用这个可以设置为False再进行自定义，详细的异常机制你可以在[处理错误](exception.md)进行了解。
- *url 为fastapi-channels添加对应的broadcaster后端地址，也就是你用来进行消息订阅的后端应用程序的地址。
- *limiter_url 为fastapi-channels添加对应的fastapi-limiter地址，这个对应你用来做限流缓存的redis数据库。可能这里之后会进行扩展，但是现在请按照我们给你提供的方式来设置

这些只是简单的使用,实际上你还可以定义一些其他的内容来实现全局化设置：限流器、权限验证。


```python title="fastapi_channels/api.py"
{!> ../../fastapi_channels/api.py[ln:15-39]!}
```

## 自定义的范畴

你还可以自定义<a href="https://github.com/encode/broadcaster" class="external-link" target="_blank">Broadcaster</a>
和<a href="https://github.com/long2ice/fastapi-limiter" class="external-link" target="_blank">FastAPI-limiter</a>,
就跟平常使用这些一样，把定义好的对象传入，或者直接对对应的库进行自主设置

```python title="main.py" hl_lines="13-16 20 27"
{!> ../../docs_src/setup/tutorial002.py!}
```
!!! note
    FastAPILimiter的init方法是个类方法，所以我这里没有考虑传入。
    
    而且不止这一点，如果你想自己在lifespan中来初始化FastAPILimiter，像是`app(lifspan=lifspan)`是不可行的。

    因为通过add_channel合并了fastapi-channel的生命周期函数和fastapi的生命周期函数，合并的结果是我的初始化步骤在fastapi的`start_up`之前

我只是把他聚合到一个方法里，在你不想单独的一个个指定的时候，帮你完成全局注册和关闭程序的后续处理。

但是还是期望你能够使用add_channel来帮助你完成fastapi-channels的注册，同时这样与你的http接口中使用FastAPI-limiter的并不冲突

```python hl_lines="7"
{!> ../../docs_src/setup/tutorial003.py!}
```
