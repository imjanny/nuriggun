
# 📖A6조 최종프로젝트 : 누리꾼 (sns형 인터넷 신문사)

## 프로젝트 소개

![Logo](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fbqblle%2Fbtsmj7RPlSn%2FrUaZ0Zz9or7ylezzv8OSrK%2Fimg.png)

우연히 뉴스를 보다가 “누리꾼의 반응이 뜨겁습니다” 같은 기자의 말에서 영감을 받아 누리꾼들의 진짜 반응이 어떤지, 기자들은 어디서 정보를 얻는 지 궁금했습니다.

유저가 기사를 내 다른 사람들의 진짜 반응을 확인 할 수 있고 공유할 수 있는 서비스를 생각하며 “ 유저가 기자가 되어 기사를 쓸 수 있는 sns 형 인터넷 신문사” 라는 주제로 프로젝트를 시작하게 되었습니다.

## 프론트엔드 Repository
https://github.com/imjanny/imjanny.github.io

## 백엔드 Repository
https://github.com/imjanny/nuriggun

## 개발 스택

- 백엔드

    `Python 3.8.10`

    `Django 4.2.2`

    `djangorestframework 3.14.0`

    `openai 0.27.8`

- 프론트엔드

    `HTML 5`

    `CSS`

    `JavaScript`

## 팀원 소개 및 역할

### 임재훈 [깃허브](https://github.com/imjanny)
팀장 / 
소셜로그인, 
카테고리,
서버 배포 및 관리

### 김경진 [깃허브](https://github.com/JINNY-US)
부팀장 /
제보하기,
답장하기,
AI 요약하기,
비동기통신
 
### 배현아 [깃허브](https://github.com/hyun1437)
팀원 /
유저 구독 기능,
게시글 댓글 CRUD,
프로필,
게시글 상세페이지,
js & css & html

### 이정현 [깃허브](https://github.com/Leejunghyun7735)
팀원 /
게시글 CRUD,
좋아요 5종반응
검색,
카테고리,
신고,
js & css & html

### 박영주 [깃허브](https://github.com/Bookwhale00)
팀원 /
유저
회원가입(이메일 인증)
로그인, 회원탈퇴
비밀번호 재설정, 메인페이지, 날씨

## ERD
https://www.erdcloud.com/d/3tcCZcvpMsZR3kF99

![App Screenshot](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbExvU6%2FbtsmyYNoyvg%2FfeBE0D2Vcz8w5NMeMWNMu0%2Fimg.png)

## 아키텍쳐 설계

![App Screenshot](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbBNxGW%2FbtsmwfCbCoa%2FN22SaJUPO9ne8lxtKhMFEK%2Fimg.png)


## 구현 기능
- 회원가입(+개인정보동의)
- 이메일인증
- 로그인
- 소셜로그인
- 로그아웃
- 회원탈퇴
- 비밀번호 찾기
- 비밀번호 변경
- 프로필
- 프로필 수정
- 팔로우 (구독)
- 제보하기 (쪽지)
- 게시글 CRUD
- 스크랩 (북마크)
- 공유하기(프론트)
- 게시글 반응하기 (좋아요, 후속기사 원해요 등등)
- 검색
- 카테고라이징
- 댓글 CRUD
- 댓글 좋아요, 싫어요
- AI를 이용한 기사 3줄 요약 기능
- 사이트 운영자에게 1:1채팅으로 문의하기(tawk.to)
- 구독중인 기자가 새 글을 작성 시 이메일 알림 기능
- 신고기능 (가짜뉴스 OUT)
- 오늘의 날씨
- 피드페이지

## 코드 컨벤션
**💡 백엔드**

**Pascal Case**
RealName, MyVisitorCount - 클래스

**Snake Case**
real_name - 변수, 함수

**Kebab Case**
my-visitor-count - URL

**💡 프론트** 

**Camel Case** realName - 함수

**Kebab Case** my-visitor-count - id, class


