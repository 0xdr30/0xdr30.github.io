import os, requests,shutil, subprocess, platform, pwd, grp
from itertools import dropwhile


cleaner = Cleaner()

# Functions

def run(command):
    return subprocess.getoutput(command)

def run_print(command):
    out = run(command)
    print(out)
    return out

def exists(file):
    if os.path.exists(file):
        os.remove(file)
    else:
        return


# install dependencies
run("apt update -y")
run("apt install python3-pip python3-bs4 python3-beautifulsoup4 2>/dev/null")

import lxml
from lxml.html.clean import Cleaner
from bs4 import BeautifulSoup

def get_readme():
    file = open('./README.desktop', 'r')
    file = file.readlines()
    newFile = []
    for i in file:
        newFile.append(i.split(" "))
    links = []
    for line in newFile:
        for string in line:
            if string.startswith('"https:') == True:
                links.append(string.strip())
        readme = links[0].strip('"')
        return readme

def create_html(link):
    exists("README.html")
    exists("README.txt")
    file = open("./README.html", "x")
    request = requests.get(link)
    file.write(requests.text)
    file.close

def get_content(link):
    content = lxml.html.tostring(cleaner.clean_html(lxml.html.parse(link)))
    return content

def remove_tags(html):
    soup = BeautifulSoup(html, "lxml")
    for data in soup(['style','script']):
        data.decompose()
    return ' '.join(soup.stripped_strings)

def convert_to_list(string):
    list = list(string.split('\n'))
    newList = string.split('\n')
    return newList

def temp_file():
    exists("temp.txt")
    data = ""
    shutil.copy2("./README.txt", "./temp.txt")
    with open('temp.txt', 'r') as file:
        data = file.read().rstrip()
    return data 

def new_readme(content):
    exists("README.html")
    exists("README.txt")
    file = open("./README.txt", "x")
    for line in content:
        file.write(line + "\n \n")
    file.close

def remove_items(list, item):
    res = [i for i in list if i != item]
    return res

def get_usernames(text):
    exists("temp.txt")
    exists("USERS.txt")
    readme = text.split(" ")
    readme = readme[readme.index('Authorized')+1:]
    target = readme.index('Competition')
    readme = readme[:target]
    readme = map(lambda s: s.strip(), readme)
    readme = remove_items(readme, "\n")
    readme = remove_items(readme, "")
    target = readme.index ("password:")
    readme = remove_items(readme, "Authorized")
    readme = remove_items(readme, "(you)")
    readme = remove_items(readme, "Administrators")
    readme = remove_items(readme, "Administrators:")
    readme = remove_items(readme, "and")
    readme = remove_items(readme, "Users")
    readme = remove_items(readme, "Users:")
    for line in range(len(readme)):
        try:
            target = readme.index('password:')
            readme.pop(target+1)
            readme.pop(target)
        except:
            continue
    file = open("USERS.txt", "x")
    for line in readme:
        file.write(line + "\n")

def create_files():
    readmeLink = get_readme()
    create_html(readmeLink)
    text = convert_to_list(remove_tags(get_content("./README.html")))
    new_readme(text)
    get_usernames(temp_file)
    
def check_sudo():
    if os.geteuid() != 0:
        print("Please run with sudo")
        exit(1)
    
def install_packages(packages):
        print ("Installing " + packages)
        run('apt update -y')
        run('apt install -y ' + packages)
        print("Finished installing " + packages)
        
def start_service(service):
        run('systemctl start ' + service)
        print("Running on Ubuntu 22.04")
        
def update_system():
    print("\n Update System...")
    run('sudo apt update -y')
    run('sudo apt upgrade -y')
    print("\nDone Updating system")
    
def user_audit():
    UID_MIN = int(run("awk '/^UID_MIN/ {print $2}' /etc/login.defs"))
    UID_MAX = int(run("awk '/^UID_MAX/ {print $2}' /etc/login.defs"))
    ME = run("logname")

    all_users = pwd.getpwall()
    users = []
    users.append(ME)
    return users

def group_audit():
    groups = grp.getgrall()
    sudo_group = None

    for group in groups:
        if group.gr_name == 'sudo':
            sudo_group = group
            break
        
    if sudo_group is None:
        print("Error: No Sudo Group Found!")
        exit(1)

def update_policies():
    print("Setting Secure Password Expiration")
    run("sed -i 's/PASS_MAX_DAYS    99999/PASS_MAX_DAYS     99/g' /etc/login.defs")
    
def check_users():
    try:
        user_file = open("USERS.txt", 'r')
        allowed_users = user_file.readlines()
        allowed_users = list(map(lambda s: s.strip(), allowed_users))
    except:
        print("Choice:\n"
              "1. Enter a comma seperated list of Usernames as is in the README\n"
              "2. Enter the name of a text file")
        allowed_users = input("User file unavailable. Please enter a comma seperated list of users beginning with authorized administrators: \n").split(", ")
        
    return allowed_users

def remove_unauthorized_users():
    current_users = user_audit()
    allowed_users = check_users()
    if current_users == allowed_users:
        print("Users are good! (Surprisingly :D)")
    elif current_users != allowed_users:
        for user in current_users:
            if user not in allowed_users:
                print("Deleting unauthorized user '" + user + "'!")
                run("deluser " + user)

    admins_count = int(input("How many administrators are there?: \n"))
    current_users = user_audit()
    for user in current_users:
        if user < admins_count:
            continue
        elif user > admins_count:
            run("deluser " + user + " sudo")




    
    
def change_passwords():
    allowed_users = check_users()
    for user in allowed_users:
        print("Changing password for '" + user + "'!")
        run("passwd " + user)

def activate_firewall():
    install_packages("ufw")
    run("ufw enable")
    run("ufw logging on")
    
def install_antivirus():
    run("apt install clamav")
    run("clamscan")
    
    
def remove_pup():
    run("apt purge wireshark samba apache2 ftp vsftp bfgminer netcat john nmap")
### END OF FUNCTION DEFINITIONS ###


### START OF SCRIPT ###

def main():
    check_sudo()
    try:
        create_files()
    except:
        print("Cannot Create User File.")
        continue
    
    update_system()
    
    remove_unauthorized_users()
    
    print("Please input a secure password containing:\n "
          "2 Special Characters\n"
          "2 Capital Letters\n"
          "No common dictionary items\n")
    your_password = input("Enter your password here: \n")

    run("echo " + your_password + " > your_password.txt")

    print("Refer to your_password.txt for your password")

    change_passwords()
    
    activate_firewall()
    
    install_antivirus()
    
    
    

main()
    