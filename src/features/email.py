from flask import current_app as app

from requests import post

class EmailSender:
    def __init__(self):
        self.api_base_url = "https://api.eu.mailgun.net/v2/%s/messages" % app.config['MAILGUN_DOMAIN']
        self.api_key = app.config['MAILGUN_KEY']
        self.ic_courses_team = "IC Courses Team <no-reply@iccourses.cs.muzoo.io>"

    def send_message(self, email, subject, html_message):
        return post(
            self.api_base_url,
            auth=("api", self.api_key),
            data={"from": self.ic_courses_team,
                "to": [email],
                "subject": subject,
                "html" : html_message}
        )
    
    def registration_success_email(self, email, username, display_name):
        html_message = "Dear " + username + ", <br /><br />" + \
                "Your account has been successfully created! <br />" + \
                "<h4>Account Information</h4>" + \
                "<b>SKY Username:</b> " + username + "<br />" + \
                "<b>Display Name:</b>  " + display_name + "<br /><br />" + \
                "You can now log in with your SKY username and password you provided. <br />" + \
                "Other users will see your posts under your display name. <br /><br />" + \
                "You may change your display name and password any time at the <a href='http://iccourses.cs.muzoo.io/changeinfo'>Change Information</a> page. " + \
                "If you forget your password, you can click on Forgot Password on the <a href='http://iccourses.cs.muzoo.io/login'>Log In</a> page and the new temporary password will be sent to you via email. <br /><br />" + \
                "Sincerely, <br />" + \
                "IC Courses Team"
        
        return self.send_message(email, "IC Courses Registration Success!", html_message)
    
    def user_changed_password(self, email, username):
        html_message = "Dear " + username + ", <br /><br />" + \
                "Your password has been changed. <br /><br / >" + \
                "If this wasn't you, please click on Forgot Password on the <a href='http://iccourses.cs.muzoo.io/login'>Log In</a> page. <br />" + \
                "We will reset the password for you. <br /><br />" + \
                "Sincerely, <br />" + \
                "IC Courses Team"
        
        return self.send_message(email, "IC Courses Password Reset", html_message)

    def we_changed_users_password(self, email, username, password):
        html_message = "Dear " + username + ", <br /><br />" + \
                "Your password has been changed to " + password + ".<br /><br / >" + \
                "For security reasons, please change your password to something else at the <a href='http://iccourses.cs.muzoo.io/changeinfo'>Change Information</a> page as soon as you log in! <br /><br />" + \
                "Sincerely, <br />" + \
                "IC Courses Team"
        
        return self.send_message(email, "IC Courses Temporary Password", html_message)

    def notify_new_moderators(self, email, username):
        html_message = "Dear " + username + ", <br /><br />" + \
                "You now have moderator privileges for IC Courses web app.<br /><br / >" + \
                "We are looking forward for your contribution to our community. :) <br /><br />" + \
                "Sincerely, <br />" + \
                "IC Courses Team"
        
        return self.send_message(email, "Welcome, New Moderator", html_message)


emailer = EmailSender()