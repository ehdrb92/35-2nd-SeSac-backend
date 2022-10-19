import jwt

from django.views import View
from django.http  import JsonResponse
from django.conf  import settings

from core.utils.kakao_api import KakaoAPI
from users.models         import User

class KakaoSocialLoginView(View):
    def get(self, request):
        auth_code   = request.GET.get('code')
        kakao_api   = KakaoAPI(settings.KAKAO_REST_API_KEY, settings.KAKAO_REDIRECT_URI)
        kakao_token = kakao_api.get_kakao_access_token(auth_code)
        kakao_info  = kakao_api.get_user_kakao_information(kakao_token)

        user, created = User.objects.get_or_create(
            kakao_id          = kakao_info['kakao_id'],
            email             = kakao_info['email'],
            nickname          = kakao_info['nickname'],
            profile_image_url = kakao_info['profile_image_url'],
        )

        kakao_api.expire_user_access_token(kakao_token)

        message = "Sign_in"
        if created == True:
            message = "Sign_up"
        
        access_token = jwt.encode({'id' : user.id}, settings.SECRET_KEY, settings.ALGORITHM)

        return JsonResponse({'access_token' : access_token, 'message' : message}, status = 200)
