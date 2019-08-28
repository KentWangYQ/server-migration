import logging
from concurrent.futures import ThreadPoolExecutor
from lib.tcp.client import Client, ClientPool
from lib.data_coll import source_file
from lib.persist import file_all, file_done, file_failed
from lib.const import MAX_CLIENT_THREAD
from config import Service as ServiceConfig

logger = logging.getLogger('mig')


def send_file(info):
    """
    发送文件
    :param info:
    :return:
    """
    client = client_pool.get_client()  # 从连接池获取client
    path, file = info
    retry = 0
    while True:  # 失败重试
        retry += 1
        result, ex = client.send_file(path, file)
        if result:
            fd.add((path, file))  # 记录成功
            break
        elif retry >= ServiceConfig.MAX_RETRY:
            ff.add((path, file, ex))  # 记录失败
            break


if __name__ == '__main__':
    clients = [Client((ServiceConfig.IP, ServiceConfig.PORT)) for _ in range(MAX_CLIENT_THREAD)]
    client_pool = ClientPool(clients=clients)

    fd = file_done.FileDone()
    ff = file_failed.FileFailed()

    file_list = file_all.recovery()  # 从记录中恢复文件列表
    if file_list:
        # 存在文件列表记录，断点续传
        done = fd.get_all()
        file_list = [f for f in file_list if f not in done]  # 排除掉已经完成的文件
    else:
        # 不存在记录，新的同步
        file_list = [f for f in source_file.walk()]
        file_all.save(file_list)  # 持久化文件列表

    # 多线程执行
    with ThreadPoolExecutor(max_workers=MAX_CLIENT_THREAD) as executor:
        for result in executor.map(send_file, file_list):
            pass

    file_all.delete()
    fd.delete()
    client_pool.close()

    logger.info('=====================')
    logger.info('Files complete: %d' % fd.total)
    logger.info('Files failed: %d' % ff.total)
    logger.info('=====================')

    logger.info('Server migration success')
