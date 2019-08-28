class Signal(object):
    """
    控制信号
    """
    INTERRUPT_CURRENT_REQUEST = b'0'  # 中断当前请求
    CLOSE = b'1'  # 连接关闭

    FILE_INFO_RECEIVED = b'10'  # 文件基本信息接收成功
    FILE_RECEIVED = b'11'  # 文件接收成功
    FILE_RECEIVE_FAILED = b'12'  # 文件接收失败
    SERVER_ERROR = b'13'  # 服务端错误
    FILE_SEND_COMPLETE = b'exit'  # 文件发送完成


DEFAULT_BUFFER_SIZE = 10240  # 默认buffer大小
SERVER_PORT = 8080  # 服务器默认端口
REQUEST_TIMEOUT = 60  # 请求超时时间

MAX_CLIENT_THREAD = 4  # 客户端进程数
