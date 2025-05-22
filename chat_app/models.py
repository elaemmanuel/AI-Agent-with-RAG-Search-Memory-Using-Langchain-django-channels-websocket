from django.db import models

class ChatMessage(models.Model):
    session_id = models.CharField(max_length=255, db_index=True)
    role = models.CharField(max_length=20)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}"