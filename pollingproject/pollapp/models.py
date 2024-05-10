from django.db import models

# Create your models here.
class UserRegisterModel(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField()
    password = models.CharField(max_length=300)
    user_status = models.BooleanField(default=False)


class UserAccountVerificationModel(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)


class Poll(models.Model):
    question = models.CharField(max_length=200)
    image = models.FileField(upload_to="poll_images/", blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()


    def __str__(self):
        return self.question
    

class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
    

class PollRecord(models.Model):
    user_id = models.ForeignKey(UserRegisterModel, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username} voted for '{self.poll.question}' and chose '{self.choice.choice_text}'"

    
