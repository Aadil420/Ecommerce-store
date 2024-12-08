# from django.core.mail import EmailMessage
# from rest_framework_simplejwt.tokens import RefreshToken
# # import os

# class Util:
#     @staticmethod
#     def send_email(data):
#         email = EmailMessage(
#             subject=data['subject'],
#             body=data['body'],
#             from_email='aadilchauhanxyz@gmail.com',
#             to=[data['to_email']]
#         )
#         email.send()


from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }