import subprocess

def send_email_via_mail_command(subject, body, to_email, attachment=None):
    # 构造 mail 命令
    mail_command = ["mail", "-s", subject, to_email]
    
    if attachment:
        mail_command += ["-A", attachment]
    
    # 使用 echo 传递邮件正文
    subprocess.run(f"echo '{body}' | {' '.join(mail_command)}", shell=True)

# 调用函数发送邮件
send_email_via_mail_command(
    subject="Test Email with Attachment",
    body="Please find the attached file.",
    to_email="destination@mail.com",
    attachment="./dailyRepo_2025-02-23.md"
)
