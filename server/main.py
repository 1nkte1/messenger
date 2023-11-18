import os
import glob
from openpyxl import load_workbook
import socket
import threading

database = load_workbook('database.xlsx')
sheet = database.active

def receive(client):
    try:
        data = b""
        while b"|" not in data:
            msg = client.recv(1024)
            if not msg:
                break
            data += msg
            data = data[:-1]
        return data.decode('utf-8')
    except Exception as e:
        print('receiving', e)

def transmit(client, message):
    try:
        client.send((str(message)+'|').encode('utf-8'))
    except Exception as e:
        print('transmitting', e)

def handle(client, address):
    print(f'connected to {address}')
    connection_lost = False
    ID = 0
    print(len(sheet['A']))

    def communication():
        nonlocal connection_lost
        nonlocal ID

        message = receive(client)
        if not message:
            connection_lost = True
            return

        print('message:', message)

        if message.startswith('login'):
            message = message[len('login'):]
            login, password = message.split(':')
            print('login:', login, 'password:', password)
            for cell in sheet['B']:
                if login == str(cell.value):
                    print('correct login!')
                    if password == cell.offset(column=1).value:
                        print('correct password!')
                        ID = int(cell.offset(column=-1).value)
                        transmit(client, '1' + str(ID))
                        return
            else:
                print('wrong login or password')
                transmit(client, '2')
                return

        elif message.startswith('signup'):
            username, login, password = message[len('signup'):].split(':')
            print(username, login, password)

            for cell in sheet['D']:
                if cell.coordinate != f'D{ID+1}' and username == str(cell.value):
                    transmit(client, 2)
                    return

            for cell in sheet['B']:
                if cell.coordinate != f'B{ID+1}' and login == str(cell.value):
                    transmit(client, 3)
                    return

            transmit(client, 1)
            ID = len(sheet['A'])
            sheet[f'A{ID+1}'] = ID
            sheet[f'B{ID+1}'] = login
            sheet[f'C{ID+1}'] = password
            sheet[f'D{ID+1}'] = username
            sheet[f'E{ID+1}'] = 0
            database.save("database.xlsx")
            return

        elif message.startswith('username'):
            transmit(client, sheet[f'D{ID+1}'].value)
            return

        elif message.startswith('editusername'):
            username = message[len('editusername'):]

            for cell in sheet['D']:
                if cell.coordinate != f'D{ID+1}' and username == str(cell.value):
                    transmit(client, 2)
                    return

            sheet[f'D{ID + 1}'] = username
            transmit(client, 1)
            database.save("database.xlsx")
            return

        elif message.startswith('editpassword'):
            password = message[len('editpassword'):]
            sheet[f'C{ID + 1}'] = password
            database.save("database.xlsx")
            return

        elif message.startswith('sendmsg'):
            def sendmsg(path, message):
                with open(path, 'a') as file:
                    file.write(message)

            message = message[len('sendmsg'):]
            print(message)
            friend_ID, contents = message.split('*')
            if friend_ID == 'None':
                sendmsg(f'{ID}.txt', contents)
            else:
                history1, history2 = f'{ID}-{friend_ID}.txt', f'{friend_ID}-{ID}.txt'

                if os.path.exists(history1):
                    sendmsg(history1, contents)
                elif os.path.exists(history2):
                    sendmsg(history2, contents)
                else:
                    sendmsg(history1, contents)
            return


        elif message.startswith('clearmsghistory'):
            def clearmsghistory(path):
                with open(path, 'w'):
                    pass

            friend_ID = message[len('clearmsghistory'):]
            if friend_ID == 'None':
                clearmsghistory(f'{ID}.txt')
            else:
                history1, history2 = f'{ID}-{friend_ID}.txt', f'{friend_ID}-{ID}.txt'
                if os.path.exists(history1):
                    clearmsghistory(history1)
                elif os.path.exists(history2):
                    clearmsghistory(history2)
                else:
                    clearmsghistory(history1)
            return

        elif message.startswith('loadmsghistory'):
            def loadmsghistory(path):
                with open(path, 'a+') as file:
                    file.seek(0)
                    # if file_size < 1024:
                    #     file.seek(0)
                    # else:
                    #     file.seek(file_size-1024)
                    contents = file.read()
                    transmit(client, contents)
                    print('success')
                    return

            friend_ID = message[len('loadmsghistory'):]

            if friend_ID == 'None':
                loadmsghistory(f'{ID}.txt')
            else:
                history1, history2 = f'{ID}-{friend_ID}.txt', f'{friend_ID}-{ID}.txt'
                if os.path.exists(history1):
                    loadmsghistory(history1)
                elif os.path.exists(history2):
                    loadmsghistory(history2)
                else:
                    loadmsghistory(history1)
            return

        elif message.startswith('findfriend'):
            username = message[len('findfriend'):]
            for cell in sheet['D']:
                if username == str(cell.value):
                    print('found!')
                    friend_ID = cell.offset(column=-3).value
                    transmit(client, f'1{friend_ID}')
                    return
            else:
                print('not found')
                transmit(client, '2')
                return

        elif message.startswith('getcontacts'):
            filenames = glob.glob('*.txt')
            logs = []
            for file in filenames:
                file = file[:-4]
                logs.append(file)

            contacts_ID = []
            for log in logs:
                if log == ID:
                    pass
                else:
                    try:
                        u1, u2 = log.split('-')
                        print(u1, u2)
                        if u1 == str(ID) or u2 == str(ID):
                            if u1 != str(ID):
                                contacts_ID.append(int(u1))
                            else:
                                contacts_ID.append(int(u2))
                    except:
                        pass

            contacts_usernames = ""
            if len(contacts_ID) == 0:
                transmit(client, 0)
                return
            else:
                for contact in contacts_ID:
                    username = sheet[f'D{contact+1}'].value
                    pfp = sheet[f'E{contact+1}'].value
                    contacts_usernames += f'{username}:{pfp}*'
                print(contacts_usernames)
                transmit(client, contacts_usernames)
                return

        elif message.startswith('getfriendID'):
            username = message[len('getfriendID'):]
            for cell in sheet['D']:
                if username == cell.value:
                    friend_ID = cell.offset(column=-3).value
                    transmit(client, friend_ID)
                    return

        elif message.startswith('getpfp'):
            index = sheet[f'E{ID+1}'].value
            transmit(client, index)

        elif message.startswith('editpfp'):
            index = message[len('editpfp'):]
            sheet[f'E{ID+1}'] = index
            database.save("database.xlsx")
            return

        else:
            print('unknown command >_<')
            transmit(client, '2')
            return

    while not connection_lost:
        communication()
def main():
    try:
        # host = '95.165.107.62'
        host = socket.gethostbyname(socket.gethostname())
        port = 8080

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()
        print('the server is online')

        while True:
            client, address = server.accept()

            thread = threading.Thread(target=handle, args=(client, address))
            thread.start()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()