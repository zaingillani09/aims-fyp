import os
import sys
import django

# Add current working directory to sys.path
sys.path.append(os.getcwd())

# Set up django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aims.settings")
django.setup()

from accounts.models import User
from core.models import Faculty, Department, Notification
from issues.models import Issue, IssueDecision
from meetings.models import Meeting

def rebuild():
    print("--- 1. Cleaning up existing database records ---")
    
    # 1. Delete transactional records
    IssueDecision.objects.all().delete()
    Issue.objects.all().delete()
    Meeting.objects.all().delete()
    Notification.objects.all().delete()
    
    # 2. Delete existing users except the superuser zaingillani09
    User.objects.exclude(username="zaingillani09").delete()
    
    # 3. Delete old departments and faculties
    Department.objects.all().delete()
    Faculty.objects.all().delete()
    
    print("Cleanup completed.")

    print("\n--- 2. Creating Faculties and Departments ---")
    
    # Faculty 1
    f1 = Faculty.objects.create(name="ENGINEERING & IT")
    d1_1 = Department.objects.create(name="Electrical & Computer Engineering", faculty=f1)
    d1_2 = Department.objects.create(name="Engineering Technology", faculty=f1)
    d1_3 = Department.objects.create(name="Software Engineering", faculty=f1)
    
    # Faculty 2
    f2 = Faculty.objects.create(name="ARTS & SOCIAL SCIENCES")
    d2_1 = Department.objects.create(name="Allied Pool", faculty=f2)
    d2_2 = Department.objects.create(name="Arts & Media", faculty=f2)
    d2_3 = Department.objects.create(name="English", faculty=f2)
    d2_4 = Department.objects.create(name="Psychology", faculty=f2)
    
    # Faculty 3
    f3 = Faculty.objects.create(name="MANAGEMENT SCIENCES")
    d3_1 = Department.objects.create(name="Aviation Management", faculty=f3)
    d3_2 = Department.objects.create(name="Business Administration", faculty=f3)
    d3_3 = Department.objects.create(name="Economics & Finance", faculty=f3)
    d3_4 = Department.objects.create(name="Tourism & Hospitality", faculty=f3)
    
    print("Faculties and departments created successfully.")

    print("\n--- 3. Creating Deans, HODs, and Teachers ---")
    
    faculties = [f1, f2, f3]
    departments = [
        d1_1, d1_2, d1_3,
        d2_1, d2_2, d2_3, d2_4,
        d3_1, d3_2, d3_3, d3_4
    ]
    
    # 1. Create Deans
    deans_list = [
        ("dean_engineering", f1),
        ("dean_arts", f2),
        ("dean_management", f3)
    ]
    for username, fac in deans_list:
        email = f"{username}@aims.edu"
        user = User(
            username=username,
            email=email,
            first_name=username.split('_')[1].capitalize(),
            last_name="Dean",
            role=User.Role.DEAN,
            faculty=fac,
            must_change_password=False,
            profile_completed=True
        )
        user.set_password("pbpass123!")
        user.save()
        
        # Link dean to faculty
        fac.dean = user
        fac.save()
        print(f"Created Dean: {username} for {fac.name}")

    # 2. Create HODs and Teachers for each department
    dept_abbrs = {
        "Electrical & Computer Engineering": "ece",
        "Engineering Technology": "et",
        "Software Engineering": "se",
        "Allied Pool": "ap",
        "Arts & Media": "am",
        "English": "eng",
        "Psychology": "psy",
        "Aviation Management": "avm",
        "Business Administration": "ba",
        "Economics & Finance": "ef",
        "Tourism & Hospitality": "th"
    }
    for dept in departments:
        dept_abbr = dept_abbrs.get(dept.name)
        if not dept_abbr:
            dept_abbr = "".join([w[0].lower() for w in dept.name.split() if w[0].isalnum()])
        if not dept_abbr:
            dept_abbr = dept.name[:4].lower()
            
        hod_username = f"hod_{dept_abbr}"
        hod_user = User(
            username=hod_username,
            email=f"{hod_username}@aims.edu",
            first_name=dept.name,
            last_name="HOD",
            role=User.Role.HOD,
            faculty=dept.faculty,
            primary_department=dept,
            must_change_password=False,
            profile_completed=True
        )
        hod_user.set_password("pbpass123!")
        hod_user.save()
        
        dept.members.add(hod_user)
        dept.hod = hod_user
        dept.save()
        print(f"Created HOD: {hod_username} for {dept.name}")

        teacher_username = f"teacher_{dept_abbr}"
        teacher_user = User(
            username=teacher_username,
            email=f"{teacher_username}@aims.edu",
            first_name=dept.name,
            last_name="Teacher",
            role=User.Role.TEACHER,
            faculty=dept.faculty,
            primary_department=dept,
            must_change_password=False,
            profile_completed=True
        )
        teacher_user.set_password("pbpass123!")
        teacher_user.save()
        
        dept.members.add(teacher_user)
        teacher_user.departments.add(dept)
        print(f"Created Teacher: {teacher_username} for {dept.name}")

    # 3. Create Rector
    rector_user = User(
        username="rector",
        email="rector@aims.edu",
        first_name="Executive",
        last_name="Rector",
        role=User.Role.RECTOR,
        must_change_password=False,
        profile_completed=True
    )
    rector_user.set_password("pbpass123!")
    rector_user.save()
    print("Created Rector: rector")

    # 4. Create an Admin / Superuser automatically
    admin_username = "admin"
    if not User.objects.filter(username=admin_username).exists():
        admin_user = User(
            username=admin_username,
            email="admin@aims.edu",
            first_name="Portal",
            last_name="Administrator",
            is_staff=True,
            is_superuser=True,
            must_change_password=False,
            profile_completed=True
        )
        admin_user.set_password("admin123")
        admin_user.save()
        print("Created Superuser: admin (pass: admin123)")

    print("\nRebuild database and seed mock data successfully completed!")

if __name__ == "__main__":
    rebuild()
