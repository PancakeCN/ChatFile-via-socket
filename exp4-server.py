'''
@Aurhor: Sublime. a.k.a. Xiao Yinrui
@Update: 2020.6.23
@E-mail: 466491019@qq.com

目前，仍有bug部分：
1.客户端和服务器端不能自动退出，会卡死
'''

from socket import *
from threading import Thread
from threading import Lock
import time
import struct
import re

BUFSIZE = 1024

words = {'how are you?':'Fine,thank you.', 
         'how old are you?':'21',
         'what is your name?':'Xiao Yinrui',
         'where do you work?':'CUIT', 'bye':'Bye'}
clientNum=-1 #记录客户端连接数目
flag=0       #未启动过线程

def client(clientSocket,Num):
    global clientNum
    mode='00'
    flag2 = False
    while True:
        if flag2 == True:
            clientSocket.sendall('服务器端即将退出...'.encode())
            time.sleep(5)
            print('服务器端已退出。')
            break
        while True:
            mode = clientSocket.recv(BUFSIZE)
            mode = mode.decode()   
            print(mode)
            while not (mode == '10' or mode == '01'):
                pass
            if mode == '10':   #文件接收模式
                data = clientSocket.recv(BUFSIZE)
                data = data.decode() 
                print('received message:{0} from client{1}'.format(data, Num))  
                match = '.*%s.*'%data
                print(match)
                matchKeys = []
                pattern = re.compile(match)
                for key in words.keys():
                    result = pattern.findall(key)
                    print(key)
                    print(result)
                    if result != []:
                        matchKeys.extend(result)
                print(matchKeys)
                if matchKeys == []:
                    matchKeys.extend(['Not Found'])
                for eachkey in matchKeys:
                    print(eachkey)
                    clientSocket.sendall(words.get(eachkey,'Nothing').encode())
                #if data.lower()=='bye':
                #    break
                time.sleep(2)
                break
            elif mode == '01':    #文件接收模式 
                data = clientSocket.recv(BUFSIZE)
                print(data)   #打印出接收的原始对象信息
                f_info=struct.unpack('l',data) 
                file_size=f_info[0]    
                recv_size=0
                while not recv_size==file_size:
                    with open('ClientFile.dat','ab') as fp:  
                        if file_size - recv_size > BUFSIZE:
                            data = clientSocket.recv(BUFSIZE)              
                            recv_size += len(data)
                        else:
                            data= clientSocket.recv(file_size - recv_size) 
                            recv_size = file_size
                        print(data)
                        fp.write(data)
                clientSocket.sendall(words.get(data,'服务器已收到文件。').encode())
                mode = '00'
                break
            else:
                flag2 = True
                break
        
        time.sleep(2)
              
    clientSocket.close()    
    lock.acquire()              
    clientNum-=1
    lock.release() 


if __name__ == '__main__':
    # 创建socket
    tcpSerSocket = socket(AF_INET, SOCK_STREAM)
    # 绑定本地信息
    address = ('', 7788)
    tcpSerSocket.bind(address)
    tcpSerSocket.listen(2)
    listThread=list()

    while True:
        if flag==0:
            print(clientNum)
            clientSocket, clientAddr = tcpSerSocket.accept()
            print('received from PORT {0[1]} on {0[0]}'.format(clientAddr ))

            clientNum+=1
            if clientNum==2 or clientNum == -1: #控制最多连接多少客户
                flag=1
            lock = Lock()     #保护 clientNum的写操作
            listThread.append(Thread(target=client,args = (clientSocket, clientNum)))
            
            listThread[clientNum].start()
            listThread[clientNum].join(2)
            #print(clientNum)
        
        else:               # 客户端全部关闭时，退出服务器
            if clientNum==-1:           
                break 
    tcpSerSocket.close()
    print('closed.')



