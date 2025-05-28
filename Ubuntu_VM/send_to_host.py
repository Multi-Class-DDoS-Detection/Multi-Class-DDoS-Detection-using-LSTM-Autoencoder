import socket
import os
import sys
import time

def send_file(filepath, target_ip, target_port=12345):
    if not os.path.isfile(filepath):
        print(f"Error: File '{filepath}' not found!")
        return
    
    filesize = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
        client_socket.settimeout(600)
        
        print(f"Connecting to {target_ip}:{target_port}...")
        client_socket.connect((target_ip, target_port))
        header = f"{filename}:<separator>:{filesize}"
        client_socket.send(header.encode())
        
        time.sleep(0.5)
        buffer_size = 262144  
        start_time = time.time()
        
        with open(filepath, 'rb') as f:
            bytes_sent = 0
            while bytes_sent < filesize:
                data = f.read(buffer_size)
                if not data:
                    break
                    
                client_socket.sendall(data)
                bytes_sent += len(data)
                percent = (bytes_sent/filesize)*100
                elapsed = time.time() - start_time
                speed = bytes_sent / (elapsed * 1024 * 1024) if elapsed > 0 else 0
                
                print(f"Progress: {bytes_sent/(1024*1024):.2f}/{filesize/(1024*1024):.2f} MB ({percent:.1f}%) - {speed:.2f} MB/s", end='\r')
        
        total_time = time.time() - start_time
        avg_speed = filesize / (total_time * 1024 * 1024) if total_time > 0 else 0
        
        print(f"\nFile '{filename}' sent successfully!")
        print(f"Transfer complete! Time: {total_time:.2f} seconds, Avg Speed: {avg_speed:.2f} MB/s")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python send_to_host.py <filepath> <target_ip> [target_port]")
        print("Example: python send_to_host.py /path/to/data.csv 192.168.56.102 12345")
        sys.exit(1)
    filepath = sys.argv[1]
    target_ip = sys.argv[2]
    target_port = int(sys.argv[3]) if len(sys.argv) > 3 else 12345
    
    send_file(filepath, target_ip, target_port)