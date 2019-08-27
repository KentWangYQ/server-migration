import socket, random

tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_client_socket.bind(('', random.randint(10000, 20000)))
r = tcp_client_socket.connect(('127.0.0.1', 8080))  # todo 随机端口
file_name = 'test.txt'
file_path = 'path1'
tcp_client_socket.send(file_name.encode())
# print(tcp_client_socket.recv(1024).decode())
tcp_client_socket.send(file_path.encode())
# print(tcp_client_socket.recv(1024).decode())

try:
    with open('data/client/' + file_name, 'rb') as file:
        while True:
            file_data = file.read(1024)
            if file_data:
                tcp_client_socket.send(file_data)
            else:
                break
except Exception as e:
    print('File download error', e)
else:
    print('File %s download complete' % file_name)

tcp_client_socket.close()
