from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import Assignment, Role, Template, Fields, Approval, Request, Response, Requeststage, User
from django.db.models import Max
from django.db import connection, transaction



def home(request):
    return render(request, "home.html")

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import User

def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(home))
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            if username and password:
                # Check if the username is already taken
                if User.objects.filter(username=username).exists():
                    return render(request, 'register.html', {'error_message': 'Username already exists'})
                else:
                    # Create the new user
                    user = User.objects.create_user(username=username, password=password)
                    login(request, user)
                    return redirect('home')  # Redirect to the home page after successful registration
            else:
                return render(request, 'register.html', {'error_message': 'Username and password are required'})
        else:
            return render(request, 'register.html')

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import User

def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(home))
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            if username and password:
                # Authenticate against your custom user model
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home')  # Redirect to the home page after successful login
                else:
                    return render(request, 'login.html', {'error_message': 'Invalid username or password'})
            else:
                return render(request, 'login.html', {'error_message': 'Username and password are required'})
        else:
            return render(request, 'login.html')

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse(home))

def create_roles(request):
    if request.user.is_admin:
        if request.method == "POST":
            role_name = request.POST.get("name")

            # Execute raw SQL query to insert a new role
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO Role (name) VALUES (%s)", [role_name])

            return HttpResponseRedirect(reverse(home))  # Redirect to the same view after creating the role

        else:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name FROM Role")
                roles = cursor.fetchall()

            return render(request, "create_role.html", {"roles": roles})
    else:
        return HttpResponseRedirect(reverse(home))

