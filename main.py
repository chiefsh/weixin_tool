import time
import os
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk
from multiprocessing import Process, freeze_support, set_executable
from config import SEND_ROLE
from auto import AutoGui
from threading import Thread


def locate_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width - 100), 50)
    root.geometry(size)


class WeiXin(object):

    def __init__(self):
        self.p = None
        self.GUI = Tk()

    def main(self):
        # 创建主窗口
        self.GUI.title('weixin tool')
        locate_window(self.GUI, 500, 600)
        self.GUI.maxsize(500, 300)
        self.GUI.minsize(500, 300)

        # 执行添加任务窗口
        # 添加一个标签
        self.account_label = Label(self.GUI, text='执行账号：')
        self.account_label.config(font=("Courier", 12))
        self.account_label.place(x=20, y=30, width=100, height=20)
        self.account_entry = Entry(self.GUI, width=15)
        self.account_entry.place(x=125, y=30, width=120, height=20)

        # 创建发送人群label
        self.send_role_label = Label(self.GUI, text='发送人群：', font=("Courier", 12))
        self.send_role_label.place(x=20, y=80, width=100, height=20)
        self.send_combobox = ttk.Combobox(self.GUI)
        self.send_combobox['values'] = ('全部', '未邀请过', '已邀请过')
        self.send_combobox.place(x=125, y=80, width=120, height=20)
        self.send_combobox.current(0)

        # 创建邀请个数label
        self.send_num_label = Label(self.GUI, text='邀请个数：', font=("Courier", 12))
        self.send_num_label.place(x=20, y=130, width=100, height=20)
        v = IntVar(self.GUI, value=300)
        self.send_num_entry = Entry(self.GUI, textvariable=v)
        self.send_num_entry.place(x=125, y=130, width=120, height=20)

        # 导入任务窗口
        # 创建执行操作label
        self.import_account_label = Label(self.GUI, text='导入账号：', font=("Courier", 12))
        self.import_account_label.place(x=255, y=30, width=100, height=20)
        self.import_acount_entry = Entry(self.GUI)
        self.import_acount_entry.place(x=360, y=30, width=120, height=20)

        # 添加一个标签
        self.import_file_label = Label(self.GUI, text='导入文件：')
        self.import_file_label.config(font=("Courier", 12))
        self.import_file_label.place(x=255, y=80, width=100, height=20)

        def get_import_file(event):
            filename = tkinter.filedialog.askopenfilename()
            if not filename:
                filename = ''
            self.import_entry.insert(0, filename)

        self.import_entry = Entry(self.GUI, width=15)
        self.import_entry.bind('<Button-1>', get_import_file)
        self.import_entry.place(x=360, y=80, width=120, height=20)

        # 创建用户标签label
        self.user_label = Label(self.GUI, text='用户标签：', font=("Courier", 12))
        self.user_label.place(x=255, y=130, width=100, height=20)
        self.user_entry = Entry(self.GUI)
        self.user_entry.place(x=360, y=130, width=120, height=20)

        # 创建执行操作label
        self.way_label = Label(self.GUI, text='执行操作：', font=("Courier", 12))
        self.way_label.place(x=20, y=200, width=100, height=20)
        self.execute_combobox = ttk.Combobox(self.GUI)
        self.execute_combobox['values'] = ('添加', '导入')
        self.execute_combobox.place(x=125, y=200, width=120, height=20)
        self.execute_combobox.current(0)

        # 创建启动按钮
        self.start_btn = Button(self.GUI, text='执行', font=("Courier", 12))
        self.start_btn.place(x=275, y=200, width=80, height=20)
        self.start_btn.bind('<Button-1>', self.start)

        # 创建停止按钮
        self.stop_btn = Button(self.GUI, text='停止', font=("Courier", 12))
        self.stop_btn.place(x=385, y=200, width=80, height=20)
        self.stop_btn.bind('<Button-1>', self.stop)
        mainloop()

    def start(self, event):
        # 获取执行操作内容
        if self.p:
            tkinter.messagebox.showwarning('警告', '当前正在执行！')
            return
        exec_way = self.execute_combobox.get()
        if exec_way == '添加':
            account = self.account_entry.get()
            if len(account) != 11:
                tkinter.messagebox.showwarning('警告', '请输入正确的执行账号！')
                return
            send_role = self.send_combobox.get()
            status = SEND_ROLE.get(send_role, [0])
            exec_num = self.send_num_entry.get()
            try:
                num = int(exec_num)
            except:
                tkinter.messagebox.showwarning('警告', '邀请个数请输入数字！')
                return
            self.execute(AutoGui(account).main, (num, status))
            self.start_btn.config(text="执行中")
        elif exec_way == '导入':  # 导入
            import_account = self.import_acount_entry.get()
            if len(import_account) != 11:
                tkinter.messagebox.showwarning('警告', '请输入正确的导入账号！')
                return
            tel_file = self.import_entry.get()
            if '.txt' not in tel_file:
                tkinter.messagebox.showwarning('警告', '请导入正确的txt文件！')
                return
            user_label = self.user_entry.get()
            if not user_label:
                tkinter.messagebox.showwarning('警告', '请输入用户标签！')
                return
            self.execute(AutoGui(import_account).insert_to_table, (tel_file, user_label))
            self.start_btn.config(text="执行中")
            Thread(target=self.listen_progress).start()
        else:
            tkinter.messagebox.showinfo('未知操作')

    def listen_progress(self):
        while 1:
            print('current progress:', self.p.is_alive())
            if not self.p or not self.p.is_alive():
                self.start_btn.config(text='执行')
                self.p = None
                break
            time.sleep(1)

    def stop(self, event):
        print('stop:', event)
        if self.p:
            self.p.terminate()
            self.p = None
            self.start_btn.config(text='执行')

    def execute(self, func, args):
        freeze_support()           # 不打开新窗口，pyinstaller打包
        # set_executable(os.path.join(sys.exec_prefix, 'pythonw.exe')) # 不打开新窗口
        self.p = Process(target=func, args=args)
        print('p:::', self.p)
        self.p.start()


if __name__ == '__main__':
    weixin = WeiXin()
    try:
        weixin.main()
    except Exception as e:
        print(e)
    finally:
        weixin.stop('')
