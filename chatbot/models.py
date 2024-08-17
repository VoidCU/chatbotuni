# models.py

from django.db import models

class Intent(models.Model):
    name = models.CharField(max_length=255, unique=True)
    response = models.TextField()

    def __str__(self):
        return self.name

class Example(models.Model):
    intent = models.ForeignKey(Intent, related_name='examples', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text

class Conversation(models.Model):
    user_id = models.CharField(max_length=255,null=True,blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    messages = models.TextField()  # Store messages separated by <sep> tag

    def __str__(self):
        return f"Conversation on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"