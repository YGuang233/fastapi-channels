---
comments: true
---

# action

action在`Channel`类的使用上展开，它将使用`Channel`的变得更像是一个FastAPI的子应用一样，虽然有些区别，没有get、post的请求方式，但是有action来接收对应动作

使用Channel也同时满足了像函数或是类的形式来编写逻辑，就像`CBV`和`FBV`一样，这里是有一点模仿DRF的痕迹在里面的，这里给我们的案例使用这两个名字来代替这两种写法
=== "CBV"
    ```python hl_lines="17-21"
    {!> ../../docs_src/action/tutorial001_cbv.py!}

    ```

=== "FBV"
    ```python hl_lines="18-21"
    {!> ../../docs_src/action/tutorial001_fbv.py!}

    ```

FBV更贴近fastapi的一般的使用形式，CBV更新DRF的CBV但是我们没有模型处理，只能说有些神韵罢了。

如上在不同形式下实现action的注册的方式是不一样的，`CBV`需要从`fastapi_channels.decorators`导入 action 装饰器 而`FBV`只需要调用实例化后的Channel的action装饰器实例方法，像fastapi那样

## 解码器
指定receiver中客户端发送的message被处理成dict()的过程

xxx

## 编码器
指定reply的形式

xoo

## 权限
