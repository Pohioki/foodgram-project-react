from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorPermission(BasePermission):
    """
       Permission class that allows access only to the author of an object.

       Methods:
           has_object_permission(request, view, obj): Determines
           if the request has permission to access the object.

       """

    def has_object_permission(self, request, view, obj):
        """
                Check if the request has permission to access the object.

                Args:
                    request: The request being made.
                    view: The view that handles the request.
                    obj: The object being accessed.

                Returns:
                    bool: True if the request has permission, False otherwise.

                """
        return (request.method in SAFE_METHODS
                or obj.author == request.user)
