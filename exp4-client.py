'''
@Aurhor: Sublime. a.k.a. Xiao Yinrui
@Update: 2020.6.23
@E-mail: 466491019@qq.com

目前，仍有bug部分：
1.客户端和服务器端不能自动退出，会卡死
'''

from socket import *
from threading import Thread
import wx
import time, os, sys
import struct

APP_TITLE = u'实验4-Socket-客户端'
BUFSIZE = 1024


class Client(wx.Frame):
    def __init__(self, superior):
        wx.Frame.__init__(self, parent = superior, title = APP_TITLE)

        self.Bind(wx.EVT_CLOSE, self.OnClose)             #主窗口绑定自身的关闭事件

        panel = wx.Panel(self, -1)
        self.statusBar = self.CreateStatusBar() #创建状态栏
        self.statusBar.SetStatusText('就绪')

        self.checkBoxChat = wx.CheckBox(panel, -1, '聊天')
        self.checkBoxFile = wx.CheckBox(panel, -1, '文件传输')

        sizer1 = wx.FlexGridSizer(1, 2, 5, 5)
        sizer1.AddMany(
            [(self.checkBoxChat, 0, wx.SHAPED|wx.EXPAND),
             (self.checkBoxFile, 0, wx.SHAPED|wx.EXPAND)]
            )

        label1 = wx.StaticText(panel, -1, "字符串发送区:", style=wx.ALIGN_RIGHT|wx.ALL)
        self.sendBufferText = wx.TextCtrl(panel, -1, "",style=wx.ALIGN_LEFT)
        self.sendBufferBtn = wx.Button(panel, -1, "发送")

        self.Bind(wx.EVT_BUTTON, self.OnSendBufferBtn, self.sendBufferBtn)

        sizer2 = wx.FlexGridSizer(1, 3, 5, 5)
        sizer2.AddMany(
            [(label1, 0, wx.SHAPED|wx.EXPAND),
             (self.sendBufferText, 0, wx.SHAPED|wx.EXPAND),
             (self.sendBufferBtn, 0, wx.SHAPED|wx.EXPAND)]
            )

        label2 = wx.StaticText(panel, -1, "字符串接收区:", style=wx.ALIGN_RIGHT|wx.ALL)
        self.recvBuffer = wx.TextCtrl(panel, -1, "", style=wx.TE_READONLY | wx.ALIGN_LEFT)
        #label3 = wx.StaticText(parent=panel,label="MousePos:")
        #self.posMouse = wx.TextCtrl(panel, -1, "", style=wx.TE_READONLY)

        sizer3 = wx.FlexGridSizer(1, 2, 5, 5)
        sizer3.AddMany(
            [(label2, 0, wx.ALIGN_RIGHT),
             (self.recvBuffer, 0, wx.ALIGN_RIGHT)]
            )

        label3 = wx.StaticText(panel, -1, "需发送文件名：", style=wx.ALIGN_RIGHT|wx.ALL)
        self.sendFileName = wx.TextCtrl(panel, -1, "", style=wx.ALIGN_LEFT)
        self.sendFileBtn = wx.Button(panel, -1, "发送")

        self.Bind(wx.EVT_BUTTON, self.OnSendFileBtn, self.sendFileBtn)

        sizer4 = wx.FlexGridSizer(1, 3, 5, 5)
        sizer4.AddMany(
            [(label3, 0, wx.ALIGN_RIGHT),
             (self.sendFileName, 0, wx.ALIGN_RIGHT),
             (self.sendFileBtn, 0, wx.SHAPED|wx.EXPAND)]
            )        

        self.border = wx.BoxSizer(wx.VERTICAL)
        self.border.Add(sizer1, 0, wx.ALL, 15)
        self.border.Add(sizer2, 0, wx.ALL, 15)
        self.border.Add(sizer3, 0, wx.ALL, 15)
        self.border.Add(sizer4, 0, wx.ALL, 15)
        panel.SetSizerAndFit(self.border)
        self.Fit()    # 窗体大小自适应

        self.closeFlag = False
        self.fileFlag = False
        self.flag = False
        self.buffBtnClicked = False
        self.fileBtnClicked = False
        self.initSocket()

    def initSocket(self):
        '''客户端Socket初始化'''
        # 创建套接字
        self.tcp_socket_client = socket(AF_INET,SOCK_STREAM)
        # 创建链接
        dest_ip = '127.0.0.1'
        dest_port = 7788
        self.tcp_socket_client.connect((dest_ip,dest_port))

        # 启动收发线程
        self.thread_rece = Thread(target=self.recv)
        self.thread_send = Thread(target=self.send_msg)    

        self.thread_rece.start()
        self.thread_send.start()    
    
    '''OnClose退出重写'''
    def OnClose(self, event):
        global client
        r = wx.MessageBox("是否真的要关闭窗口？", "请确认", wx.CANCEL|wx.OK|wx.ICON_QUESTION)
        if r == wx.OK:        #注意wx.OK跟wx.MessageDialog返回值wx.ID_OK不一样
            self.closeFlag = True
            self.tcp_socket_client.send('xx'.encode())  #喜爱难过向服务器端发送关闭指令
            #sys.exit(0)

            self.tcp_socket_client.close()
            self.thread_rece.join()
            self.thread_send.join()
            # 关闭
            #self.tcp_socket_client.close()
            client.Destroy()


    def OnSendBufferBtn(self, event):
        buff = self.sendBufferText.GetValue()
        self.msg = buff
        self.buffBtnClicked = True

    def OnSendFileBtn(self, event):
        #self.tcp_socket_client.send('file'.encode())

        self.filename = self.sendFileName.GetValue()
        self.fileBtnClicked = True


    def recv(self):
        while True:
            print(self.closeFlag)
            if self.closeFlag == True:
                break
            data_recv = self.tcp_socket_client.recv(1024)
            data=data_recv.decode()
            self.recvBuffer.SetValue(data)
            #print('>服务端：', data)
                

    def send_msg(self):
        self.msg = ''
        self.filename = ''
        self.modeChat = 0
        self.modeFile = 0
        while True:
            isChat = self.checkBoxChat.GetValue()
            isFile = self.checkBoxFile.GetValue()
            if isChat == False and isFile == False:
                if self.closeFlag == True:
                        break
                continue

            if isChat and not isFile:     #聊天模式        
                self.modeChat = 1
                self.modeFile = 0
                self.sendCurrentMode(self.modeChat, self.modeFile)
                while not self.buffBtnClicked:
                    self.statusBar.SetStatusText('正在等待发送')
                    if self.closeFlag == True:
                        self.flag = True
                        break
                    continue

                if self.flag:
                    break
                self.buffBtnClicked = False
                #print(self.closeFlag)

                if self.msg != '':    
                    self.tcp_socket_client.send(self.msg.encode())
                    self.msg = ''
                    self.statusBar.SetStatusText('消息发送成功')
                    time.sleep(2)
                    self.statusBar.SetStatusText('就绪')
                self.exit_and_set_default()

            elif not isChat and isFile:      #文件发送模式        
                self.modeChat = 0
                self.modeFile = 1
                self.sendCurrentMode(self.modeChat, self.modeFile)
                while not self.fileBtnClicked:
                    self.statusBar.SetStatusText('正在等待发送')
                    if self.closeFlag == True:
                        self.flag = True
                        break
                    continue

                if self.flag:
                    break
                self.fileBtnClicked = False
                if self.filename != '':
                    file_size=os.path.getsize(self.filename)
                    fhead = struct.pack('l',file_size)
                    print(fhead)      #打印出发送的原始对象信息
                    self.tcp_socket_client.sendall(fhead)
                    fp=open(self.filename,'rb')
                    while True:      
                        data=fp.read(BUFSIZE)
                        if not data:
                            break
                        self.tcp_socket_client.sendall(data)
                    fp.close()

                    self.filename = ''
                    self.statusBar.SetStatusText('文件发送成功')
                    time.sleep(2)
                    self.statusBar.SetStatusText('就绪')
                    self.exit_and_set_default()

            #else:
                #self.exit_and_set_default()
                #self.sendCurrentMode(self.modeChat, self.modeFile)
                #self.statusBar.SetStatusText('请重新选择模式')
                #time.sleep(2)
                #self.statusBar.SetStatusText('就绪')
                #time.sleep(2)

    def sendCurrentMode(self, mChat, mFile):
        mode = "%d%d"%(mChat, mFile)
        self.tcp_socket_client.send(mode.encode())

    def exit_and_set_default(self):
        self.checkBoxChat.SetValue(False)
        self.checkBoxFile.SetValue(False)
        self.modeChat = 0
        self.modeFile = 0


if __name__ == '__main__':
    app = wx.App()
    client = Client(None)
    client.Show(True)
    app.MainLoop()
