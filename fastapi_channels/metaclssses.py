class ActionConsumerMeta(type):
    """
    记录操作方法的元类
    Metaclass that records action methods
    """

    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)

        cls._actions = {}

        for attr_name, attr_value in attrs.items():  # 函数名、函数
            if hasattr(attr_value, "action"):
                action_name, action_desc = attr_value.action
                perm_call, perm_desc = attr_value.permission
                cls._actions[action_name] = (
                    attr_name,
                    perm_call,
                )  # 返回action对应的函数名和对应的权限验证
        return cls
