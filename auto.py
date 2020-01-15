import sys
import traceback
import time
import random
import logging
import os
import pyautogui

from config import NOTE
import sqlite3



class ElementNotFound(Exception):

    def __init__(self, *args, **kwargs):  # real signature unknown
        super().__init__(args, kwargs)


class UserNotFound(Exception):

    def __init__(self, *args, **kwargs):  # real signature unknown
        super().__init__(args, kwargs)


class HasExists(Exception):

    def __init__(self, *args, **kwargs):  # real signature unknown
        super().__init__(args, kwargs)


class AutoGui(object):

    def __init__(self, account=''):
        self.account = account
        self.conn = None
        self.c = None

    def create_table(self):
        self.conn = sqlite3.connect('wexin.db')
        self.c = self.conn.cursor()
        self.c.execute(
            '''
            create table enterprise_wechat
            (id INT AUTO_INCREMENT PRIMARY KEY ,
             telephone VARCHAR (15) NOT NULL DEFAULT '',
             account VARCHAR (15) NOT NULL DEFAULT '',
             num INT NOT NULL DEFAULT 0,
             user_tag VARCHAR (256) NOT NULL DEFAULT '',
             status INT NOT NULL DEFAULT 0,
             created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
             modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            ''')
        self.conn.commit()
        self.conn.close()

    def got_to_new_customer_page(self):
        # 判断企业微信是否在桌面最上层
        select_location = pyautogui.locateCenterOnScreen('./img/select.png', confidence=0.9)
        if not select_location:
            un_select_location = pyautogui.locateCenterOnScreen('./img/un_select.png', confidence=0.9)
            if not un_select_location:
                print('未找到通讯窗口，检查企业微信是否在最上层')
                raise ElementNotFound()
            # 进入通讯窗口
            pyautogui.click(un_select_location)
            print('进入通讯窗口')
        # 查找 新的客户 tab 并进入
        new_customer_selected = pyautogui.locateCenterOnScreen('./img/new_customer_selected.png', confidence=0.9)
        if not new_customer_selected:
            print('未选中 新的客户')
            new_customer_un_select = pyautogui.locateCenterOnScreen('./img/new_customer_un_select.png', confidence=0.9)
            if not new_customer_un_select:
                print('未找到 新的客户 选项')
                raise ElementNotFound()
            pyautogui.click(new_customer_un_select)
        print('进入 新的客户')

    def execute(self, telephone, conn, c):
        try:
            self.got_to_new_customer_page()
            add_icon = pyautogui.locateCenterOnScreen('./img/add_icon.png', confidence=0.9)
            if not add_icon:
                print('未找到 add_icon')
                raise ElementNotFound()
            pyautogui.click(add_icon)
            input_tel_icon = pyautogui.locateCenterOnScreen('./img/input_tel_icon.png', confidence=0.9)
            if not input_tel_icon:
                print('未找到 input tel icon')
                raise ElementNotFound()
            pyautogui.click(input_tel_icon)
            pyautogui.typewrite(telephone, interval=0.25)
            time.sleep(1)
            go_to_add = pyautogui.locateCenterOnScreen('./img/go_to_add.png', confidence=0.9)
            if not go_to_add:
                print('未找到 go to add icon')
                raise ElementNotFound()
            pyautogui.click(go_to_add)
            time.sleep(2)
            search_result = pyautogui.locateCenterOnScreen('./img/search_result.png', confidence=0.9)
            if not search_result:
                not_found_user = pyautogui.locateCenterOnScreen('./img/not_found_user.png', confidence=0.9)
                if not_found_user:
                    print('用户不存在')
                    confirm_not_found_user = pyautogui.locateCenterOnScreen('./img/confirm_not_user.png', confidence=0.9)
                    pyautogui.click(confirm_not_found_user)
                    raise UserNotFound()
            # 处理已添加 和 未添加
            add = pyautogui.locateCenterOnScreen('./img/add.png')
            if not add:
                has_added = pyautogui.locateCenterOnScreen('./img/has_added.png')
                if has_added:
                    print('已添加')
                    raise HasExists()
                else:
                    print('未知错误')
                    raise ElementNotFound()
            pyautogui.click(add)
            time.sleep(2)
            send = pyautogui.locateCenterOnScreen('./img/send.png', confidence=0.9)
            if not send:
                print('未找到 send icon')
                raise ElementNotFound()
            pyautogui.click(send)
            print('send and sleep 2 seconds .....')
            time.sleep(2)
            status = 1
        except HasExists as e:
            print(e)
            status = 2
        except ElementNotFound as e:
            print(e)
            status = -1
        except UserNotFound:
            status = -2
        except Exception as e:
            print(e)
            status = -1
        finally:
            # 回到 新的客服页面
            pyautogui.press('esc')
        attempt = 3
        while attempt > 0:
            attempt -= 1
            try:
                sql = "UPDATE enterprise_wechat SET status={}, num=num+1 WHERE account='{}' and telephone='{}';".format(status, self.account, telephone)
                print('update sql:', sql)
                c.execute(sql)
                conn.commit()
                break
            except Exception as e:
                print(e)
                conn.close()
                conn = sqlite3.connect('wexin.db')
                c = conn.cursor()

    def main(self, limit=500, status=[]):
        self.conn = sqlite3.connect('wexin.db')
        self.c = self.conn.cursor()
        sql = "SELECT telephone FROM enterprise_wechat WHERE account='{}' and status in ({}) LIMIT {};".format(self.account, ', '.join([str(i) for i in status]), limit)
        print('sql:', sql)
        cursor = self.c.execute(sql)
        tel_list = [tel for tel, in cursor]
        for tel in tel_list:
            print('current telephone:', tel)
            self.execute(tel, self.conn, self.c)
            sleep_time = random.randint(30, 50)
            print('sleep {} seconds......'.format(sleep_time))
            time.sleep(sleep_time)

    def insert_to_table(self, tel_file, user_label):
        if not self.conn:
            self.conn = sqlite3.connect('wexin.db')
            self.c = self.conn.cursor()
        with open(tel_file, 'r') as f:
            count = 0
            total = 0
            for tel in f:
                tel = tel.strip()
                cursor = self.c.execute("SELECT telephone FROM enterprise_wechat WHERE account='{}' and telephone='{}';".format(self.account, tel))
                cursor = [i for i in cursor]
                print('cursor:', cursor)
                if not cursor:
                    self.c.execute("INSERT INTO enterprise_wechat (telephone, status, account, user_tag) VALUES ('{}', {}, '{}', '{}');".format(tel, 0, self.account, user_label))
                    count += 1
                    total += 1
                    if count == 500:
                        self.conn.commit()
                        count = 0
                    print(total)
            if count > 0:
                self.conn.commit()
            print(total)


if __name__ == '__main__':
    auto = AutoGui(account='13581410621')
    # auto.create_table()
    auto.main(limit=1, status=[0])
    # auto.insert_to_table(tel_file='./tel.txt', user_label='@精准求职')

