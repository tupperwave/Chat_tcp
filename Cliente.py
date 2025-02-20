import socket
import sys
import threading
import customtkinter as ctk
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

# Configurações de criptografia DES (deve ser igual ao servidor)
DES_KEY = b'chave8by'  # Chave DES de 8 bytes
DES_IV = b'iv8bytes'   # IV de 8 bytes para CBC

SERVER_PORT = 8000
BUFFER = 1024

ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class MyFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1216x684")
        self.title("Client")
        
        self.textbox = ctk.CTkTextbox(master=self, width=1216, height=657, corner_radius=25, font=('Helvetica bold', 20))
        self.textbox.pack()

        widget_frame = ctk.CTkFrame(self)
        widget_frame.pack(side="top", anchor="n")

        self.entryText = ctk.CTkEntry(widget_frame, placeholder_text="Digite sua mensagem", width=500, font=('Helvetica bold', 14))
        self.entryText.pack(side="left")  

        self.submitButton = ctk.CTkButton(widget_frame, text="Enviar", command=self.submit)
        self.submitButton.pack(side="left")  

        self.connection = self.connecting()

    def submit(self):
        text = self.entryText.get()
        threading.Thread(target=self.conversation, args=(text,)).start()

    def connecting(self):
        value = "127.0.0.1"
        return self.start_connection(value)
    
    def checking_ip_address(self, ip_address):
        print("Checkando IP")
        parts = ip_address.split(".")
        if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
            return True
        print("Terminando o programa... cheque se o endereço de IP foi corrigido!")
        sys.exit()
        
    def start_connection(self, ip_address):
        print("Tentando se conectar ao servidor...")
        self.checking_ip_address(ip_address)
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            destino = (ip_address, SERVER_PORT)
            connection.connect(destino)
        except (ConnectionError, OSError) as erro:
            print("Conexão recusada. Tipo do erro:", type(erro))
            sys.exit()

        return connection

    def close_connection(self):
        print("Terminando a conexão...")
        self.connection.close()

    def start_listening(self):
        while True:
            try:
                ciphertext = self.connection.recv(BUFFER)
                if ciphertext:
                    # Descriptografa a mensagem recebida
                    cipher = DES.new(DES_KEY, DES.MODE_CBC, DES_IV)
                    padded_plaintext = cipher.decrypt(ciphertext)
                    plaintext = unpad(padded_plaintext, DES.block_size)
                    rec_mensagem = plaintext.decode('utf-8')
                    self.textbox.insert("end", f'Servidor: {rec_mensagem}\n')
                    if rec_mensagem.lower() == "sair":
                        self.textbox.insert("end", f"O lado do servidor terminou a conexão. Informe 'sair' para terminar a conexão\n")
                        self.close_connection()
                        break
            except ConnectionError as erro:
                print(erro)
                self.textbox.insert("end", f"Erro de conexão\n")
                self.close_connection()
                break

    def conversation(self, text): 
        self.entryText.delete(0, ctk.END)
        if text != "":
            try:
                # Criptografa a mensagem antes de enviar
                plaintext = text.encode('utf-8')
                padded_plaintext = pad(plaintext, DES.block_size)
                cipher = DES.new(DES_KEY, DES.MODE_CBC, DES_IV)
                ciphertext = cipher.encrypt(padded_plaintext)
                self.connection.send(ciphertext)
                self.textbox.insert("end", f'Você: {text}\n')
                if text.lower() == "sair":
                    self.close_connection()
                    return
            except Exception as e:
                self.textbox.insert("end", f"Erro ao criptografar: {e}\n")

if __name__ == '__main__':
    app = App()
    listening_thread = threading.Thread(target=app.start_listening)
    listening_thread.daemon = True
    listening_thread.start()
    app.mainloop()