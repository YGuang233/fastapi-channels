---
comments: true
---

# 频道类

你可以发现本项目主要围绕着`频道管理管理类`展开的

这样我们就不得不来仔细说明一下这两个类的区别了

## BaseChannel类

一切的基础，如果道家中说”一生万物“，那么这个 **BaseChannel类** 就是本项目的一了，它是本项目中最核心最基础的频道管理类了。

它比起它的子类 **Channel** 来说基本上它不做什么，当然它也会处理一些基础的任务：

### 频道名的定义

频道名的定义有三种方式，一种是在类的初始化前，一种是初始化进行定义，初始化前的那种我期望的是你通过类的形式编写频道类，初始化时是我期望你通过函数的形式来编写频道类

最后一种是在connect方法（实例化方法）传入,，这将使得channel name的定义更加抽象又具体，你可以在上面两种方法定义对应的模板，然后在connect中使用它

=== "初始化前"
    ```python hl_lines="16"
    {!> ../../docs_src/classes/tutorial001_class.py!}

    ```

=== "初始化"
    ```python hl_lines="12"
    {!> ../../docs_src/classes/tutorial001_init.py!}
    
    ```

=== "connect方法"
    ```python hl_lines="18"
    {!> ../../docs_src/classes/tutorial001_connect.py!}

    ```
这三种定义channel的优先级时依次递进的，实际上就是类方法<初始化方法<实例化方法。

所以这三种只需要定义了一种就行，如果都没有定义将会使用`default_channel`这个频道名

### 最大连接数限制

=== "初始化前"
    ```python hl_lines="16"
    {!> ../../docs_src/classes/tutorial001_class.py!}

    ```
=== "初始化"
    ```python hl_lines="13"
    {!> ../../docs_src/classes/tutorial002_init.py!}
    ```

`max_connection`默认为`None`将不对连接数进行限制，如果为正整数才会对其加入频道前做是否超过最大连接数的验证

强调：这样设置只是一个频道的最大可连接数，不是对应的房间人数限制，实际上房间人数

单用户多端登陆最大的连接数的互踢可以看[这里]()的实现

### 基础的权限验证

BaseChannel类及其子类的所有权限验证都可以输入： [`BasePermission`]('模仿DRF的一个权限类,会调用对应的has_permission方法，返回bool'), [`Callable`]('返回bool的可调用对象'), `bool`, [**`None`**]('这将被视为True')

详细内容请阅读 [权限验证](permission.md)

### 基础的限流

主要使用了fastapi-limiter库，详情请阅读 [限流器](limiter.md) ,通过简单的定义就可以设置对应的房间的访问流量

### 频道广播和个人广播

可以选择性的广播到个人还是频道，通过`broadcast_to_channel`和`broadcast_to_personal`

在进行对应的广播的时候，有着不同的参数需求

```python
await channel.broadcast_to_channel(
    channel=channel, message='Hello, Channel!'
)

await channel.broadcast_to_personal(
    websocket=channel, message='Hello, Channel!'
)
```

广播到频道需要频道名这意味着，你仅需要知道对应的频道名就能将message发送对应频道的连接用户

而广播到个人需要websocket对象，这实际上和`websocket.send()`的作用是一样的，只不过通过`broadcast_to_personal`可以做一些额外的操作，比如序列化数据把字典转换为str类型的message发送出去，不需要反复手动转换

### 生命周期事件

用于加入频道之前进行的触发事件和离开频道触发的事件。这一切发生在基础的权限验证和限流之后展开，频道限流会在请求过程中会一直运作的。
详细请阅读 [生命周期](../advanced/lifespan.md) ，如果你不想了解这些步骤，那么只需要思考如何重写receiver方法

但同时他有着大量的留白在接收和做出回复中,你只需要重写BaseChannel类的receiver方法，处理接收内容并作出对应回复

```Python hl_lines="8-15"
{!> ../../docs_src/classes/tutorial003.py!}
```

总得来说BaseChannel类它只是构建了一个有着基础功能的频道，在满足基本的连接条件后只是单纯的收发，中间的数据处理还是需要自己根据项目的需求来设计

## Channel类

当你用习惯了Channel类，基本上不会在使用BaseChannel类了，封装的Channel类不止继承了BaseChannel类的功能，还实现了`action`
，没错是动作，在前端传输不同的action就能做出对应的动作，就像是一问一答。

而使用BaseChannel类每次在一个新项目、和之前一样的处理的频道，就需要反复重写receiver方法，否则在满足基本的连接条件后只是单纯的收发，不利于快速的构建业务逻辑。

我知道每个人在不同的action有不同的权限和限流的限制，所以在继承BaseChannel类的功能上又增强了这些功能的应用，以应对不同的场景需求。

而Channel类做的处理只是那种恰到好处的处理，不多做处理，并且也留下了很多自定义更改的方式，以一种高可变，快速的编码效率。