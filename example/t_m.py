from fastapi_channels.throttling.base import _create_backend

if __name__ == '__main__':
    # Throttle.init(url="redis://localhost:6379")
    # print(_create_backend(url="redis://localhost:6379"))
    print(_create_backend(url="memory://"))