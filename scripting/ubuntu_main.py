import os, requests,shutil, subprocess, platform, pwd, grp
from itertools import dropwhile

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
#run("apt update -y")
run("apt -f install")
run("apt install python3-lxml python3-psutil python3-bs4 python3-beautifulsoup4 python3-psutil 2>/dev/null")

import lxml
from lxml.html.clean import Cleaner
from bs4 import BeautifulSoup
import psutil
cleaner = Cleaner()
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
    run('apt install -y ' + packages)
    print("Finished installing " + packages)
        
def start_service(service):
        run('systemctl start ' + service)
        
def update_system():
    print("\n Update System...")
    run('sudo apt update -y')
    run('sudo apt upgrade -y')
    print("\nDone Updating system")
    
def user_audit():
    UID_MIN = int(run("awk '/^UID_MIN/ {print $2}' /etc/login.defs"))
    UID_MAX = int(run("awk '/^UID_MAX/ {print $2}' /etc/login.defs"))
    users = []
    all_users = pwd.getpwall()
    for user in all_users:
        if user.pw_uid in range(UID_MIN, UID_MAX):
            users.append(user.pw_name)
    print(users)
    return users

def group_audit():
    groups = grp.getgrall()
    sudo_group = None

    for group in groups:
        if group.gr_name == 'sudo':
            sudo_group = group
            break
        
    if sudo_group is None:
        print("Error: No Sudo Group Found!\n Exiting \n")
        exit(1)
    return groups

def update_policies():
    print("Setting Secure Password Expiration\n")
    run("sed -i '/PASS_MAX_DAYS/c\\PASS_MAX_DAYS   99' /etc/login.defs")
    run("sed -i '/PASS_MIN_DAYS/c\\PASS_MIN_DAYS   5' /etc/login.defs")
    run("sed -i '/PASS_WARN_AGE/c\\PASS_WARN_AGE   7' /etc/login.defs")
    print("Setting Secure Password Content Requirements\n")
    run("sed -i '/minlen/c\\minlen = 14' /etc/security/pwquality.conf")
    run("sed -i '/dcredit/c\\dcredit = -2' /etc/security/pwquality.conf")
    run("sed -i '/ucredit/c\\ucredit = -2' /etc/security/pwquality.conf")
    run("sed -i '/lcredit/c\\lcredit = -2' /etc/security/pwquality.conf")
    run("sed -i '/ocredit/c\\ocredit = -2' /etc/security/pwquality.conf")
    run("sed -i '/maxrepeat/c\\maxrepeat = -1' /etc/security/pwquality.conf")
    run("touch common-password-up")
    f = open("./common-password-up", "a")
    f.write("password       requisite       pam_pwquality.so retry=3 minlen=10 dcredit=-2 ucredit=-2 lcredit=-2 ocredit=-2")
    f.write("password       [success=1 default=ignore]      pam_unix.so obscure use_authtok try_first_pass sha512 remember=5")
    f.write("password       requisite       pam_deny.so")
    f.write("password       required        pam_permit.so")
    f.write("password	    optional	    pam_gnome_keyring.so")
    run("mv common-password-up /etc/pam.d/")
    run("rm -r /etc/pam.d/common-password")
    run("mv /etc/pam.d/common-password-up /etc/pam.d/common-password")
    run("sed -i '/PermitRootLogin/c\\PermitRootLogin no' /etc/ssh/sshd_config")
    run("sed -i '/FAILLOG_ENAB/c\\FAILLOG_ENAB yes' /etc/login.defs")
    run("sed -i '/LOG_UNKFAIL_ENAB/c\\LOG_UNKFAIL_ENAB yes' /etc/login.defs")
    run("sed -i '/LOG_OK_LOGINS/c\\LOG_OK_LOGINS yes' /etc/login.defs")
    run("sed -i '/SYSLOG_SU_ENAB/c\\SYSLOG_SU_ENAB yes' /etc/login.defs")
    run("sed -i '/SYSLOG_SG_ENAB/c\\SYSLOG_SG_ENAB yes' /etc/login.defs")
    run("sed -i '/SULOG_FILE/c\\SULOG_FILE /var/log/sulog' /etc/login.defs")
    run("sed -i '/FTMP_FILE/c\\FTMP_FILE /var/log/btmp' /etc/login.defs")
    run("sed -i '/SU_NAME/c\\SU_NAME su' /etc/login.defs")
    run("sed -i '/LOGIN_RETRIES/c\\LOGIN_RETRIES 5' /etc/login.defs")
    run("sed -i '/LOGIN_TIMEOUT/c\\LOGIN_TIMEOUT 60' /etc/login.defs")
    run("sed -i '/ENCRYPT_METHOD/c\\ENCRYPT_METHOD sha512' /etc/login.defs")

    
