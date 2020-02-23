# -*- coding:utf-8 -*- 
# __author__ = 'zhaozhiyuan'
# import pandas as pd
import smtplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import traceback


def convert_html(title,image=0,content=None,index=False):

    text = ""
    if image:
        for t,i in zip(title,range(image)):
            text += '<p><strong>%s<strong><br /><img src="cid:image%s" /></p>'%(t,i)          
    else:
        for t,c in zip(title,content):       
            text += "<p><strong>%s</strong><br /></p>%s"%(t,c.to_html(index=index))            
    return text


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(),addr))



def send_mail(html,att_file=None,has_att=False,timestamp=None,receiver = ['kindle_forme@126.com']):
    style = '''<html>
             <style type="text/css">
                h2 {color: blue}
                h3 {color: blue}
                
                img {float:left; widht:350; height:300}
                .dataframe{ border-collapse:collapse; text-align: center;font-family:Microsoft YaHei}
                .dataframe th{ border:solid 1px #607B8B;text-align: center;background-color:#5CACEE}
                .dataframe td{ border:solid 1px #607B8B;text-align: center}
             </style>
             <body>
             <dir>
            '''
    html = style + html + "</dir></body></html>"
    sender = 'kindle_forme@126.com'
    
    # subject = 'python email test'
    smtpserver = 'smtp.126.com'
    # 设置邮箱及密码
    username = 'kindle_forme@126.com'
    password = 'qazwsx123'

    i = 0
    if has_att:
        msgRoot = MIMEMultipart()  
        msgText = MIMEText(html,'html','utf-8')
        msgRoot.attach(msgText)
        for file in att_file:

            fp = open('./books/'+file, 'rb')
            # msgImage = MIMEImage(fp.read())
            msgFile = MIMEText(fp.read(),'base64', 'utf-8')
            # msgFile = MIMEApplication(fp.read())
            
            fp.close()
            # msgFile["Content-Type"] = 'application/octet-stream'
            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            print(f'attachment; filename="{file}"')
            # msgFile["Content-Disposition"] = f'attachment;filename="{file}"'
            msgFile.add_header('Content-Disposition', 'attachment', filename=f"{file}")
            # msgFile.add_header('Content-ID', '<image%s>'%i)
            msgRoot.attach(msgFile)
            i += 1
    else:
        msgRoot = MIMEText(html,'html','utf8')

    msgRoot['From'] = _format_addr(u'kindle <%s>' % sender)
    msgRoot['To'] = _format_addr(u'kindle <%s>' % receiver)
    msgRoot['Subject'] = Header(u'kindle <%s>' % timestamp, 'utf-8').encode()

    try:
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver,25)
        
        # smtp.ehlo()
        # smtp.starttls()
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msgRoot.as_string())
        smtp.quit()
        return 'sending success'
    except Exception as e:
        traceback.print_exc()
        return e
    

if __name__=='__main__':

    ok = send_mail('test',att_file=['《一个人的朝圣》.mobi'],has_att=1,receiver='ivy_wangchen_5TJk0m@kindle.com')
    print(ok)