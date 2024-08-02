import socket

# 創建 socket 對象
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 綁定 IP 和端口
server_socket.bind(('localhost', 12345))

# 監聽連接
server_socket.listen(5)

print("Server is listening...")

while True:
    # 接受客戶端連接
    client_socket, addr = server_socket.accept()
    print(f"Connected by {addr}")

    # 接收數據
    data = client_socket.recv(1024)
    print(f"Server Received: {data.decode()}")

    # 發送數據
    client_socket.sendall(b"Hello, Client")

    # 關閉客戶端連接
    client_socket.close()
