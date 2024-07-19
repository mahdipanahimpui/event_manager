from functools import reduce
from operator import or_
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from . models import Participant




class Filtration:
    """
        important Note: Filteration class must be the first parrent class in child class
                        Otherwise, performance will be impaired
        important Note: the child class must inherit at least one of the subsequent classes that have get_queryset def
    """
    filtration_class = None
    pagination_class = None

    def check_filtration_class(self):
        if self.filtration_class is None:
            raise ValueError("Filtration_class is not defined.")
        
    def filter_queryset(self, queryset):
        try:
            return self.filtration_class().list(self.request, queryset)
        except Exception as e:
            raise RuntimeError("Filtration_class not provided in corrct way") from e

    def get_queryset(self):
        queryset = super().get_queryset()
        self.check_filtration_class()
        filtered_queryset = self.filter_queryset(queryset)
        
        return filtered_queryset
    
# --------------------------------------------------------------------------------------


########### Handlers ###########
# ----------------------------------------------------------------------------------------
class OrderingQueryHandler:
    def __init__(self, request, query_param='order_by', ascending_by_default=False):
        self.order_by_query = request.GET.get(query_param, None)

        self.ascending_query = str(request.GET.get('ascending', ascending_by_default)).lower()
        if self.ascending_query == 'true':
            self.ordering = ''
        elif self.ascending_query == 'false':
            self.ordering = '-'
        else:
            self.ordering = '' if ascending_by_default is True else '-'
            
    def get_result(self, queryset):
        if self.order_by_query is not None and hasattr(queryset.model, self.order_by_query):
            self.order_by_query = self.order_by_query 
            order_by = self.ordering + self.order_by_query
            queryset = queryset.order_by(order_by)

        return queryset

# -------------------------------------------------------------------------------------------------
class SearchQueryHandler:
    def __init__(self, request, query_param='search'):
            self.search_query = request.GET.get(query_param, None)

    def get_result(self, queryset, fields):

        if self.search_query:
            query = reduce(or_, [Q(**{field + '__icontains': self.search_query}) for field in fields])
            queryset = queryset.filter(query)

        return queryset

# -------------------------------------------------------------------------------------------------
class ChoiceFieldQueryHandler:
    def __init__(self, request, query_param, choices):
        self.choice_query = request.GET.get(query_param, None)
        self.choices = choices

    def get_result(self, queryset, fields):

        if self.choice_query in self.choices:
            query = reduce(or_, [Q(**{field + '__exact': self.choice_query}) for field in fields])
            queryset = queryset.filter(query)
        return queryset
    

    
# -------------------------------------------------------------------------------------------------
class StatusQueryHandler:
    def __init__(self, request, query_param='status', min=None, max=None):
        """
            <is not None> is used, because of falseness of 0
        """
        try:
            self.status_query = int(request.GET.get(query_param, None))

            if (min is not None) and  not (min <= self.status_query):
                error_message = 'out of rande error: min_value:{} <= {}  is not provided'.format(min, self.status_query)
                raise ValidationError(error_message)
            
            if (max is not None) and not (self.status_query <= max):
                error_message = 'out of rande error: {} <= max_value:{}  is not provided'.format(self.status_query, max)
                raise ValidationError(error_message)

        except (TypeError, ValueError):
            self.status_query = None
    
    def get_result(self, queryset, field_name='status'):            
        if self.status_query is not None: 
            query_condition = {field_name: self.status_query}
            queryset = queryset.filter(**query_condition)
        return queryset
    
# -------------------------------------------------------------------------------------------------
class NoneFiledQueryHandler:
    def __init__(self, request, query_param='attendance_time'):
        self.attended_query = request.GET.get(query_param, None)

    def get_result(self, queryset, field_name='attendance_time'):
        if self.attended_query == 'none': 
            query_condition = {field_name: None}
            queryset = queryset.filter(**query_condition)

        elif self.attended_query == 'not_none':
            query_condition = {field_name: None}
            queryset = queryset.exclude(query_condition)
        
        return queryset
    
# -----------------------------------------------------------------------------------------------
class BooleanStatusQueryHandler:
    def __init__(self, request, query_param=''):
        try: 
            self.status_query = str(request.GET.get(query_param, '')).lower()
        except (TypeError, ValueError):
            self.status_query = ''


    def get_result(self, queryset, field_name):
        if self.status_query == 'false': 
            query_condition = {field_name: False}
            queryset = queryset.filter(**query_condition)

        elif self.status_query == 'true':
            query_condition = {field_name: True}
            queryset = queryset.filter(**query_condition)
        
        return queryset
    
# --------------------------------------------------------------------------------
class RangeQueryHandler:
    def __init__(self, request, start_range_query_param, end_range_query_param):
        try:
            self.start_range_query = int(request.GET.get(start_range_query_param, None))
        except (TypeError, ValueError):
            self.start_range_query = None

        try:
            self.end_range_query = int(request.GET.get(end_range_query_param, None))
        except (TypeError, ValueError):
            self.end_range_query = None


    def get_result(self, queryset, field_name):
        if self.start_range_query is not None:
            query_condition = {f'{field_name}__gte': self.start_range_query}
            queryset = queryset.filter(**query_condition)
            
        if self.end_range_query is not None:
            query_condition = {f'{field_name}__lte': self.end_range_query}
            queryset = queryset.filter(**query_condition)

        return queryset
    

