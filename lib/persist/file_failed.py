import os
import pickle
from threading import Lock


class FileFailed(object):
    """
    上传失败文件管理器
    """
    file_path = './data/persist/'
    file_name = 'failed.pkl'

    w_lock = Lock()

    def __init__(self):
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        # 打开文件，因高频写入，保持常开，析构时关闭
        self.file_ab = open('%s%s' % (self.file_path, self.file_name), 'ab')
        self.total = 0

    def add(self, info):
        """
        添加失败文件
        :param info: 文件信息(file_path, file_name)
        :return:
        """
        if not os.path.exists(self.file_path):
            os.mkdir(self.file_path)
        with self.w_lock:
            pickle.dump(info, self.file_ab)
            self.total += 1

    def get_all(self):
        """
        获取所有失败的文件列表
        :return: 文件列表 or None
        """
        if not os.path.exists('%s%s' % (self.file_path, self.file_name)):
            return None
        with open('%s%s' % (self.file_path, self.file_name), 'rb') as file:
            while True:
                try:
                    yield pickle.load(file)
                except EOFError:
                    break
                except Exception:
                    return None

    def __del__(self):
        # 关闭文件
        self.file_ab.close()
