#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# __author__ = "shark"
# Date: 2018/10/9
import traceback

from plumbum import cli
from plumbum import colors
from plumbum import local
import yagmail

class SendMail(cli.Application):
    VERSION = colors.red | "1.0"
    to_email = []
    user, password, host, port = '','','',''
    to_emails = []
    @cli.switch(['-f', '--file'], str,
                help="""指定配置文件 INI 风格;
                如： -f  /path/conf.ini
                    --file=/path/conf.ini
                所以当键值对，必须在[DEFAULT]内配置
                """)
    def conf_file(self, filename):
        p = local.path(filename)
        if p.isfile():
            with cli.ConfigINI(p) as conf:
                SendMail.user, SendMail.password = conf.get('user'), conf.get('password')
                SendMail.host, SendMail.port = conf.get('smtp_server'), conf.get('smtp_port')
                SendMail.to_emails = conf.get('to_emails').split(',')


@SendMail.subcommand("register")
class Register(cli.Application):
    """
    向系统的密钥环中注册邮箱账号和密码,
    子命令中参数的值会覆盖 -f 指定文件中的值
    """

    _user = cli.SwitchAttr(['-u', '--user'], str, help="发件箱的账户")
    _password = cli.SwitchAttr(['-p', '--password'], str, help="发件箱的授权密码，非登录密码")

    def main(self, *args):
        self.user = self._user if self._user else SendMail.user
        self.password = self._password if self._password else SendMail.password
        if all([self.user, self.password]):
            yagmail.register(self.user, self.password)
        else:
            self.user = self.user if self.user else '未获取到'
            self.password = '已提供' if self.password else '未获取到'
            error_msg = '''必须指定账号和密码:
                            user: {}
                            password: {}'''.format(self.user, self.password)

            raise ValueError(error_msg)

@SendMail.subcommand("send")
class Send(cli.Application):
    """发送邮件"""

    __user = cli.SwitchAttr(['-u', '--user'], str, help="发送邮箱的账号")
    __host = cli.SwitchAttr(['-h', '--host'], str, help="发送邮件的 SMTP 地址")
    __port = cli.SwitchAttr(['-P', '--post'], int, help="发送邮件的 SMTP 端口，注意加密和不加密端口不同")

    __enable_ssl = cli.Flag('--ssl', default=False, help="假如给定此参数，使用加密传输，默认不使用")

    __title = cli.SwitchAttr(['-j', '--subject'], str, mandatory=True, help='发送邮件的标题')
    __contents = cli.SwitchAttr(['-m', '--html', '--contents'], str, list=True,
                   help="发送邮件的正文")
    __subs = cli.SwitchAttr(['-s', '--sub'], str, list=True,
                help='发送的附近，支持多个，示例： -s 1.jpg -s 2.jpg')

    __to_emails = []

    @cli.switch(['-t', '--to'], str, list=True,
                  help="收件人邮箱，支持多个")
    def get_emails(self, email_user):
        self.__to_emails = tuple(set(email_user))

    def main(self, *args):
        self.user = self.__user if self.__user else SendMail.user
        self.host = self.__host if self.__host else SendMail.host
        self.port = self.__port if self.__port else SendMail.port

        self.to_emails = self.__to_emails if self.__to_emails else SendMail.to_emails

        if not self.__enable_ssl:
            if self.port != 25:
                raise ValueError("SMTP 非加密端口是 25")

        if not all((self.user, self.host, self.port)):
            error_msg = """参数不完整: 
                        user: {}
                        host: {}
                        port: {}""".format(self.user,self.host,self.port)
            raise ValueError(error_msg)
        try:
            __yag = yagmail.SMTP(user=self.user,
                                host=self.host,
                                port=self.port,
                               smtp_ssl=self.__enable_ssl)

            __yag.send(to=self.to_emails,
                       subject=self.__title,
                       contents=self.__contents,
                       attachments=self.__subs)
        except Exception:
            print(traceback.format_exc())

if __name__ == '__main__':
    SendMail()
