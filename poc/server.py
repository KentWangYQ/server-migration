# import socket
#
# tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# tcp_server_socket.bind(('', 8080))
# tcp_server_socket.listen(128)
# print('Server started and listen at 8080')
# while True:
#     client_socket, client_ip = tcp_server_socket.accept()
#     print('Client: ', client_ip, 'Connected')
#     file_name_data = client_socket.recv(1024)
#     file_name = file_name_data.decode()
#     # client_socket.send('Got file name')
#     try:
#         with open('data/server/' + file_name, 'wb') as file:
#             while True:
#                 file_data = client_socket.recv(1024)
#                 if file_data:
#                     file.write(file_data)
#                 else:
#                     print('File: ', file_name, ' send complete')
#                     break
#     except Exception as e:
#         print('Send Error', e)
#
#     client_socket.close()

from socketserver import BaseRequestHandler, TCPServer


class FileHandler(BaseRequestHandler):
    def handle(self):
        print('Got connection from: ', self.client_address)
        file_name = b''
        while True:
            _data = self.request.recv(1024)
            if not _data:
                break
            file_name += _data.decode()
            # self.request.send(b'file name received')

        file_path = b''
        while True:
            _data = self.request.recv(1024)
            if not _data:
                break
            file_path += _data.decode()
            # self.request.send(b'file path received')

        try:
            with open('data/server/%s/%s' % (file_path, file_name), 'wb') as file:
                while True:
                    _data = self.request.recv(1024)
                    if not _data:
                        break
                    file.write(_data)
        except Exception as e:
            print('Receive file failed: ', file_name, e)
        else:
            print('Receive file success: ', file_name)


if __name__ == '__main__':
    serv = TCPServer(('', 8080), FileHandler)
    serv.serve_forever()
