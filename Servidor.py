import socket
import threading
import customtkinter as ctk

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

        self.entryText = ctk.CTkEntry(widget_frame, placeholder_text="Digite sua mensagem", width = 500, font=('Helvetica bold',14))
        self.entryText.pack(side="left")  

        self.submitButton = ctk.CTkButton(widget_frame, text="enviar", command=self.submit)
        self.submitButton.pack(side="left")
        
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True  # Allows the server thread to terminate when the main thread exits.
        self.server_thread.start()
        
        self.flag = False;
        self.client_socket = "";

    def submit(self):
        text = self.entryText.get()
        if self.flag:
            self.client_socket.send(bytes(text, "utf8"))
            self.flag = False
            self.textbox.insert("end", f'Servidor: {text}\n')
            self.entryText.delete(0, ctk.END)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', SERVER_PORT))
        self.server_socket.listen(1)
        self.textbox.insert("end", "Waiting for a client to connect...\n")
        self.accept_client()

    def accept_client(self):
        
        client_socket, client_address = self.server_socket.accept()
        self.client_socket = client_socket;
        self.textbox.insert("end", f"Client {client_address[0]} connected.\n")
        self.handle_client(client_socket)


    def handle_client(self, client_socket):
        while True:
            rec_message = client_socket.recv(BUFFER).decode("utf8")
            self.flag = True
            if not rec_message:
                break

            self.textbox.insert("end", f'Client: {rec_message}\n')

            if rec_message == "sair":
                self.textbox.insert("end", "Client terminated the connection.\n")
                break
        client_socket.close()
        

if __name__ == '__main__':
    app = App()
    app.mainloop()
