import os

def uploadFile():
    os.system("clear")
    a = input("Upload File")


def downloadFile():
    os.system("clear")
    a = input("Download File")

def menu():
    op = -1
    while(int(op) < 3):
        os.system('clear')    
        print("_____________________________________________________")
        print("|                   W E L C O M E                   |")
        print("|                                                   |")
        print("|                  1: Upload File                   |")
        print("|                  2: Download File                 |")
        print("|___________________________________________________|")
        op = input(" Please, select one option: ")
        os.system('clear')
        if(op == "1"):       
            uploadFile()
        elif(op == "2"):
            downloadFile()
        else:
            print ("Exit!")

menu()