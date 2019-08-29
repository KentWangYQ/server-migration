import logging
from socketserver import ThreadingTCPServer
from config import Service as ServiceConfig
from lib.tcp.server import FileHandler

logger = logging.getLogger('mig')

if __name__ == '__main__':
    serv = ThreadingTCPServer(('', ServiceConfig.PORT), FileHandler)
    serv.request_queue_size = 20  # 提高queue大小，应对多端请求
    try:
        logger.info('Server started')
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        serv.shutdown()
        serv.server_close()
        logger.info("Server stopped.")
