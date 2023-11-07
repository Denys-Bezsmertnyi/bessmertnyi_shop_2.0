from django.contrib.auth.mixins import UserPassesTestMixin, AccessMixin


class AdminRequiredMixin(UserPassesTestMixin, AccessMixin):
    login_url = '/login'

    def test_func(self):
        return self.request.user.is_superuser
