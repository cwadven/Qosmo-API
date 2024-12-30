from member.exceptions import (
    GuestTokenRequiredException,
    LoginRequiredException,
)
from rest_framework.permissions import BasePermission


class IsMemberLogin(BasePermission):

    def has_permission(self, request, view):
        if bool(request.member and request.member.is_authenticated):
            return True
        raise LoginRequiredException()


class IsGuestExists(BasePermission):

    def has_permission(self, request, view):
        if bool(request.guest):
            return True
        raise GuestTokenRequiredException()
