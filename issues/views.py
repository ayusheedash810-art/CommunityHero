from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, IssueForm
from django.contrib.auth.decorators import login_required
from .models import Issue, Verification
from django.db.models import Q
from .models import Issue, Profile
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
import google.generativeai as genai
import os
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
from django.db.models import Count

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")
def home(request):
    query = request.GET.get("q")
    status = request.GET.get("status")
    issues = Issue.objects.all().order_by("-created_at")
    if query:
        issues = issues.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query)
    )
    if status:
        issues = issues.filter(status=status)
    total_issues = Issue.objects.count()
    pending = Issue.objects.filter(status="Pending").count()
    resolved = Issue.objects.filter(status="Resolved").count()
    return render(
        request,
        "issues/home.html",
        {
            "user": request.user,
            "issues": issues,
            "total_issues": total_issues,
            "pending": pending,
            "resolved": resolved,
            "query": query,
            "status": status,
        },
    )


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            Profile.objects.create(user=user)

            login(request, user)

            return redirect("/")

    else:

        form = RegisterForm()

    return render(request, "issues/register.html", {"form": form})

def user_login(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("/")

    return render(request, "issues/login.html")
def user_logout(request):
    logout(request)
    return redirect("home")
@login_required
def report_issue(request):

    if request.method == "POST":

        form = IssueForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            issue = form.save(commit=False)
            issue.user = request.user

            prompt = f"""
Analyze this civic issue.

Title:
{issue.title}

Description:
{issue.description}

Return your answer EXACTLY in this format.

Category: <category>
Priority: <High/Medium/Low>
Summary: <one sentence summary>
Department: <department>
Solution: <short solution>

Choose category ONLY from:

Pothole
Garbage
Water Leakage
Street Light
Road Damage
Other
"""

            response = model.generate_content(prompt)

            result = response.text

            category = "Other"
            priority = "Medium"
            summary = "AI summary unavailable."
            department = ""
            solution = ""

            for line in result.splitlines():

                if line.startswith("Category:"):
                    category = line.replace("Category:", "").strip()

                elif line.startswith("Priority:"):
                    priority = line.replace("Priority:", "").strip()

                elif line.startswith("Summary:"):
                    summary = line.replace("Summary:", "").strip()    

                elif line.startswith("Department:"):
                    department = line.replace("Department:", "").strip()

                elif line.startswith("Solution:"):
                    solution = line.replace("Solution:", "").strip()

            valid_categories = [
                "Pothole",
                "Garbage",
                "Water Leakage",
                "Street Light",
                "Road Damage",
                "Other",
            ]

            valid_priorities = [
                "High",
                "Medium",
                "Low",
            ]

            if category in valid_categories:
                issue.category = category
            else:
                issue.category = "Other"

            if priority in valid_priorities:
                issue.priority = priority
            else:
                issue.priority = "Medium"

            issue.category = category
            issue.priority = priority
            issue.ai_summary = summary
            issue.department = department
            issue.ai_solution = solution

            issue.save()

            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.points += 10
            profile.save()

            return redirect("home")

    else:

        form = IssueForm()

    return render(
        request,
        "issues/report_issue.html",
        {
            "form": form
        }
    )
def issue_detail(request, pk):

    issue = get_object_or_404(Issue, pk=pk)

    verified = False

    if request.user.is_authenticated:
        verified = Verification.objects.filter(
            issue=issue,
            user=request.user
        ).exists()

    return render(
        request,
        "issues/issue_detail.html",
        {
            "issue": issue,
            "verified": verified,
        }
    )

@login_required
def edit_issue(request, pk):

    issue = get_object_or_404(Issue, pk=pk)

    if issue.user != request.user:
        return redirect("home")

    if request.method == "POST":

        form = IssueForm(
            request.POST,
            request.FILES,
            instance=issue
        )

        if form.is_valid():
            form.save()
            return redirect("issue_detail", pk=issue.pk)

    else:

        form = IssueForm(instance=issue)

    return render(
        request,
        "issues/report_issue.html",
        {
            "form": form
        }
    )
@login_required
def delete_issue(request, pk):

    issue = get_object_or_404(Issue, pk=pk)

    if issue.user != request.user:
        return redirect("home")

    if request.method == "POST":
        issue.delete()
        return redirect("home")

    return render(
        request,
        "issues/delete_issue.html",
        {
            "issue": issue
        }
    )
@login_required
def verify_issue(request, pk):

    issue = get_object_or_404(Issue, pk=pk)

    issue.verification_count += 1
    issue.save()
 
    profile, created = Profile.objects.get_or_create(user=request.user)
    profile.points += 5
    profile.save()

    return redirect("issue_detail", pk=pk)

@login_required
def verify_issue(request, pk):

    issue = get_object_or_404(Issue, pk=pk)

    Verification.objects.get_or_create(
        issue=issue,
        user=request.user
    )

    return redirect("issue_detail", pk=pk)

@staff_member_required
def update_status(request, pk):

    issue = get_object_or_404(Issue, pk=pk)

    if request.method == "POST":

        new_status = request.POST.get("status")

        issue.status = new_status

    if (
        new_status == "Resolved"
        and not issue.points_awarded
    ):
        profile, created = Profile.objects.get_or_create(user=issue.user)
        profile.points += 20
        profile.save()

        issue.points_awarded = True

    issue.save()
    return redirect("issue_detail", pk=pk)
@staff_member_required
def admin_dashboard(request):

    issues = Issue.objects.all().order_by("-created_at")

    category_data = (
    Issue.objects
    .values("category")
    .annotate(total=Count("category"))
    )

    status_data = (
    Issue.objects
    .values("status")
    .annotate(total=Count("status"))
    )
    top_category = (
    Issue.objects
    .values("category")
    .annotate(total=Count("category"))
    .order_by("-total")
    .first()
    )

    prediction = ""

    if top_category:
        prediction = (
            f"{top_category['category']} issues are increasing. "
            "The municipality should prioritize this category to prevent further complaints."
        )

    context = {
        "issues": issues,
        "total": Issue.objects.count(),
        "pending": Issue.objects.filter(status="Pending").count(),
        "resolved": Issue.objects.filter(status="Resolved").count(),
        "high": Issue.objects.filter(priority="High").count(),
        "medium": Issue.objects.filter(priority="Medium").count(),
        "low": Issue.objects.filter(priority="Low").count(),
        "category_data": category_data,
        "status_data": status_data,
        "prediction": prediction,
    }

    return render(
        request,
        "issues/admin_dashboard.html",
        context
    )
@staff_member_required
def predictive_insights(request):

    total = Issue.objects.count()

    pending = Issue.objects.filter(status="Pending").count()

    resolved = Issue.objects.filter(status="Resolved").count()

    high = Issue.objects.filter(priority="High").count()

    garbage = Issue.objects.filter(category="Garbage").count()

    pothole = Issue.objects.filter(category="Pothole").count()

    water = Issue.objects.filter(category="Water Leakage").count()

    street = Issue.objects.filter(category="Street Light").count()

    road = Issue.objects.filter(category="Road Damage").count()

    prompt = f"""
You are an AI civic planning assistant.

Here are the current city issue statistics.

Total Issues: {total}

Pending Issues: {pending}

Resolved Issues: {resolved}

High Priority Issues: {high}

Garbage: {garbage}

Potholes: {pothole}

Water Leakage: {water}

Street Lights: {street}

Road Damage: {road}

Provide:

1. Overall analysis

2. Biggest problem

3. Recommendation for the municipality

Keep it under 150 words.
"""

    response = model.generate_content(prompt)

    return render(
        request,
        "issues/predictive_insights.html",
        {
            "insight": response.text
        }
    )
def test_ai(request):

    response = model.generate_content(
        "Say hello in one sentence."
    )

    return render(
        request,
        "issues/test_ai.html",
        {
            "reply": response.text
        }
    )