def cleanup_system():
    run("nano /etc/apt/sources.list")
    run("nano /etc/resolv.conf") #use 8.8.8.8
    run("nano /etc/hosts") # no redirects
    run("nano /etc/rc.local") # only exit 0
    run("nano /etc/sysctl.conf") # change net.ipv4.tcp_syncookies to enabled
    run("apt -V -y install firefox hardinfo chkrootkit iptables portsentry lynis ufw gufw sysv-rc-conf nessus clamav")
    run("apt -V -y install --reinstall coreutils")
    run("apt update")
    run("apt ugrade")
    run("apt dist-upgrade")
    run("iptables -A INPUT -p tcp -s 0/0 -d 0/0 --dport 23 -j DROP")
    run("iptables -A INPUT -p tcp -s 0/0 -d 0/0 --dport 2-49 -j DROP")
    run("iptables -A INPUT -p udp -s 0/0 -d 0/0 --dport 2049 -j DROP")
    run("iptables -A INPUT -p tcp -s 0/0 -d 0/0 --dport 6000:6009 -j DROP")
    run("iptables -A INPUT -p tcp -s 0/0 -d 0/0 --dport 7100 -j DROP")
    run("iptables -A INPUT -p tcp -s 0/0 -d 0/0 --dport 515 -j DROP")
    run("iptables -A INPUT -p udp -s 0/0 -d 0/0 --dport 515 -j DROP")
    run("iptables -A INPUT -p tcp -s 0/0 -d 0/0 --dport 111 -j DROP")
    run("iptables -A INPUT -p udp -s 0/0 -d 0/0 --dport 111 -j DROP")
    run("iptables -A INPUT -p all -s localhost  -i eth0 -j DROP")
    run("ufw enable")
    run("ufw deny 23")
    run("ufw deny 2049")
    run("ufw deny 515")
    run("ufw deny 111")
    run("lsof -i -n -P")
    run("netstat -tulpn")
    run("find / -name '*.mp3' -type f -delete")
    run("find / -name '*.mov' -type f -delete")
    run("find / -name '*.mp4' -type f -delete")
    run("find / -name '*.avi' -type f -delete")
    run("find / -name '*.mpg' -type f -delete")
    run("find / -name '*.mpeg' -type f -delete")
    

    
def iptables_update():
    print("Please refer to the iptables_rules document on your desktop!")
    run("iptables -L > /home/" + ME + "/Desktop/iptables_rules.txt")
def check_users():
    allowed_users = ['']
    try:
        user_file = open("USERS.txt", 'r')
        allowed_users = user_file.readlines()
        allowed_users = list(map(lambda s: s.strip(), allowed_users))
    except:
        while allowed_users == ['']:
            allowed_users = input("\nPlease enter a comma seperated list of authorized users: \n").split(", ")
    allowed_users_lower = []
    for user in allowed_users:
        allowed_users_lower.append(user.lower())
    return allowed_users_lower

def remove_unauthorized_users():
    current_users = user_audit()
    allowed_users = check_users()
    if current_users == allowed_users:
        print("\nUsers are good! (Surprisingly :D)\n")
    elif current_users != allowed_users:
        for user in current_users:
            if user.lower() not in allowed_users:
                print("Deleting unauthorized user '" + user + "'!\n")
                run("deluser " + user)
        for user in allowed_users:
            run("useradd " + user)

    admins = input("Please enter a comma seperated list of administrators: \n").split(", ")
    
    current_users = user_audit()

    for user in current_users:
        if user not in admins:
            print("Removing " + user + " from sudo\n")
            run("deluser " + user + " sudo")
    
def change_passwords(password):
    users = user_audit()
    for user in users:
        print("Changing password for '" + user + "'!\n")
        run("usermod -p " + password + " " + user)

def activate_firewall():
    install_packages("ufw\n")
    run("ufw enable\n")
    run("ufw logging on\n")
    
def install_antivirus():
    run("apt install clamav -y\n")
    run("clamscan -y\n")
    
def remove_pup():
    dictionary = open("./hacking_tools.txt", "r").readlines()
    for tool_name in dictionary:
        print("Deleting any trace of " + tool_name)
        run("apt purge -y" + tool_name)
    print("Removing leftovers :D")
    run("apt autoremove -y")

def new_password():
    print("Please input a secure password containing:\n"
          "2 Special Characters\n"
          "2 Capital Letters\n"
          "No common dictionary items\n\n")
    your_password = input("Enter your password here: \n")

    run("echo " + your_password + " > your_password.txt")

    print("Refer to your_password.txt for your password")

    return your_password  
### END OF FUNCTION DEFINITIONS ###


### START OF SCRIPT ###

def main():
    check_sudo()
    try:
        create_files()
    except:
        print("Cannot Create User File.")
    
    cleanup_system():
    
    remove_unauthorized_users()

    remove_pup()
    
    activate_firewall()
    
    install_antivirus()

    update_policies()

    change_passwords(new_password())

    
    
main()
    
