import socket
import sys
import threading

import customtkinter as ctk

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
        self.conversation(text)

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
        except ConnectionError as erro:
            print("Conexão recusada. Tipo do erro:", type(erro))
            sys.exit()

        return connection

    def close_connection(self):
        print("Terminando a conexão...")
        self.connection.close()

    def start_listening(self):
        while True:
            try:
                rec_mensagem = self.connection.recv(BUFFER).decode("utf8")
                if rec_mensagem:
                    self.textbox.insert("end", f'Servidor: {rec_mensagem}\n')
                    if rec_mensagem == "sair":
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
            self.connection.send(bytes(text, "utf8"))
            self.textbox.insert("end", f'Você: {text}\n')
            if text == "sair":
                self.close_connection()
                return

if __name__ == '__main__':
    app = App()
    listening_thread = threading.Thread(target=app.start_listening)
    listening_thread.daemon = True
    listening_thread.start()
    app.mainloop()
