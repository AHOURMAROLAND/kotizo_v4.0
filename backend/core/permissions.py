from rest_framework.permissions import BasePermission

class IsAdminKotizo(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class IsVerified(BasePermission):
    message = "Votre compte doit être vérifié pour effectuer cette action."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.est_verifie)

class HasStaffPermission(BasePermission):
    required_section = None
    required_level = 'read'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if not self.required_section:
            return request.user.is_staff
        return request.user.staff_permissions.filter(
            section=self.required_section,
            actif=True
        ).exists()