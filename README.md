# clisendmail
A tool for sending mail based on the command line of the pytho3 implementation

## 使用

### 配置

修改 `mails.ini` 文件
```shell
[DEFAULT]
user = yourusername
password = yourpassword
smtp_server = smtp.126.com
smtp_port = 25
to_emails=1@1.com,2@2.com
```

```python
sendmial.py -f ./mails.ini send -t 1@1.com -j 邮件标题 -m 邮件内容 
```
