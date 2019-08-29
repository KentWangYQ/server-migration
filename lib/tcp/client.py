import os
import socket
import json
import time
import threading
import logging
from lib.const import Signal, DEFAULT_BUFFER_SIZE

logger = logging.getLogger('mig')


class Client(object):
    def __init__(self, address, auto_connect=True):
        """
        Socket client
        :param address: AF_INET address
        :param auto_connect: 自动连接
        """
        self.address = address
        self.sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if auto_connect:
            self.connect()

    def connect(self):
        """
        建立连接
        :return:
        """
        self.sock_client.connect(self.address)

    def close(self):
        """
        关闭连接
        :return:
        """
        # 先向服务器发送关闭信令
        self.sock_client.send(Signal.CLOSE)
        self.sock_client.recv(DEFAULT_BUFFER_SIZE)
        self.sock_client.close()

    def send_file(self, file_dir, file_name):
        """
        向服务器发送文件
        :param file_dir: 文件目录
        :param file_name: 文件名称
        :return:
        """
        file_dir += '' if file_dir.endswith('/') else '/'
        path = '%s%s' % (file_dir, file_name)
        if not os.path.exists(path):
            return False, FileNotFoundError()

        # 发送目录和文件名
        self.sock_client.send(json.dumps((file_dir, file_name)).encode())
        time.sleep(.1)
        r = self.sock_client.recv(DEFAULT_BUFFER_SIZE)

        if r != Signal.FILE_INFO_RECEIVED:
            #  服务端反馈文件信息接收失败
            return False, Exception('File info receive failed')

        # 发送文件
        try:
            with open(path, 'rb') as file:
                ret, offset = 0, 0
                while True:
                    # 零拷贝发送
                    ret = self.sock_client.sendfile(file, offset, DEFAULT_BUFFER_SIZE)
                    if ret == 0:
                        # 发送成功
                        self.sock_client.send(Signal.FILE_SEND_COMPLETE)
                        break

                    offset += ret
                    r = self.sock_client.recv(DEFAULT_BUFFER_SIZE)
                    if r != Signal.BUFFER_RECEIVED:
                        return False, Exception('Buffer receive failed')

            if self.sock_client.recv(DEFAULT_BUFFER_SIZE) != Signal.FILE_RECEIVED:
                # 服务端反馈文件接收失败
                return False, Exception('File info receive failed')
        except Exception as e:
            # 文件发送异常，向服务端发送终止信号
            self.sock_client.send(Signal.INTERRUPT_CURRENT_REQUEST)
            logger.error('File upload error: %s %s' % (path, e))
            return False, e
        else:
            # 发送成功
            logger.info('File upload complete: %s' % path)

            return True, None


class ThreadSelector(object):
    """
    资源池选择器(线程策略)

    每个线程分配一个固定的资源
    """

    def __init__(self):
        self.client_thread_mapping = {}
        self.lock = threading.Lock()

    def select(self, clients):
        """
        资源选择
        :param clients:
        :return:
        """
        _id = threading.get_ident()
        if _id in self.client_thread_mapping:
            return self.client_thread_mapping[_id]
        elif clients:
            with self.lock:
                client = clients.pop()
                self.client_thread_mapping[_id] = client
            return client
        else:
            raise Exception('There is no enough client')


class ClientPool(object):
    """
    Socket连接池
    """

    def __init__(self, clients, select_class=ThreadSelector):
        if not clients:
            raise Exception("No defined clients, you need to specify at least one client.")
        self.clients = clients
        self.free_clients = clients[:]
        self.selector = select_class()

    def get_client(self):
        """
        获取连接
        默认采用线程匹配策略
        :return:
        """
        return self.selector.select(self.free_clients)

    def close(self):
        """
        关闭池中所有连接
        :return:
        """
        for client in self.clients:
            client.close()
