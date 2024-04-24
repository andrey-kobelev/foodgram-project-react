from rest_framework.pagination import PageNumberPagination


class UsersPaginator(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'limit'
    page_query_param = 'page'
