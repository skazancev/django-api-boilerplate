from django.db import models


class DurationCountSubquery(models.Subquery):
    template = "(SELECT COALESCE(SUM(duration), 0) FROM (%(subquery)s) _count)"
    output_field = models.IntegerField()


class SQCount(models.Subquery):
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = models.IntegerField()


class SQSum(models.Subquery):
    template = "(SELECT COALESCE(SUM(%(field)s), 0) FROM (%(subquery)s) _sum)"
    output_field = models.IntegerField()
