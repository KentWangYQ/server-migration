import os
import pickle
import logging

logger = logging.getLogger('mig')

file_path = './data/persist/'
file_name = 'file_list.pkl'


def save(file_list):
    """
    持久化文件列表
    :param file_list: 文件列表
    :return:
    """
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    with open('%s%s' % (file_path, file_name), 'wb') as file:
        pickle.dump(file_list, file)


def recovery():
    """
    从持久化介质恢复文件列表
    :return: 文件列表
    """
    if not os.path.exists('%s%s' % (file_path, file_name)):
        return None
    with open('%s%s' % (file_path, file_name), 'rb') as file:
        return pickle.load(file)


def delete():
    """
    删除文件列表持久化文件
    :return:
    """
    if os.path.exists('%s%s' % (file_path, file_name)):
        try:
            os.remove('%s%s' % (file_path, file_name))
        except Exception as e:
            logger.warning('Delete file_all.pkl failed: %s' % e)