# --------------------------------------------------------------------------------------------------
class RelationIdsQueryHandler:

    def __init__(self, request, query_param):
        try: 
            self.relation_id_query = request.GET.get(query_param)
            self.relation_id_query =  int(self.relation_id_query) if self.relation_id_query.strip().isdigit() else None
        except (SyntaxError, NameError, AttributeError):
            self.relation_id_query = None

    def get_result(self, queryset, field_name):
        if self.relation_id_query is not None:
            query_condition = {f'{field_name}__id': self.relation_id_query}
            queryset = queryset.select_related(field_name)
            queryset = queryset.filter(**query_condition)
        return queryset



######## Filtrations ########
# ------------------------------------------------------------------------------------
class BaseFilter:
    
    def handle_filter(self, request, queryset):
        return queryset

    def list(self, request, filtration_queryset):
        temp_queryset = filtration_queryset
        temp_queryset = self.handle_filter(request, temp_queryset)
        temp_queryset = OrderingQueryHandler(request).get_result(temp_queryset)
        return temp_queryset
    
# ---------------------------------------------------------------------------------
class ParticipantFiltration(BaseFilter):

    def handle_filter(self, request, queryset):
        
        TITLE_CHOICES = [element[1] for element in Participant.TITLE_CHOICES]
        MEMBERSHIP_TYPE_CHOICES = [element[1] for element in Participant.MEMBERSHIP_TYPE_CHOICES]
        EDUCATION_LEVEL_CHOICES = [element[1] for element in Participant.EDUCATION_LEVEL_CHOICES]
        REGESTERED_AS_CHOICES = [element[1] for element in Participant.REGESTERED_AS_CHOICES]
        SCIENCE_RANKING_CHOICES = [element[1] for element in Participant.SCIENCE_RANKING_CHOICES]


        temp_queryset = queryset

        temp_queryset = NoneFiledQueryHandler(request, query_param='attendance_time').get_result(temp_queryset, field_name='attendance_time')
        temp_queryset = StatusQueryHandler(request, query_param='meal_status', min=0, max=2).get_result(temp_queryset, field_name='meal')

        temp_queryset = ChoiceFieldQueryHandler(request, query_param='title', choices=TITLE_CHOICES).get_result(temp_queryset, fields=['title'])
        temp_queryset = ChoiceFieldQueryHandler(request, query_param='regestered_as', choices=REGESTERED_AS_CHOICES).get_result(temp_queryset, fields=['regestered_as'])
        temp_queryset = ChoiceFieldQueryHandler(request, query_param='education_level', choices=EDUCATION_LEVEL_CHOICES).get_result(temp_queryset, fields=['education_level'])
        temp_queryset = ChoiceFieldQueryHandler(request, query_param='science_ranking', choices=SCIENCE_RANKING_CHOICES).get_result(temp_queryset, fields=['science_ranking'])
        temp_queryset = ChoiceFieldQueryHandler(request, query_param='membership_type', choices=MEMBERSHIP_TYPE_CHOICES).get_result(temp_queryset, fields=['membership_type'])

        temp_queryset = SearchQueryHandler(request).get_result(temp_queryset, ('first_name', 'last_name', 'mobile_phone_number', 'city', 'email_address'))

        return temp_queryset
    

# ---------------------------------------------------------------------------------
class EventFiltration(BaseFilter):

    def handle_filter(self, request, queryset):
        
        temp_queryset = queryset
        temp_queryset = BooleanStatusQueryHandler(request, query_param='is_active').get_result(temp_queryset, field_name='is_active')
        temp_queryset = BooleanStatusQueryHandler(request, query_param='survey_email_sent').get_result(temp_queryset, field_name='survey_email_sent')
        temp_queryset = BooleanStatusQueryHandler(request, query_param='sending_attendance_email').get_result(temp_queryset, field_name='sending_attendance_email')

        temp_queryset = SearchQueryHandler(request).get_result(temp_queryset, ('name', 'note'))

        return temp_queryset
    

# ---------------------------------------------------------------------------------
class MeetingFiltration(BaseFilter):

    def handle_filter(self, request, queryset):
        
        temp_queryset = queryset
        temp_queryset = SearchQueryHandler(request).get_result(temp_queryset, ('code', 'title', 'presenter', 'about_presenter', 'organizer', 'holding_place'))
        temp_queryset = BooleanStatusQueryHandler(request, query_param='survey_email_sent').get_result(temp_queryset, field_name='survey_email_sent')
        temp_queryset = BooleanStatusQueryHandler(request, query_param='sending_attendance_email').get_result(temp_queryset, field_name='sending_attendance_email')

        return temp_queryset
    
# -------------------------------------------------------------------------------------
class UserFiltration(BaseFilter):
    def handle_filter(self, request, queryset):
        temp_queryset = queryset
        temp_queryset = BooleanStatusQueryHandler(request, query_param='is_active').get_result(temp_queryset, field_name='is_active')
        temp_queryset = SearchQueryHandler(request).get_result(temp_queryset, ('username', 'email', 'first_name', 'last_name'))
        return temp_queryset
    
    def list(self, request, filtration_queryset):
        temp_queryset = filtration_queryset
        temp_queryset = self.handle_filter(request, temp_queryset)
        temp_queryset = OrderingQueryHandler(request, query_param='order_by', ascending_by_default=True).get_result(temp_queryset)
        return temp_queryset
    


# -------------------------------------------------------------------------------------
class EmailLogFiltration(BaseFilter):
    def handle_filter(self, request, queryset):
        
        temp_queryset = queryset
        temp_queryset = RelationIdsQueryHandler(request, query_param='meeting').get_result(temp_queryset, field_name='meeting')
        temp_queryset = SearchQueryHandler(request).get_result(temp_queryset, ('to', 'subject', 'body', 'title'))

        return temp_queryset
