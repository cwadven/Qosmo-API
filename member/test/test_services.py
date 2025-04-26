from unittest.mock import patch, MagicMock

from common.models import (
    BlackListSection,
    BlackListWord,
)
from django.test import TestCase
from member.models import (
    Member,
    MemberExtraLink,
    MemberInformation,
)
from member.services import (
    check_email_exists,
    check_nickname_exists,
    check_nickname_valid,
    check_only_alphanumeric,
    check_only_korean_english_alphanumeric,
    check_username_exists,
    get_active_member_extra_link_qa,
    get_active_member_information_qs,
    get_member_profile,
)


class MemberCheckMemberInfoTestCase(TestCase):
    def setUp(self):
        pass

    def test_check_username_exists_should_return_true_when_username_exists(self):
        # Given: test 라는 이름을 가진 Member 생성
        Member.objects.create_user(username='test')

        # Expected:
        self.assertEqual(check_username_exists('test'), True)

    def test_check_username_exists_should_return_false_when_username_not_exists(self):
        # Expected:
        self.assertEqual(check_username_exists('test'), False)

    def test_check_nickname_exists_should_return_true_when_username_exists(self):
        # Given: test 라는 nickname 을 가진 Member 생성
        Member.objects.create_user(username='aaaa', nickname='test')

        # Expected:
        self.assertEqual(check_nickname_exists('test'), True)

    def test_check_nickname_exists_should_return_false_when_username_not_exists(self):
        # Expected:
        self.assertEqual(check_nickname_exists('test'), False)

    def test_check_email_exists_should_return_true_when_username_exists(self):
        # Given: test 라는 email 을 가진 Member 생성
        Member.objects.create_user(username='aaaa', email='test@naver.com')

        # Expected:
        self.assertEqual(check_email_exists('test@naver.com'), True)

    def test_check_email_exists_should_return_false_when_username_not_exists(self):
        # Expected:
        self.assertEqual(check_email_exists('test@naver.com'), False)

    def test_check_nickname_valid_when_valid(self):
        # Given: test 라는 nickname 을 가진 Member 생성
        # Expected:
        self.assertEqual(check_nickname_valid('test'), True)

    def test_check_nickname_valid_when_invalid(self):
        # Given: test 라는 nickname 을 가진 Member 생성
        black_list_section, _ = BlackListSection.objects.get_or_create(
            name='닉네임',
            defaults={
                'description': '닉네임 블랙리스트',
            }
        )
        BlackListWord.objects.get_or_create(
            black_list_section=black_list_section,
            wording='test',
        )

        # Expected:
        self.assertEqual(check_nickname_valid('123test'), False)


class CheckRegexTestCase(TestCase):
    def test_check_only_alphanumeric(self):
        self.assertEqual(check_only_alphanumeric("abc123"), True)
        self.assertEqual(check_only_alphanumeric("abc@123"), False)
        self.assertEqual(check_only_alphanumeric("한글123"), False)

    def test_check_only_korean_english_alphanumeric(self):
        self.assertEqual(check_only_korean_english_alphanumeric("안녕abc123"), True)
        self.assertEqual(check_only_korean_english_alphanumeric("안녕abc@123"), False)
        self.assertEqual(check_only_korean_english_alphanumeric("가나다ABC123"), True)


class GetActiveMemberInformationQuerySetTestCase(TestCase):

    def setUp(self):
        self.member1 = Member.objects.create_user(username='test1', nickname='test1')
        self.member_information1 = MemberInformation.objects.create(
            member=self.member1,
            description='test1',
        )
        self.member_information2 = MemberInformation.objects.create(
            member=self.member1,
            description='test2',
        )

    @patch('member.services.MemberInformation.objects.filter')
    def test_get_active_member_information_qs(self,
                                              mock_filter):
        # Given:
        # When:
        get_active_member_information_qs(self.member1.id)

        # Then: Assert that MemberInformation.objects.filter is called with the correct data
        mock_filter.assert_called_once_with(
            member_id=self.member1.id, is_deleted=False
        )


