---
comments: true
---

# 生命周期事件

类似**FastAPI**支持定义在应用启动前，或应用关闭后执行的事件处理器（函数）

**FastAPI-Channels**也有对应的生命周期函数(on_join、on_leave、lifespan)，用于用户加入频道和退出频道进行的操作。
这对于设置你需要在单次连接中使用的资源非常有用，这些资源在请求之间共享，你可能需要在之后进行释放。例如，数据库连接池，或加载一个共享的机器学习模型。

这一切主要依靠`contextlib`的上下文管理器来实现的来实现的😉

## 用例

```python
from contextlib import asynccontextmanager
from fastapi_channels.channels import Channel
from fastapi import FastAPI
app=FastAPI()
c=Channel()

```

## 替代事件（即将启用）

### `join` 事件
使用 `join` 事件
### `leave` 事件
