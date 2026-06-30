from django.db import models
from django.contrib.auth.models import User

class Issue(models.Model):

    CATEGORY_CHOICES = [
        ("Pothole", "Pothole"),
        ("Garbage", "Garbage"),
        ("Water Leakage", "Water Leakage"),
        ("Street Light", "Street Light"),
        ("Road Damage", "Road Damage"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
    ]
    PRIORITY_CHOICES = [
    ("High", "High"),
    ("Medium", "Medium"),
    ("Low", "Low"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="Other"
    )

    image = models.ImageField(
        upload_to="issues/",
        blank=True,
        null=True
    )

    location = models.CharField(max_length=200)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    priority = models.CharField(
    max_length=10,
    choices=PRIORITY_CHOICES,
    default="Medium"
    )
    ai_solution = models.TextField(blank=True)

    department = models.CharField(
        max_length=100,
        blank=True
    )
    ai_summary = models.TextField(
    blank=True,
    null=True
    )
    verification_count = models.PositiveIntegerField(default=0)
    points_awarded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class Verification(models.Model):

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="verifications"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("issue", "user")    
class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    points = models.PositiveIntegerField(default=0)

    def badge(self):

        if self.points >= 200:
            return "🏆 Gold Hero"

        elif self.points >= 100:
            return "🥈 Silver Hero"

        elif self.points >= 50:
            return "🥉 Bronze Hero"

        return "🌱 New Citizen"

    def __str__(self):
        return self.user.username       

class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    points = models.PositiveIntegerField(default=0)

    def badge(self):

        if self.points >= 200:
            return "🏆 Gold Hero"

        elif self.points >= 100:
            return "🥈 Silver Hero"

        elif self.points >= 50:
            return "🥉 Bronze Hero"

        return "🌱 New Citizen"

    def __str__(self):
        return self.user.username     
