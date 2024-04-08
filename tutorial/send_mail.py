import pandas as pd

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_mail_addresses(fname):
    students = pd.read_csv(fname, sep=",")
    students.rename(columns={'Last Name': 'lastname'}, inplace=True)
    students.rename(columns={'First Name': 'firstname'}, inplace=True)
    students.rename(columns={'Email': 'email'}, inplace=True)
    if 'End-of-Line Indicator' in students.columns:
        del students["End-of-Line Indicator"]
    students['Username'] = students['Username'].str.replace(
        '^#', '', regex=True
    )
    students.set_index('Username', inplace=True)
    return students


def send_tutorial_mails(
    tutorial,
    file_with_emails,
    test_student,
    mail_account,
    mail_passwd,
    send_mail=False,
    test=True,
):
    students = get_mail_addresses(file_with_emails)

    def convert(a):
        if a == "-":
            return "-"
        elif a == 1:
            return "A"
        elif a == 2:
            return "B"
        else:
            return "C"

    # HOW TO SEND MAILS
    # see here for an explanation:
    # https://support.google.com/mail/answer/185833?hl=en
    # https://mailtrap.io/blog/python-send-email-gmail/
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(mail_account, mail_passwd)

    for _, result in tutorial.df.iterrows():
        username = result["Username"]
        if test and username != test_student:
            continue
        try:
            student = students.loc[username]
            print(username, student["email"])
        except KeyError:
            print(f"Username; {username} unknown.")
            continue
        message = MIMEMultipart()
        message["From"] = mail_account
        message["To"] = student["email"]
        message["Subject"] = f"{tutorial.course}: results for {tutorial.name}"
        text = f"Dear {student['firstname']} {student['lastname']},\n\n"
        text += f"Here are your answers and grade for {tutorial.name} of {tutorial.date} of {tutorial.course}.\n\n"

        real = {i: convert(tutorial.answer_key[i]) for i in range(1, 11)}
        text += f"Real answers: {real}\n"

        answers = {i: convert(a) for i, a in enumerate(result[:10], 1)}
        text += f"Your answers: {answers}\n\n"

        score = result['score']
        num = tutorial.num_valid_questions
        grade = result['grade']
        text += f"Total points you obtained: {score}.\n"
        text += f"Total number of valid questions: {num}.\n"
        text += f"Your grade: 10 * {score} / {num} = {grade}.\n\n"

        text += "In case something is not correct, we can discuss this during the second hour of the tutorial.\n\n"
        text += "Yours,\n\n"
        text += "Nicky van Foreest"
        if test:
            print(text)

        message.attach(MIMEText(text, "plain"))

        if send_mail:
            receiver_email = student["email"]
            if test:
                receiver_email = mail_account
            session.sendmail(mail_account, receiver_email, message.as_string())

    print('Sent')
    session.quit()
