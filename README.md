# 프로젝트 소개

* 프로젝트명: Fresh us
* 개발기간: 2022.08.01-2022.08.11
* 개발인원: Frontend 4, Backend 2 (Backend 담당)
* 기술스택: Python, Django, MySQL, Miniconda

친환경을 주제로한 여행지 커뮤니티 사이트를 구현해보았습니다. 짧게 정해진 프로젝트 기한에 맞추기 위해 기존의 커머스 사이트 싱그러운 집(https://www.shouse.garden/main/main.html)사이트의 기획을 클론하였습니다. 짧은 기간안에 결과물을 만들기 위해 웹 서비스 작성시 대부분의 기반이 이미 만들어져있는 장고 프레임워크를 사용하였습니다. 

## 구현

* 소셜 API를 이용한 회원가입 및 로그인
* 게시물 목록 조회, 검색 및 페이지네이션 구현
* 게시물 CRUD 구현
* 댓글 CRUD 구현
 
### 데이터베이스 다이어그램

![diagram](./schema.png)

### 담당 구현 사항

* 카카오 소셜 API를 이용하여 회원가입 및 로그임 구현

```python
from core.utils.kakao_api import KakaoAPI

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
```

카카오 API를 이용하는 모듈을 별도로 구별하여 코드를 작성하였습니다. 최초로 로그인을 하게되면 카카오 정보를 바탕으로 사이트에 회원가입 되도록 하였습니다. 로그인 후에는 카카오 정보를 가져오기 위한 토큰을 만료시키고, 가입된 정보를 포함한 JWT를 클라이언트에 전달하여 로그인 상태를 유지할 수 있도록 구현하였습니다.

* 댓글 CRUD 구현

```python
# ./core/login_decorator.py
access_token = request.headers.get('AUTHORIZATION')

if access_token == '':
    request.user = None
    return func(self, request, *args, **kwargs)

payload      = jwt.decode(access_token, settings.SECRET_KEY, settings.ALGORITHM)
request.user = User.objects.get(id=payload['id'])

return func(self, request, *args, **kwargs)

# ./comments/view.py
@login_decorator
def get(self, request, post_id):
    user   = request.user

    user_id = None
    if not user == None:    
        user_id = user.id
```

게시글 상세 페이지에서 댓글 조회를 구현하는데 문제가 있었습니다. 댓글 조회의 경우 회원과 비회원이 모두 가능해야하는데 JWT를 통해 회원임을 검증하는 데코레이터에 의해 비회원이 댓글을 조회할 수 없게된 것입니다. 그래서 비회원이 페이지를 요청할 경우 헤더의 AUTHORIZATION에 공백을 전달하여 이를 구분하여 비회원이 댓글을 조회할 수 있도록 구현하였습니다.

```python
for comment in comments:
    result.append({
        'id'               : comment.id,
        'user_id'          : comment.user_id,
        'parent_comment_id': comment.parent_comment_id,
        'profile_image_url': comment.user.profile_image_url,
        'nickname'         : comment.user.nickname,
        'comment'          : comment.comment,
        'created_at'       : comment.created_at,
        'depth'            : 0
    })
    for review in Comment.objects.filter(parent_comment_id=comment.id).order_by('-created_at'):
        result.append({
            'id'               : review.id,
            'user_id'          : review.user_id,
            'parent_comment_id': review.parent_comment_id,
            'profile_image_url': review.user.profile_image_url,
            'nickname'         : review.user.nickname,
            'comment'          : review.comment,
            'created_at'       : review.created_at,
            'depth'            : 1
        })

result_res = {'comment' : result[offset : offset + limit]}
```

대댓글을 구현하기 위한 코드입니다. 댓글과 대댓글의 개수를 합쳐 적용되는 페이지네이션을 구현하기 위해 상단과 같이 코드를 작성하였습니다.

## API 명세서
<img width="789" alt="스크린샷 2022-07-30 오후 3 33 59" src="https://user-images.githubusercontent.com/91110192/184284788-c9657496-28e3-4027-bccf-9ebd0ef858ed.png">
<img width="789" alt="스크린샷 2022-07-30 오후 3 33 51" src="https://user-images.githubusercontent.com/91110192/184284793-e3f193f4-8718-47ac-9a0f-00da5e949f10.png">

* [싱그러운 우리 API](https://pastoral-slice-3c4.notion.site/API-553343a65d5c49c1bdf2024745ce39c9)를 보시면, 자세한 API를 확인 가능합니다.

## 참고
- 이 프로젝트는 [싱그러운 집](https://www.shouse.garden/main/main.html) 사이트를 참조하여 학습 목적으로 만들었습니다.
- 실무수준의 프로젝트이지만 학습용으로 만들었기 때문에 이 코드를 활용하여 이득을 취하거나 무단 배포할 경우 법적으로 문제될 수 있습니다.
