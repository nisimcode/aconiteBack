from django.db import models


class JeopardyQuestion(models.Model):
    show_number = models.IntegerField()
    air_date = models.CharField(max_length=50)
    round = models.CharField(max_length=50)
    category = models.CharField(max_length=255)
    value = models.FloatField(null=True)
    question = models.TextField()
    answer = models.TextField()

    class Meta:
        ordering = ['-show_number', 'air_date']
        db_table = "jeopardy_questions"

    def __str__(self):
        return f"{self.show_number} - {self.category}"
