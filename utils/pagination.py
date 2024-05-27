from rest_framework.pagination import PageNumberPagination

# -------------------------------------------------------------
class EventPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

# -------------------------------------------------------------
class ParticipantPagination(PageNumberPagination):
    page_size = 500
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

# -------------------------------------------------------------
class MeetingPagination(PageNumberPagination):
    page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

# -------------------------------------------------------------
class SurveyPagination(PageNumberPagination):
    page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

# --------------------------------------------------------------
class SurveyOptionPagination(PageNumberPagination):
    page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

# ----------------------------------------------------------------
class SurveyOpinionPagination(PageNumberPagination):
    page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

# ----------------------------------------------------------------
class SurveySelectOptionPagination(PageNumberPagination):
    page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

# ----------------------------------------------------------------
class AdminPagination(PageNumberPagination):
    page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 1000

# ----------------------------------------------------------------
class EmailLogPagination(PageNumberPagination):
    page_size = 500
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 3000