def assign_roles(request):
    if request.user.is_admin:
        if request.method == "POST":
            user_id = request.POST["user_id"]
            role_id = request.POST["role_id"]

            with connection.cursor() as cursor:
                # Check if the assignment already exists
                cursor.execute("""
                    SELECT id FROM Assignment
                    WHERE role_id = %s AND user_id = %s
                """, [role_id, user_id])
                assignment_exists = cursor.fetchone()

                if not assignment_exists:
                    # Insert new assignment
                    cursor.execute("""
                        INSERT INTO Assignment (role_id, user_id)
                        VALUES (%s, %s)
                    """, [role_id, user_id])

                    # Check if the role being assigned is "Admin"
                    cursor.execute("""
                        SELECT name FROM Role WHERE id = %s
                    """, [role_id])
                    role_name = cursor.fetchone()[0]

                    # If role name is "Admin", set user's is_admin to True
                    if role_name == "Admin":
                        cursor.execute("""
                            UPDATE User SET is_admin = TRUE WHERE id = %s
                        """, [user_id])

            return HttpResponseRedirect(reverse(assign_roles))
        else:
            # Fetch all assignments
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT A.id, U.username, R.name
                    FROM Assignment A
                    INNER JOIN User U ON A.user_id = U.id
                    INNER JOIN Role R ON A.role_id = R.id
                """)
                assignments = cursor.fetchall()

            all_roles = Role.objects.all()
            all_users = User.objects.all()

            return render(request, "assign_role.html", {
                "all_roles": all_roles,
                "all_users": all_users,
                "assignments": assignments  # Pass assignments to the template context
            })
    else:
        return HttpResponseRedirect(reverse(home))


def delete_role(request, id):
    if request.user.is_admin:
        if request.method == "POST":
            with connection.cursor() as cursor:
                # Execute raw SQL query to delete the role
                cursor.execute("DELETE FROM Role WHERE id = %s", [id])

                return HttpResponseRedirect(reverse(create_roles))  # Redirect to the create_roles view
        else:
            return HttpResponseRedirect(reverse(home))
    else:
        return HttpResponseRedirect(reverse(home))

def delete_assignment(request, id):
    if request.user.is_admin:
        if request.method == "POST":
            with connection.cursor() as cursor:
                # Execute raw SQL query to delete the role
                cursor.execute("DELETE FROM Assignment WHERE id = %s", [id])

                return HttpResponseRedirect(reverse(assign_roles))  # Redirect to the create_roles view
        else:
            return HttpResponseRedirect(reverse(home))
    else:
        return HttpResponseRedirect(reverse(home))

def delete_template(request, id):
    if request.user.is_admin:
        if request.method == "POST":
            with connection.cursor() as cursor:
                try:
                    # Manually delete related approvals
                    cursor.execute("DELETE FROM Approval WHERE template_id = %s", [id])

                    cursor.execute("DELETE FROM Fields WHERE template_id = %s", [id])

                    # Now delete the template
                    cursor.execute("DELETE FROM Template WHERE id = %s", [id])

                    # Commit the transaction
                    transaction.commit()

                    return HttpResponseRedirect(reverse('templates'))  # Redirect to the templates view
                except Exception as e:
                    # Rollback the transaction in case of an error
                    transaction.rollback()
                    raise e
        else:
            return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse('home'))


def templates(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            # Get all templates using SQL query
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, title FROM Template")
                t_templates = cursor.fetchall()

            return render(request, "templates.html", {
                "templates": t_templates
            })

        else:
            title = request.POST["title"]
            user = request.user

            # Create template
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO Template (title, user_id) VALUES (%s, %s)", [title, user.id])

            return HttpResponseRedirect(reverse(templates))

    else:
        return HttpResponseRedirect(reverse(user_login))

def template(request, id):
    if request.user.is_authenticated:
        with connection.cursor() as cursor:
            # Get template using SQL query
            cursor.execute("SELECT id, title, user_id FROM Template WHERE id = %s", [id])
            template_row = cursor.fetchone()

            if template_row:
                template_id, template_title, user_id = template_row

                # Get template's user's username
                cursor.execute("SELECT username FROM User WHERE id = %s", [user_id])
                user_row = cursor.fetchone()
                user_username = user_row[0] if user_row else None

                # Get all fields associated with the template using SQL query
                cursor.execute("SELECT id, name, type, required, text FROM Fields WHERE template_id = %s", [template_id])
                fields = cursor.fetchall()

                # Get all approvals associated with the template using SQL query
                cursor.execute("""
                    SELECT A.id, A.stage, R.id AS role_id, R.name AS role_name
                    FROM Approval A
                    INNER JOIN Role R ON A.role_id = R.id
                    WHERE A.template_id = %s
                """, [template_id])
                approvals = cursor.fetchall()

                # Get all roles using SQL query
                cursor.execute("SELECT id, name FROM Role")
                all_roles = cursor.fetchall()

                # Get all users using SQL query
                cursor.execute("SELECT id, username FROM User")
                all_users = cursor.fetchall()

                # Get all requests made by the user to this template
                cursor.execute("SELECT id, status FROM Request WHERE user_id = %s AND template_id = %s", [request.user.id, template_id])
                user_requests = cursor.fetchall()

                return render(request, "template.html", {
                    "template": {'id': template_id, 'title': template_title, 'user': {'id': user_id, 'username': user_username}},
                    "fields": fields,
                    "approvals": approvals,
                    "all_roles": all_roles,
                    "all_users": all_users,
                    "user_requests": user_requests
                })

        # If template with given id is not found or there's an error, redirect to home
        return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse('home'))


def create_field(request, id):
    if request.user.is_admin:
        if request.method == "POST":
            template_id = id
            question = request.POST["question"]

            with connection.cursor() as cursor:
                # Insert a new field using SQL query
                cursor.execute("""
                    INSERT INTO Fields (template_id, name)
                    VALUES (%s, %s)
                """, [template_id, question])

            return HttpResponseRedirect(reverse('template', args=(id,)))
        else:
            return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse('home'))


def create_approval(request, id):
    if request.user.is_admin:
        if request.method == "POST":
            template_id = id
            role_id = request.POST.get("role", None)

            with connection.cursor() as cursor:
                # Get the maximum stage for approvals associated with the template
                cursor.execute("""
                    SELECT MAX(stage) FROM Approval WHERE template_id = %s
                """, [template_id])
                max_stage_result = cursor.fetchone()
                max_stage = max_stage_result[0] if max_stage_result[0] is not None else 0
                print("########################################", max_stage)

                # Insert a new approval using SQL query
                cursor.execute("""
                    INSERT INTO Approval (template_id, stage)
                    VALUES (%s, %s)
                """, [template_id, max_stage + 1])

                # Get the ID of the newly inserted approval
                new_approval_id = cursor.lastrowid

                # Update the newly inserted approval with user or role information if provided

                cursor.execute("""
                    UPDATE Approval SET role_id = %s WHERE id = %s
                """, [role_id, new_approval_id])

            return HttpResponseRedirect(reverse('template', args=(id,)))
        else:
            return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse('home'))

from django.db import connection
from django.http import HttpResponseRedirect
from django.urls import reverse

def create_request(request, id):
    if request.user.is_authenticated:
        if request.method == "POST":
            template_id = id
            user_id = request.user.id

            with connection.cursor() as cursor:
                # Insert a new request using SQL query
                cursor.execute("""
                    INSERT INTO Request (user_id, template_id, approval_stage, status)
                    VALUES (%s, %s, %s, 'InProgress')
                """, [user_id, template_id, 1])

                # Get the ID of the newly inserted request
                new_request_id = cursor.lastrowid

                # Create responses for the newly created request
                cursor.execute("SELECT id FROM Fields WHERE template_id = %s", [template_id])
                template_fields = cursor.fetchall()
                for field_id_tuple in template_fields:
                    field_id = field_id_tuple[0]  # Extracting the field ID from the tuple
                    answer = request.POST.get(str(field_id), False)
                    if answer:
                        cursor.execute("""
                            INSERT INTO Response (request_id, question_id, answer)
                            VALUES (%s, %s, %s)
                        """, [new_request_id, field_id, answer])

            return HttpResponseRedirect(reverse('template', args=(id,)))
        else:
            with connection.cursor() as cursor:
                # Fetch template details
                cursor.execute("SELECT * FROM Template WHERE id = %s", [id])
                template = cursor.fetchone()

                # Fetch template fields
                cursor.execute("SELECT id, name FROM Fields WHERE template_id = %s", [id])
                fields = cursor.fetchall()

                return render(request, "create_request.html", {
                    "template": template,
                    "fields": fields
                })
    else:
        return HttpResponseRedirect(reverse('home'))


def template_request(request, id):
    if request.user.is_authenticated:
        user_id = request.user.id
        # Get request details using SQL query
        with connection.cursor() as cursor:

            is_approver = False
            is_approved = False

            cursor.execute("""
                SELECT R.status
                FROM Request R
                WHERE R.id = %s
            """, [id])

            approved_query = cursor.fetchone()
            if approved_query[0] == "Approved":
                is_approved = True
            role_id_req_stage = [False, False]
            if not is_approved:

                cursor.execute("""
                    SELECT RS.id, A.role_id
                    FROM RequestStage RS
                    INNER JOIN Approval A ON RS.approval_id = A.id
                    INNER JOIN Role R ON A.role_id = R.id
                    WHERE RS.request_id = %s AND A.stage = (SELECT approval_stage FROM Request WHERE id = %s)
                    LIMIT 1
                """, [id, id])

                role_id_req_stage = cursor.fetchone()
                cursor.execute("""
                    SELECT COUNT(*) FROM Assignment
                    WHERE user_id = %s AND role_id = %s
                """, [user_id, role_id_req_stage[1]])
                result = cursor.fetchone()
                if result[0] > 0:
                    is_approver = True


            cursor.execute("""
                SELECT R.id, R.status, R.approval_stage, T.id AS template_id, T.title AS template_title,
                       (SELECT approval_stage FROM Request WHERE id = %s) AS current_approval, R.user_id
                FROM Request R
                INNER JOIN Template T ON R.template_id = T.id
                WHERE R.id = %s
            """, [id, id])
            request_row = cursor.fetchone()

            if request_row:
                request_id, request_status, approval_stage, template_id, template_title, current_approval, request_user_id = request_row

                if is_approver or user_id == request_user_id:

                    # Get fields and their responses using SQL query
                    cursor.execute("""
                        SELECT F.id, F.name, COALESCE(RE.answer, '') AS answer
                        FROM Fields F
                        LEFT JOIN Response RE ON F.id = RE.question_id AND RE.request_id = %s
                        WHERE F.template_id = %s
                    """, [request_id, template_id])
                    fields = cursor.fetchall()

                    # Get approvals for the template using SQL query
                    cursor.execute("""
                        SELECT A.id, A.stage, R.id AS role_id, R.name AS role_name
                        FROM Approval A
                        INNER JOIN Role R ON A.role_id = R.id
                        WHERE A.template_id = %s
                    """, [template_id])
                    approvals = cursor.fetchall()
                    # is_approver = False
                    # cursor.execute("""
                    #     SELECT RS.id, A.role_id
                    #     FROM RequestStage RS
                    #     INNER JOIN Approval A ON RS.approval_id = A.id
                    #     INNER JOIN Role R ON A.role_id = R.id
                    #     WHERE RS.request_id = %s AND A.stage = (SELECT approval_stage FROM Request WHERE id = %s)
                    #     LIMIT 1
                    # """, [id, id])

                    # role_id = cursor.fetchone()
                    # cursor.execute("""
                    #     SELECT COUNT(*) FROM Assignment
                    #     WHERE user_id = %s AND role_id = %s
                    # """, [user_id, role_id[1]])
                    # result = cursor.fetchone()
                    # if result[0] > 0:
                    #     is_approver = True

                    # Get request stages for the request using SQL query
                    cursor.execute("""
                        SELECT RS.id, RS.approved, RS.approved_timestamp, A.role_id, R.name AS role_name, A.stage AS approval_stage
                        FROM RequestStage RS
                        INNER JOIN Approval A ON RS.approval_id = A.id
                        INNER JOIN Role R ON A.role_id = R.id
                        WHERE RS.request_id = %s
                    """, [request_id])
                    request_stages = cursor.fetchall()


                    if request.method == "GET":
                        return render(request, "template_request.html", {
                            "template": {'id': template_id, 'title': template_title},
                            "requests": {'id': request_id, 'status': request_status, 'approval_stage': approval_stage},
                            "fields": fields,
                            "approvals": approvals,
                            "request_stages": request_stages,
                            "is_approver": is_approver,
                            "current_req_stage_id": role_id_req_stage[0]
                        })


                    elif request.method == "POST" and request_status == 'SubmissionPending':
                        # Update responses if the request status is SubmissionPending
                        for field in fields:
                            field_id, _, _, _, _, _ = field
                            answer = request.POST.get(str(field_id), False)
                            if answer is not False:
                                cursor.execute("""
                                    INSERT INTO Response (request_id, question_id, answer)
                                    VALUES (%s, %s, %s)
                                    ON DUPLICATE KEY UPDATE answer = %s
                                """, [request_id, field_id, answer, answer])

                        # Update request status to InProgress
                        cursor.execute("UPDATE Request SET status = 'InProgress' WHERE id = %s", [request_id])

                        return HttpResponseRedirect(reverse('fill_response', args=(request_id,)))
                else:
                    return HttpResponseRedirect(reverse(home))
            else:
                return HttpResponseRedirect(reverse(user_login))
    else:
        return HttpResponseRedirect(reverse(user_login))

