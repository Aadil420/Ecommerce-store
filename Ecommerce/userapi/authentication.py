# from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from custom_admin.models import Admin_Panel_AuthToken

# class CostumTokenAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         token = request.META.get('HTTP_AUTHORIZATION')
#         if not token:
#             raise AuthenticationFailed('Authentication credentials were not provided.')
        
#         try:
#             token = token.split("Token ")[1]
#             auth_token = Admin_Panel_AuthToken.objects.get(token=token)
#         except Admin_Panel_AuthToken.DoesNotExist:
#             raise AuthenticationFailed('Invalid token')
        
#         return (auth_token.user, None)