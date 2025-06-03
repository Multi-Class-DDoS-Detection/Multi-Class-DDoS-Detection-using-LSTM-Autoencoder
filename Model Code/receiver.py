import socket
import os
import time

def get_download_path():
    return r"./"  

def receive_file():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '0.0.0.0'
    port = 12345

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Waiting for incoming file on port {port}...")

        client_socket, address = server_socket.accept()
        print(f"Connected to {address}")
        client_socket.settimeout(600)

        header_data = client_socket.recv(1024).decode()
        filename, filesize = header_data.split(':<separator>:')
        filesize = int(filesize)

        print(f"Receiving file: {filename} ({filesize/1048576:.2f} MB)")

        downloads_dir = get_download_path()
        os.makedirs(downloads_dir, exist_ok=True)
        save_path = os.path.join(downloads_dir, filename)

        start_time = time.time()
        with open(save_path, 'wb') as f:
            bytes_received = 0
            buffer_size = 262144

            while bytes_received < filesize:
                data = client_socket.recv(min(buffer_size, filesize - bytes_received))
                if not data:
                    break
                f.write(data)
                bytes_received += len(data)

                percent = (bytes_received/filesize)*100
                elapsed = time.time() - start_time
                speed = bytes_received / (elapsed * 1024 * 1024) if elapsed > 0 else 0

                print(f"Progress: {bytes_received/(1024*1024):.2f}/{filesize/(1024*1024):.2f} MB ({percent:.1f}%) - {speed:.2f} MB/s", end='\r')

        total_time = time.time() - start_time
        avg_speed = filesize / (total_time * 1024 * 1024) if total_time > 0 else 0

        print(f"\nFile saved as: {save_path}")
        print(f"Transfer complete! Time: {total_time:.2f} seconds, Avg Speed: {avg_speed:.2f} MB/s")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        try:
            client_socket.close()
        except:
            pass
        server_socket.close()

if __name__ == "__main__":  # Fixed the main block
    receive_file()