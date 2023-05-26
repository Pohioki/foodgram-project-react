from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
        Custom pagination class for controlling the page size.

        Attributes:
            page_size (int): The default number of items
            to be included in a page.

            page_size_query_param (str): The query parameter name
            for specifying the page size.
        """
    page_size = 6
    page_size_query_param = 'limit'