def approval_requests(request):
    if request.user.is_authenticated:
        user_id = request.user.id

        with connection.cursor() as cursor:
            # Fetch all the approval requests
            cursor.execute("""
                SELECT REQ.id, RS.approved, RS.approved_timestamp, A.role_id, R.name AS role_name, U.username AS request_username, T.title AS template_title, A.stage
                FROM RequestStage RS
                INNER JOIN Approval A ON RS.approval_id = A.id
                INNER JOIN Role R ON A.role_id = R.id
                INNER JOIN Request REQ ON RS.request_id = REQ.id
                INNER JOIN User U ON REQ.user_id = U.id
                INNER JOIN Template T ON REQ.template_id = T.id
                WHERE REQ.approval_stage = A.stage
                AND A.role_id IN (
                    SELECT role_id
                    FROM Assignment
                    WHERE user_id = %s
                )

            """, [user_id])
            approval_requests = cursor.fetchall()

            return render(request, "approval_requests.html", {"approval_requests": approval_requests})
    else:
        return HttpResponseRedirect(reverse(user_login))


def approve_request(request, id):
    if request.user.is_authenticated:
        if request.method == "POST":
            user_id = request.user.id
            with connection.cursor() as cursor:

                is_approver = False
                cursor.execute("""
                    SELECT A.role_id
                    FROM RequestStage RS
                    INNER JOIN Approval A ON RS.approval_id = A.id
                    WHERE RS.id = %s
                    LIMIT 1
                """, [id])

                role_id_req_stage = cursor.fetchone()
                cursor.execute("""
                    SELECT COUNT(*) FROM Assignment
                    WHERE user_id = %s AND role_id = %s
                """, [user_id, role_id_req_stage[0]])
                result = cursor.fetchone()
                if result[0] > 0:
                    is_approver = True

                if is_approver:
                # Fetch the RequestStage details
                    cursor.execute("""
                        SELECT RS.id, RS.approval_id, RS.approved, A.stage, REQ.approval_stage AS current_approval_stage
                        FROM RequestStage RS
                        INNER JOIN Approval A ON RS.approval_id = A.id
                        INNER JOIN Request REQ ON RS.request_id = REQ.id
                        WHERE RS.id = %s
                    """, [id])
                    request_stage = cursor.fetchone()

                    if request_stage:
                        rs_id, approval_id, approved, approval_stage, current_approval_stage = request_stage

                        # Check if the approval stage matches the current approval stage
                        if approval_stage == current_approval_stage:
                            # Check if the request is not already approved
                            if not approved:
                                # Mark the request stage as approved
                                cursor.execute("UPDATE RequestStage SET approved = 1 WHERE id = %s", [rs_id])

                                # Update the current approval stage of the request
                                cursor.execute("UPDATE Request SET approval_stage = approval_stage + 1 WHERE id = (SELECT request_id FROM RequestStage WHERE id = %s)", [rs_id])

            return HttpResponseRedirect(reverse('approval_requests'))
        else:
            return HttpResponseRedirect(reverse('approval_requests'))
    else:
        return HttpResponseRedirect(reverse('home'))

def get_all_requests(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        with connection.cursor() as cursor:
            # Fetch all the approval requests
            cursor.execute("""
                SELECT REQ.id, REQ.status, T.title AS template_title
                FROM Request REQ
                INNER JOIN Template T ON REQ.template_id = T.id
                WHERE REQ.user_id = %s
            """, [user_id])
            all_requests = cursor.fetchall()

        return render(request, "all_requests.html", {
            "requests" : all_requests
        })
