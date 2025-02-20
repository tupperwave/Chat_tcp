import socket
import threading
import customtkinter as ctk
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

# Configurações de criptografia DES
DES_KEY = b'chave8by'  # Chave DES de 8 bytes
DES_IV = b'iv8bytes'   # IV de 8 bytes para CBC

SERVER_PORT = 8000
BUFFER = 1024

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MyFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1216x684")
        self.title("Servidor")
        self.textbox = ctk.CTkTextbox(master=self, width=1216, height=657, corner_radius=25, font=('Helvetica bold',20))
        self.textbox.pack()

        widget_frame = ctk.CTkFrame(self)
        widget_frame.pack(side="top", anchor="n")

        self.entryText = ctk.CTkEntry(widget_frame, placeholder_text="Digite sua mensagem", width=500, font=('Helvetica bold',14))
        self.entryText.pack(side="left")  

        self.submitButton = ctk.CTkButton(widget_frame, text="enviar", command=self.submit)
        self.submitButton.pack(side="left")
        
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        self.flag = False
        self.client_socket = None

    def submit(self):
        text = self.entryText.get()
        if self.flag and self.client_socket:
            try:
                # Criptografa a mensagem
                plaintext = text.encode('utf-8')
                padded_plaintext = pad(plaintext, DES.block_size)
                cipher = DES.new(DES_KEY, DES.MODE_CBC, DES_IV)
                ciphertext = cipher.encrypt(padded_plaintext)
                self.client_socket.send(ciphertext)
                self.textbox.insert("end", f'Servidor: {text}\n')
                self.entryText.delete(0, ctk.END)
            except Exception as e:
                self.textbox.insert("end", f"Erro ao criptografar: {e}\n")
            self.flag = False

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', SERVER_PORT))
        self.server_socket.listen(1)
        self.textbox.insert("end", "Aguardando conexão do cliente...\n")
        self.accept_client()

    def accept_client(self):
        client_socket, client_address = self.server_socket.accept()
        self.client_socket = client_socket
        self.textbox.insert("end", f"Cliente {client_address[0]} conectado.\n")
        self.handle_client(client_socket)

    def handle_client(self, client_socket):
        while True:
            try:
                ciphertext = client_socket.recv(BUFFER)
                if not ciphertext:
                    break
                # Descriptografa a mensagem
                cipher = DES.new(DES_KEY, DES.MODE_CBC, DES_IV)
                padded_plaintext = cipher.decrypt(ciphertext)
                plaintext = unpad(padded_plaintext, DES.block_size)
                rec_message = plaintext.decode('utf-8')
                self.flag = True
                self.textbox.insert("end", f'Cliente: {rec_message}\n')

                if rec_message.lower() == "sair":
                    self.textbox.insert("end", "Cliente encerrou a conexão.\n")
                    break
            except Exception as e:
                self.textbox.insert("end", f"Erro ao descriptografar: {e}\n")
                break
        client_socket.close()

if __name__ == '__main__':
    app = App()
    app.mainloop()