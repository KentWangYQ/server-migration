import os
import socket
import pickle
import logging
from socketserver import StreamRequestHandler
from config import Service as ServiceConfig
from lib.const import Signal, DEFAULT_BUFFER_SIZE, REQUEST_TIMEOUT

logger = logging.getLogger('mig')

root = ServiceConfig.ROOT + ('' if ServiceConfig.ROOT.endswith('/') else '/')


class FileHandler(StreamRequestHandler):
    """
    文件传输Handler
    """

    def handle(self):
        logger.info('Got Connection from: %s %s' % self.client_address)
        self.request.settimeout(REQUEST_TIMEOUT)
        try:
            while True:  # 使用循环实现长连接
                r = self.request.recv(8192)
                if r == Signal.CLOSE:
                    # 接收到客户端关闭信号，连接关闭
                    logger.info('Connection closed by client')
                    break
                elif r:
                    # 接收文件基本信息
                    file_dir, file_name = pickle.loads(r)
                    self.request.send(Signal.FILE_INFO_RECEIVED)

                    file_dir += '' if file_dir.endswith('/') else '/'

                    try:
                        path = '%s%s' % (root, file_dir)
                        if not os.path.exists(path):
                            os.makedirs(path)
                        # 接收并写入文件
                        with open('%s%s' % (path, file_name), 'wb') as file:
                            while True:
                                _data = self.request.recv(DEFAULT_BUFFER_SIZE)
                                if _data == Signal.FILE_SEND_COMPLETE or not _data:
                                    # 接收完成
                                    break
                                file.write(_data)
                    except IOError as e:
                        self.request.send(Signal.FILE_RECEIVE_FAILED)
                        logger.error('File write failed: %s %s %s' % (file_dir, file_name, e))
                    except Exception as e:
                        self.request.send(Signal.FILE_RECEIVE_FAILED)
                        logger.error('Receive file failed: %s %s %s' % (file_dir, file_name, e))
                    else:
                        # 文件接收成功，向客户端发送成功信号
                        self.request.send(Signal.FILE_RECEIVED)
                        logger.info('Receive file success: %s %s' % (file_dir, file_name))
        except socket.timeout:
            logger.warning('Request timeout')
            self.finish()
