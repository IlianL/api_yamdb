from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """Проверка: является ли пользователь администратором."""
    message = 'Данное действие доступно только администратору.'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.method in permissions.SAFE_METHODS
                or (request.user.role == 'admin' or request.user.is_superuser))
        return request.method in permissions.SAFE_METHODS


class IsAuthorIsAdminIsModeratorOrReadOnly(permissions.BasePermission):
    """
    Проверяем является ли пользователь автором,
    модератором или администратором. Для отзывов, комментариев.
    """

    message = 'У вас недостаточно прав для выполнения данного действия.'

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated)
    
    def has_obj_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (request.method in permissions.SAFE_METHODS
                    or request.user.is_superuser
                    or request.user.role == 'admin'
                    or request.user.role == 'moderator'
                    or obj.author == request.user)
        return request.method in permissions.SAFE_METHODS


class IsAdmin(permissions.BasePermission):

    message = 'Доступно только администратору.'

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.role == 'admin' or request.user.is_superuser)
                )
