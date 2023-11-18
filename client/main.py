#одинаковые юзернеймы+
#регистрация+
#время отправления - на клиенте а не на сервере+
#нажатие по enter+
#запуск на определенном месте на экране+
#трай эксепт с фотографиями
#видно всем не видно никому+
#информация

from sys import exit
import os
import datetime
import time
import socket
from threading import Thread
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter.font as font

#мессенджер
class messenger:
    def __init__(self):
        # self.ID = None
        self.establish_connection()

    #соединение с сервером
    def establish_connection(self):
        # host = socket.gethostbyname(socket.gethostname())
        host = '95.165.107.62'
        port = 8080
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))
            # print('connected!')
            self.login()
        #если сервер оффлайн
        except socket.error:
            self.offline_popup()
            # print('the server is offline')
            exit()

    #получение данных с сервера
    def receive(self):
        try:
            data = b""
            while b"|" not in data:
                message = self.client.recv(1024)
                if not message:
                    break
                data += message
                data = data[:-1]
            return data.decode('utf-8')
        except Exception as e:
            # print('receive', e)
            self.offline_popup()
            exit()

    #отправление данных на сервер
    def transmit(self, message):
        try:
            self.client.send((str(message) + '|').encode('utf-8'))
        except Exception as e:
            # print('transmit', e)
            self.offline_popup()
            exit()

    #оффлайн
    def offline_popup(self):
        offline = Tk()
        offline.geometry('150x100')
        offline.resizable(False, False)
        offline.title('messenger')
        offline_label = ttk.Label(offline, text='сервер оффлайн >_<')
        exit_button = ttk.Button(offline, text='закрыть', command=exit)
        offline_label.place(relx=0.5, rely=0.3, anchor='center')
        exit_button.place(relx=0.5, rely=0.8, anchor='center')

        offline.mainloop()

    def signup(self):
        def signup_send(event):
            if username_entry.get() == '' or login_entry.get() == '' or password_entry1.get() == '' or password_entry2.get() == '':
                wrong_label['text'] = 'заполните все поля'
                return
            for data in [username_entry.get(), login_entry.get(), password_entry1.get(), password_entry2.get()]:
                for char in data:
                    if char == ":" or char == "*":
                        wrong_label['text'] = 'недопустимые символы (:)'
                        return
            if len(username_entry.get()) > 10:
                wrong_label['text'] = 'слишком длинный юзернейм'
                username_entry.delete('10', 'end')
                return
            if password_entry1.get() != password_entry2.get():
                wrong_label['text'] = 'пароли не совпадают!'
                return
            if login_entry.get() == 'login' or password_entry1.get() == 'password':
                wrong_label['text'] = 'не-а'
                return

            self.transmit(f'signup{username_entry.get()}:{login_entry.get()}:{password_entry1.get()}')
            check = self.receive()
            if check == '1':
                messagebox.showinfo('success!', f'успешно!\nюзернейм: {username_entry.get()}\nлогин: {login_entry.get()}\nпароль: {password_entry1.get()}')
                with open('details.txt', 'w') as file:
                    file.write(f'{login_entry.get()}:{password_entry1.get()}')
                go_back()
            elif check == '2':
                wrong_label['text'] = 'этот юзернейм уже занят'
            else:
                wrong_label['text'] = 'этот логин уже занят'

        def go_back():
            signup_window.destroy()
            self.login()

        signup_window = Tk()
        signup_window.title('sign up')
        login_icon = PhotoImage(master=signup_window, file='icon.png')
        signup_window.iconphoto(True, login_icon)


        screen_width = signup_window.winfo_screenwidth()
        screen_height = signup_window.winfo_screenheight()
        x = int((screen_width / 2) - (280 / 2))
        y = int((screen_height / 2) - (150 / 2))
        signup_window.geometry("{}x{}+{}+{}".format(300, 200, x, y))

        signup_window.resizable(False, False)

        style1 = ttk.Style()

        style1.theme_use('alt')
        style1.configure('TLabel', background="#363636", foreground='#cacaca')
        style1.configure('TButton', background='#00564d', foreground="#cacaca")
        style1.map('TButton', background=[('active', '#00897b')], foreground=[('active', '#cacaca')])
        signup_window.configure(bg='#363636')

        # виджеты
        wrong_label = ttk.Label(signup_window, anchor="center", justify="center")
        back_button = ttk.Button(signup_window, text='<-', command=go_back)
        username_label = ttk.Label(signup_window, text='юзернейм\n(видно всем)', anchor="center", justify="center")
        username_entry = ttk.Entry(signup_window, width=30)
        login_label = ttk.Label(signup_window, text='логин\n(не видно\nникому)', anchor="center", justify="center")
        login_entry = ttk.Entry(signup_window, width=30)
        password_label1 = ttk.Label(signup_window, text='пароль')
        password_entry1 = ttk.Entry(signup_window, width=30)
        password_label2 = ttk.Label(signup_window, text='повторите\n   пароль')
        password_entry2 = ttk.Entry(signup_window, width=30)
        signup_button = ttk.Button(signup_window, text='зарегистрироваться', command=lambda: signup_send(None))

        wrong_label.grid(row=0, column=1)
        back_button.grid(row=0, column=0)
        username_label.grid(row=1, column=0)
        username_entry.grid(row=1, column=1)
        login_label.grid(row=2, column=0)
        login_entry.grid(row=2, column=1)
        password_label1.grid(row=3, column=0)
        password_entry1.grid(row=3, column=1)
        password_label2.grid(row=4, column=0)
        password_entry2.grid(row=4, column=1)
        signup_button.grid(row=5, column=1)

        signup_window.bind("<Return>", signup_send)

        signup_window.mainloop()

    #вход в аккаунт
    def login(self):
        # проверка правильности логина и пароля
        def login_password_check(event):

            for data in [login_entry.get(), password_entry.get()]:
                for char in data:
                    if char == ":" or char == "*":
                        wrong_label['text'] = 'недопустимые символы (:)'
                        return

            if login_entry.get() == 'login' or password_entry.get() == 'password':
                wrong_label['text'] = 'не-а'
                return

            self.transmit('login'+str(login_entry.get())+':'+str(password_entry.get()))
            response = self.receive()
            if response.startswith('1'):
                with open('details.txt', 'w') as file:
                    file.write(login_entry.get()+':'+password_entry.get())

                login_window.destroy()
                self.main_info()
                self.main_menu_place()
                self.root.mainloop()
            elif response == '2':
                wrong_label['text'] = '>_< некорректные данные'
            else:
                wrong_label['text'] = '>_< что-то не так'
                self.offline_popup()
                exit()

        def redirect():
            login_window.destroy()
            self.signup()

        def instant_login(login, password):
            for data in [login, password]:
                for char in data:
                    if char == ":" or char == "*":
                        return
            if login == 'login' or password == 'password':
                return

            self.transmit(f'login{login}:{password}')
            response = self.receive()
            if response.startswith('1'):
                self.main_info()
                self.main_menu_place()
                self.root.mainloop()
                return
            elif response == '2':
                with open('details.txt', 'w'):
                    pass
                self.login()
            else:
                self.offline_popup()
                exit()

        def instant_login_check():
            if os.path.exists('details.txt'):
                with open('details.txt', 'r') as file:
                    contents = file.read()

                if contents == '':
                    return
                else:
                    try:
                        login, password = contents.split(':')
                        instant_login(login, password)
                    except Exception:
                        with open('details.txt', 'w'):
                            pass
                        self.login()
            else:
                with open('details.txt', 'w'):
                    return

        instant_login_check()

        # окно
        login_window = Tk()
        login_window.title('login')
        try:
            login_icon = PhotoImage(master=login_window, file='icon.png')
            login_window.iconphoto(True, login_icon)
        except TclError:
            login_window.withdraw()
            messagebox.showwarning('ошибка', 'мессенджер не может быть запущен, потому что фотографии были изменены. переустановите приложение или обратитесь за помощью к разработчику\nkomaeda.nadezhda@gmail.com')
            exit()

        screen_width = login_window.winfo_screenwidth()
        screen_height = login_window.winfo_screenheight()
        x = int((screen_width / 2) - (200 / 2))
        y = int((screen_height / 2) - (100 / 2))
        login_window.geometry("{}x{}+{}+{}".format(200, 100, x, y))
        # login_window.eval('tk::PlaceWindow . center')
        # login_window.geometry('200x100')
        login_window.resizable(False, False)

        style1 = ttk.Style()
        style1.theme_use('alt')
        style1.configure('TLabel', background="#363636", foreground='#cacaca')
        style1.configure('TButton', background='#00564d', foreground="#cacaca")
        style1.map('TButton', background=[('active', '#00897b')], foreground=[('active', '#cacaca')])
        login_window.configure(bg='#363636')

        # виджеты
        wrong_label = ttk.Label(login_window, text='', anchor="center", justify="center")
        login_label = ttk.Label(login_window, text='логин')
        password_label = ttk.Label(login_window, text='пароль')
        login_entry = ttk.Entry(login_window, width=23)
        password_entry = ttk.Entry(login_window, show='*', width=23)
        login_button = ttk.Button(login_window, text='войти', command=lambda: login_password_check(None))
        signup_button = ttk.Button(login_window, text='зарегистрироваться', command=redirect)

        wrong_label.place(relx=0.5, rely=0.1, anchor='center')
        login_label.place(relx=0, rely=0.2)
        login_entry.place(relx=0.25, rely=0.2)
        password_label.place(relx=0, rely=0.42)
        password_entry.place(relx=0.25, rely=0.42)
        (login_button.place(relx=0.6, rely=0.7))
        signup_button.place(relx=0, rely=0.7)

        login_window.bind("<Return>", login_password_check)

        login_window.protocol("WM_DELETE_WINDOW", self.close_window)

        login_window.mainloop()

    def close_window(self):
        self.needs_updating_check = False
        exit()

    # основные штуки и все такое
    def main_info(self):
        def help():
            def copy():
                help_window.clipboard_clear()
                help_window.clipboard_append('komaeda.nadezhda@gmail.com')

            help_window = Toplevel()

            width = help_window.winfo_reqwidth()
            height = help_window.winfo_reqheight()
            x = int((help_window.winfo_screenwidth() / 2 - width / 2))
            y = int((help_window.winfo_screenheight() / 2 - height / 2))
            help_window.geometry("+{}+{}".format(x, y))

            help_window.grab_set()
            help_window.resizable(False, False)

            help_window.configure(bg='#363636')

            info_label = ttk.Label(help_window, text='возникли вопросы?\nkomaeda.nadezhda@gmail.com')
            copy_button = ttk.Button(help_window, text='скопировать')

            info_label.pack()
            copy_button.pack()

        # окно
        self.root = Tk()

        self.root.geometry('300x300')
        self.root.title('messenger')
        main_icon = PhotoImage(master=self.root, file='icon.png')
        self.root.iconphoto(True, main_icon)
        self.root.resizable(False, False)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (300 / 2))
        y = int((screen_height / 2) - (300 / 2))
        self.root.geometry("{}x{}+{}+{}".format(300, 300, x, y))

        # customtkinter.set_appearance_mode('dark')
        #темы
        dark_theme = ttk.Style()
        dark_theme.theme_use('alt')
        dark_theme.configure('TLabel', background="#363636", foreground='#cacaca')
        dark_theme.configure('TButton', background='#00564d', foreground="#cacaca")
        dark_theme.map('TButton', background=[('active', '#00897b')], foreground=[('active', '#cacaca')])
        dark_theme.configure('TScrollbar', background='#363636', troughcolor='#4a4a4a')
        dark_theme.map('TScrollbar', background=[('active', '#363636')], troughcolor=[('active', '#4a4a4a')])
        self.root.configure(bg='#363636')

        # переменные
        self.profile_click_check = False
        self.contacts_click_check = False
        self.edit_username_check = False

        #пфп
        try:
            self.profile_logo0 = PhotoImage(master=self.root, file='profile0.png')
            self.profile_logo1 = PhotoImage(master=self.root, file='profile1.png')
            self.profile_logo2 = PhotoImage(master=self.root, file='profile2.png')
            self.profile_logo3 = PhotoImage(master=self.root, file='profile3.png')
            self.profile_logo4 = PhotoImage(master=self.root, file='profile4.png')
        except TclError:
            self.root.withdraw()
            messagebox.showwarning('ошибка', 'мессенджер не может быть запущен, потому что фотографии были изменены. переустановите приложение или обратитесь за помощью к разработчику\nkomaeda.nadezhda@gmail.com')
            exit()

        self.transmit('getpfp')
        pfp_index = self.receive()

        if pfp_index == '0':
            self.profile_var = self.profile_logo0
        elif pfp_index == '1':
            self.profile_var = self.profile_logo1
        elif pfp_index == '2':
            self.profile_var = self.profile_logo2
        elif pfp_index == '3':
            self.profile_var = self.profile_logo3
        elif pfp_index == '4':
            self.profile_var = self.profile_logo4

        #юзернейм пользователя
        self.transmit('username')
        self.username = StringVar()
        self.username.set(self.receive())

        #юзернейм друга
        self.friend_username = StringVar(value='избранное')

        # профиль
        self.profile_button = ttk.Button(self.root, image=self.profile_var, command=self.profile_click)
        self.profile_label = ttk.Label(self.root, text='настройки')

        # контакты
        self.contacts_button = ttk.Button(self.root, text="друзья", command=self.contacts_click)

        # сообщения
        self.friend_ID = None
        self.messages_button = ttk.Button(self.root, text="сообщения", command=lambda: self.messages_click(self.friend_ID))

        #дополнительно

        self.exit_button = ttk.Button(self.root, text='закрыть', command=self.close_window)
        self.greeting = ttk.Label(self.root, textvariable=self.username, font=font.Font(size=25))
        self.help_button = ttk.Button(self.root, text='помощь', command=help)

        self.root.protocol("WM_DELETE_WINDOW", self.close_window)


    # нажатие на профиль
    def profile_click(self):
        # изменение юзернейма
        def edit_username():
            if self.edit_username_check:
                if self.username_entry.get() == '':
                    messagebox.showwarning("предупреждение", "юзернейм не может быть пустым")
                    return

                for char in self.username_entry.get():
                    if char == ":" or char == "*":
                        messagebox.showwarning("предупреждение", "недопустимые символы (:)")
                        return

                if len(self.username_entry.get()) > 10:
                    messagebox.showwarning("предупреждение", "слишком длинный юзернейм\nмаксимальная длина - 10 символов")
                    self.username_entry.delete('10', 'end')
                    return

                self.transmit(f'editusername{self.username_entry.get()}')
                check = self.receive()

                if check == '1':
                    self.username.set(self.username_entry.get())
                    self.username_entry.place_forget()
                    self.username_label.place(x=60, y=0)
                    self.edit_username_button['text'] = 'изменить юзернейм'
                    self.edit_username_check = False
                else:
                    messagebox.showwarning("предупреждение", "вы не можете использовать этот юзернейм:(")

            else:
                self.username_label.place_forget()
                self.username_entry.place(x=60, y=0)
                self.edit_username_button['text'] = 'сохранить изменения'
                self.edit_username_check = True

        # изменение пароля
        def edit_password():
            def save_password():
                if edit_password_entry.get() == '':
                    messagebox.showwarning("предупреждение", "пароль не может быть пустым!")
                    return
                if edit_password_entry.get() == 'password':
                    messagebox.showwarning("предупреджение", "вы не можете использовать этот пароль >:(")
                    return
                for char in edit_password_entry.get():
                    if char == ":" or char == "*":
                        messagebox.showwarning("предупреждение", "недопустимые символы (:)")
                        return
                self.transmit(f'editpassword{edit_password_entry.get()}')
                password_toplevel.destroy()

            password_toplevel = Toplevel()

            width = password_toplevel.winfo_reqwidth()
            height = password_toplevel.winfo_reqheight()
            x = int((password_toplevel.winfo_screenwidth() / 2 - width / 2)+25)
            y = int((password_toplevel.winfo_screenheight() / 2 - height / 2))
            password_toplevel.geometry("+{}+{}".format(x, y))

            password_toplevel.grab_set()
            password_toplevel.resizable(False, False)
            edit_password_label = ttk.Label(password_toplevel, text="введите новый пароль", anchor="center", justify="center")
            edit_password_entry = ttk.Entry(password_toplevel)
            save_changes_button = ttk.Button(password_toplevel, text='сохранить изменения', command=save_password)

            for i in [edit_password_label, edit_password_entry, save_changes_button]:
                i.pack()

        def edit_pfp():
            def choose_pfp(pfp_index):
                self.transmit(f'editpfp{pfp_index}')
                if pfp_index == '0':
                    self.profile_var = self.profile_logo0
                elif pfp_index == '1':
                    self.profile_var = self.profile_logo1
                elif pfp_index == '2':
                    self.profile_var = self.profile_logo2
                elif pfp_index == '3':
                    self.profile_var = self.profile_logo3
                elif pfp_index == '4':
                    self.profile_var = self.profile_logo4
                self.profile_button.configure(image=self.profile_var)
                pfps.destroy()

            pfps = Toplevel()

            width = pfps.winfo_reqwidth()
            height = pfps.winfo_reqheight()
            x = int((pfps.winfo_screenwidth() / 2 - width / 2)-50)
            y = int((pfps.winfo_screenheight() / 2 - height / 2)+50)
            pfps.geometry("+{}+{}".format(x, y))

            pfps.resizable(False, False)
            pfps.grab_set()

            pfp0 = ttk.Button(pfps, image=self.profile_logo0, command=lambda: choose_pfp('0'))
            pfp1 = ttk.Button(pfps, image=self.profile_logo1, command=lambda: choose_pfp('1'))
            pfp2 = ttk.Button(pfps, image=self.profile_logo2, command=lambda: choose_pfp('2'))
            pfp3 = ttk.Button(pfps, image=self.profile_logo3, command=lambda: choose_pfp('3'))
            pfp4 = ttk.Button(pfps, image=self.profile_logo4, command=lambda: choose_pfp('4'))


            column = 0
            for pfp in [pfp0, pfp1, pfp2, pfp3, pfp4]:
                pfp.grid(row=1, column=column)
                column += 1

        #выход из аккаунта
        def log_out():
            with open('details.txt', 'w'):
                pass
            self.root.destroy()
            self.login()

        # страница профиля
        self.username_label = ttk.Label(self.root, textvariable=self.username, anchor='center')
        self.online_label = ttk.Label(self.root, text='online')
        self.edit_username_button = ttk.Button(self.root, text='изменить юзернейм', command=edit_username, width=20)
        self.username_entry = ttk.Entry(self.root, textvariable=self.username, width=15)
        self.edit_password_button = ttk.Button(self.root, text='изменить пароль', command=edit_password, width=20)
        self.edit_pfp_button = ttk.Button(self.root, text='изменить фото', command=edit_pfp, width=20)
        self.logout_button = ttk.Button(self.root, text='выйти из аккаунта', command=log_out, width=20)

        # туда сюда нажатие
        if self.profile_click_check:
            self.profile_click_check = False
            self.main_menu_place()
        else:
            self.help_button.place_forget()
            self.greeting.place_forget()
            self.profile_label.place_forget()
            self.username_label.place(x=60, y=0)
            self.online_label.place(x=60, y=20)
            self.edit_username_button.place(relx=0.55, y=0)
            self.edit_pfp_button.place(relx=0.55, y=25)
            self.edit_password_button.place(relx=0.55, y=50)
            self.logout_button.place(relx=0.55, y=75)
            self.exit_button.configure(command=self.main_menu_place, text='главное меню')
            self.profile_click_check = True

    #нажатие на контакты
    def contacts_click(self):
        #нажатие на поиск
        def find_friend():
            # нажатие на кнопку сообщений
            def select_friend():
                self.friend_ID = result[1:]
                self.friend_username.set(self.search_entry.get())
                self.messages_click(self.friend_ID)

            if self.search_entry.get() == self.username.get():
                self.its_you_label['text'] = 'вы нашли себя!'
                self.friend_username_label.place_forget()
                self.add_friend_button.place_forget()
            else:
                self.add_friend_button.configure(command=select_friend)
                self.transmit(f'findfriend{self.search_entry.get()}')
                result = self.receive()

                if not result:
                    return
                if result.startswith('1'):
                    self.its_you_label['text'] = 'пользователь найден'
                    self.friend_username_label['text'] = self.search_entry.get()
                    self.friend_username_label.place(relx=0.5, rely=0.28, anchor='center')
                    self.add_friend_button.place(relx=0.5, rely=0.35, anchor='center')
                elif result == '2':
                    self.its_you_label['text'] = 'такой пользователь не существует >_<'
                    self.friend_username_label.place_forget()
                    self.add_friend_button.place_forget()

        def get_contacts():
            def press(username):
                self.friend_username.set(username)
                self.transmit(f'getfriendID{username}')
                self.friend_ID = self.receive()
                self.messages_click(self.friend_ID)

            def generate_page():
                x = 0
                y = 0.45
                for i in range(self.start, min(self.start+4, len(contacts))):
                    self.variables.append(f'contact{i}')
                    username, index = contacts[i].split(":")

                    img = self.profile_logo0
                    if index == '0':
                        img = self.profile_logo0
                    elif index == '1':
                        img = self.profile_logo1
                    elif index == '2':
                        img = self.profile_logo2
                    elif index == '3':
                        img = self.profile_logo3
                    elif index == '4':
                        img = self.profile_logo4

                    globals()[self.variables[i]] = ttk.Button(self.root, text=username, image=img, compound='top', command=lambda i=i: press(globals()[self.variables[i]]['text']))
                    globals()[self.variables[i]].place(relx=x, rely=y)
                    x += 0.25

            def forward():
                for i in range(self.start, min(self.start+4, len(self.variables))):
                    globals()[self.variables[i]].place_forget()

                self.start += 4
                generate_page()

                if len(contacts) <= self.start+4:
                    forward_button['state'] = 'disabled'
                back_button['state'] = 'normal'

            def back():
                for i in range(self.start, min(self.start + 4, len(self.variables))):
                    globals()[self.variables[i]].place_forget()

                self.start -= 4
                generate_page()

                if self.start <= 0:
                    back_button['state'] = 'disabled'
                forward_button['state'] = 'normal'

            self.transmit('getcontacts')
            contacts = self.receive()

            if contacts == '0':
                return

            self.contacts_label.place(relx=0, rely=0.39)

            contacts = contacts.rstrip('*')
            contacts = contacts.split('*')

            if len(contacts) > 4:
                forward_button = ttk.Button(self.root, text='->', command=forward)
                back_button = ttk.Button(self.root, text='<-', command=back, state='disabled')
                forward_button.place(relx=0.75, rely=0.76)
                back_button.place(relx=0, rely=0.76)

            self.variables = []
            self.start = 0
            generate_page()

        def open_saved():
            self.friend_username.set('избранное')
            self.friend_ID = None
            self.messages_click(self.friend_ID)


        #виджеты
        self.search_label = ttk.Label(self.root, text='поиск друзей', anchor="center", justify="center", width=35, font=font.Font(size=15))
        self.seach_username_label = ttk.Label(self.root, text='юзернейм')
        self.search_entry = ttk.Entry(self.root, width=25)
        self.search_button = ttk.Button(self.root, text='найти', command=find_friend)
        self.its_you_label = ttk.Label(self.root, text='', anchor="center", justify="center")

        self.friend_username_label = ttk.Label(self.root, anchor="center", justify="center")
        self.add_friend_button = ttk.Button(self.root, text='отправить сообщение')
        self.contacts_label = ttk.Label(self.root, text='мои друзья: ', state='hidden')
        self.saved_messages_button = ttk.Button(self.root, text='открыть избранное', command=open_saved, width=24)

        # туда сюда нажатие
        if self.contacts_click_check:
            for widget in self.root.winfo_children():
                widget.place_forget()
            self.contacts_click_check = False
            self.main_menu_place()
        else:
            self.contacts_click_check = True
            # убираем ненужное
            for widget in self.root.winfo_children():
                if widget not in [self.contacts_button, self.messages_button, self.exit_button]:
                    widget.place_forget()
            get_contacts()
            self.search_label.place(relx=0.5, rely=0.05, anchor="center")
            self.seach_username_label.place(relx=0, rely=0.1)
            self.search_entry.place(relx=0.22, rely=0.1)
            self.search_button.place(relx=0.75, rely=0.097)
            self.its_you_label.place(relx=0.5, rely=0.21, anchor='center')
            self.saved_messages_button.place(relx=0.25, rely=0.76)
            self.exit_button.configure(command=self.main_menu_place, text='главное меню')

    # нажатие на сообщения
    def messages_click(self, ID):
        # отправка сообщения
        def send_message(event):
            # убираем перенос строки
            def clear_everything():
                self.text_widget.delete('1.0', 'end')

            for char in self.text_widget.get('1.0', 'end'):
                if char == '*':
                    messagebox.showwarning('предупреждение', 'недопустимые символы (*)')
                    return
            self.msghistory.configure(state='normal')
            current_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            self.transmit(f"sendmsg{ID}*{current_time}\n{self.username.get()}:\n{self.text_widget.get('1.0', 'end')}\n")
            #сразу после запускаем удаление ненужного переноса строки
            self.root.after(1, clear_everything)

        def load_messages():
            while self.needs_updating_check:
                self.transmit(f'loadmsghistory{ID}')
                self.contents = self.receive()
                # self.idk.append(contents)
                time.sleep(0.5)

        def updating():
            try:
                self.msghistory.configure(state='normal')
                scroll_y = self.msghistory.yview()[0]
                scroll_x = self.msghistory.xview()[0]
                last = self.msghistory.get('1.0', 'end').strip()
                now = self.contents.strip()
                self.msghistory.delete('1.0', 'end')
                self.msghistory.insert('1.0', self.contents)
                if last == now:
                    self.msghistory.yview(MOVETO, scroll_y)
                    self.msghistory.xview(MOVETO, scroll_x)
                else:
                    self.msghistory.see('end')

                # self.idk = []
                self.msghistory.configure(state='disabled')
            except Exception:
                pass

            if self.needs_updating_check:
                self.root.update()
                self.root.after(ms=500, func=updating)


        def clear_msghistory():
            self.transmit(f'clearmsghistory{ID}')
            self.msghistory.configure(state='normal')
            self.msghistory.delete('1.0', 'end')
            self.msghistory.configure(state='disabled')

        def go_back():
            self.needs_updating_check = False
            self.main_menu_place()

        for widget in self.root.winfo_children():
            widget.place_forget()

        self.contents = ''
        self.needs_updating_check = True

        # страница сообщений
        self.back_button = ttk.Button(self.root, text="<-", command=go_back, width=3)
        self.current_friend = ttk.Label(self.root, textvariable=self.friend_username, anchor="center", justify="center", font=font.Font(size=12))
        self.clear_msghistory_button = ttk.Button(self.root, text='очистить', width=12, command=clear_msghistory)
        self.msghistory = Text(self.root, width=35, height=11, state='disabled', wrap='none')
        self.text_widget = Text(self.root, width=37, height=5)
        self.msghistory['font'] = ('Arial', 11)
        self.text_widget['font'] = ('Arial', 11)
        self.text_widget.bind('<Return>', send_message)
        self.text_widget.bind('<Key>', self.text_widget.see('end'))

        self.scrollbar = ttk.Scrollbar(self.root, command=self.msghistory.yview, orient='vertical')
        self.msghistory.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar2 = ttk.Scrollbar(self.root, command=self.msghistory.xview, orient='horizontal')
        self.msghistory.configure(xscrollcommand=self.scrollbar2.set)

        self.msghistory.configure(background='#303030', foreground='#cacaca')
        self.text_widget.configure(background='#303030', foreground='#cacaca', insertbackground='#cacaca')
        self.enter_message_label = ttk.Label(self.root, text='начните печатать')


        # размещение
        self.msghistory.place(relx=0, rely=0.1)
        self.text_widget.place(relx=0, rely=0.7)
        self.back_button.place(x=3, y=3)
        self.current_friend.place(relx=0.5, rely=0.05, anchor='center')
        self.clear_msghistory_button.place(relx=0.7, rely=0.01)
        self.scrollbar.place(relx=0.95, rely=0.1, height=165)
        self.scrollbar2.place(relx=0, rely=0.65, width=300)

        # self.idk = deque()
        update = Thread(target=load_messages)
        update.start()
        updating()

    #выход в главное меню
    def main_menu_place(self):
        self.profile_click_check = False
        self.contacts_click_check = False
        self.edit_username_check = False

        for widget in self.root.winfo_children():
            widget.place_forget()

        self.profile_button.place(relx=0, rely=0)
        self.profile_label.place(x=0, y=60)

        self.contacts_button.place(relx=0, rely=0.9)
        self.messages_button.place(relx=0.74, rely=0.9)
        self.exit_button = ttk.Button(self.root, text='закрыть', command=self.close_window)
        self.exit_button.place(relx=0.5, rely=0.943, anchor='center')
        self.greeting.place(x=60, y=0)
        self.help_button.place(relx=0.75, rely=0)

a = messenger()