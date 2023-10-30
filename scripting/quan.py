import subprocess
#shell execution and dependency checking
#shell execute should work on linux
def shellExecute(command):
    return bytes.decode(subprocess.check_output(command.split(),shell=True))


#powershell only work on window
def powershellExecute(command):
    return shellExecute("powershell.exe "+command)




depNotFound = False
def checkDependencies(defList):
    global depNotFound
    #Getting the list of installed packages
    InstalledOutput = shellExecute("pip list")
    for i in defList:
        #check to see if the package is installed or not
        if not (i in str(InstalledOutput)):
            #installing the missing package
            depNotFound=True
            print("Installing "+i)
            InstallOut = shellExecute("pip install "+i)
            print((InstallOut))

dependencies = ["pywin32","pyuac"]
checkDependencies(dependencies)
#this template is meant for window
#modification are needed for use with linux

def main():
    print("All dependencies installed")
    import pyuac
    if (pyuac.isUserAdmin()):
        #stopping services example
        print("Stopping Print Spooler")
        powershellExecute("Stop-Service -Name \"Spooler\"")
        powershellExecute("Set-Service -StartupType Disable \"Spooler\"")


        input("Press Enter to exit")
    else:
        pyuac.runAsAdmin()


if __name__ == "__main__" and not depNotFound:
    main()
elif depNotFound:
    print("Installed all missing dependencies, restart the script to continue")
input("Press Enter to exit")