class GetActiveMemberExtraLinkQuerySetTestCase(TestCase):
    def setUp(self):
        self.member1 = Member.objects.create_user(username='test1', nickname='test1')
        self.member_extra_link1 = MemberExtraLink.objects.create(
            member=self.member1,
            description='test1',
        )
        self.member_extra_link2 = MemberExtraLink.objects.create(
            member=self.member1,
            description='test2',
        )

    @patch('member.services.MemberExtraLink.objects.filter')
    def test_get_active_member_extra_link_qa(self,
                                             mock_filter):
        # Given:
        # When:
        get_active_member_extra_link_qa(self.member1.id)

        # Then: Assert that MemberInformation.objects.filter is called with the correct data
        mock_filter.assert_called_once_with(
            member_id=self.member1.id, is_deleted=False
        )


class GetMemberProfileTestCase(TestCase):
    def setUp(self):
        self.member = Member.objects.create_user(
            username='test_user',
            nickname='테스트 유저',
            profile_image_url='test/image.jpg',
            member_status_id=1,
        )

    @patch('member.services.Member.raise_if_inaccessible')
    def test_get_member_profile_should_raise_error_when_invalid_member_status(
            self,
            mock_raise_if_inaccessible,
    ):
        # Given: member_status_id invalid
        self.member.member_status_id = 2
        self.member.save()
        # And:
        mock_raise_if_inaccessible.side_effect = Exception

        # When: 프로필 정보 조회
        with self.assertRaises(Exception):
            get_member_profile(self.member.id)

        # Then: Should raise error
        mock_raise_if_inaccessible.assert_called_once_with()

    @patch('member.services.MapSubscriptionService')
    def test_get_member_profile_should_return_correct_profile_data(self, mock_subscription_service):
        # Given: MapSubscriptionService 모킹 설정
        mock_service_instance = MagicMock()
        mock_service_instance.get_member_subscription_count.return_value = 5
        mock_subscription_service.return_value = mock_service_instance

        # When: 프로필 정보 조회
        profile_data = get_member_profile(self.member.id)

        # Then: MapSubscriptionService가 올바른 인자로 호출되었는지 확인
        mock_subscription_service.assert_called_once_with(member_id=self.member.id)
        mock_service_instance.get_member_subscription_count.assert_called_once_with()

        # Then: 반환된 프로필 데이터가 올바른지 확인
        self.assertEqual(profile_data, {
            'id': self.member.id,
            'nickname': self.member.nickname,
            'profile_image': self.member.profile_image_url,
            'subscribed_map_count': 5
        })

    @patch('member.services.MapSubscriptionService')
    def test_get_member_profile_should_handle_none_profile_image(self, mock_subscription_service):
        # Given: 프로필 이미지가 없는 회원
        member_without_image = Member.objects.create_user(
            username='no_image_user',
            nickname='이미지없는유저',
            profile_image_url=None,
            member_status_id=1,
        )

        # Given: MapSubscriptionService 모킹 설정
        mock_service_instance = MagicMock()
        mock_service_instance.get_member_subscription_count.return_value = 0
        mock_subscription_service.return_value = mock_service_instance

        # When: 프로필 정보 조회
        profile_data = get_member_profile(member_without_image.id)

        # Then: MapSubscriptionService가 올바른 인자로 호출되었는지 확인
        mock_subscription_service.assert_called_once_with(member_id=member_without_image.id)
        mock_service_instance.get_member_subscription_count.assert_called_once_with()

        # Then: 반환된 프로필 데이터가 올바른지 확인
        self.assertEqual(profile_data, {
            'id': member_without_image.id,
            'nickname': member_without_image.nickname,
            'profile_image': None,
            'subscribed_map_count': 0
        })
