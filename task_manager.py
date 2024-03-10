import os
from datetime import datetime, date
from reference_items import greeting, menu_title, menu_items, admin_menu_items, update_menu, goodbye


# Stores two datetime formats for use in varying reports
DATETIME_STRING_FORMAT = "%Y-%m-%d"
REPORT_DATETIME_FORMAT = "%A %d %B %Y"


def read_task_file():
    """Reads the contents of the task.txt file and returns
    each task as separate element in a list.
    """

    with open("tasks.txt", 'r', encoding="utf-8") as task_file:
        contents = task_file.read().split("\n")

    task_data = [i for i in contents if i]      # Removes any blank spaces from the 'contents' list

    return task_data


def read_user_file():
    """Returns the users in user.txt as a dictionary."""

    # Read in user_data from the text file and save as a list to user_data
    with open("user.txt", 'r', encoding="utf-8") as user_file:
        user_data = user_file.read().split("\n")

    # Convert user_data to a dictionary
    username_password = {}
    for user in user_data:
        username, password = user.split(';')
        username_password[username] = password

    return username_password


def reg_user(login_dict):
    """Register a new user and save the details to the user.txt file.
    This also checks the existing user database to prevent registering
    a username that is already take.
    """

    existing_user = True
    password_match = False

    print("\n\n\n----- Register a new user -----")

    # Checks to avoid adding a new username if the username is already taken
    while existing_user:

        new_username = input("New Username: ")

        if new_username in login_dict.keys():
            print("\nThis username is already taken. Please try again:")
            continue
        else:
            existing_user = False


    # Checks to ensure that both passwords match
    while not password_match:

        new_password = input("New Password: ")
        confirm_password = input("Confirm Password: ")

        # Adds the details to the user.txt file if it passes the valdiation
        if new_password == confirm_password:
            with open("user.txt", "a", encoding="utf-8") as out_file:
                out_file.write(f"\n{new_username};{new_password}")
            print("\nNew user added successfully!")
            password_match = True
        else:
            print("\nPasswords do not match. Please try again:")
            continue


def add_task(login_dict):
    """Allow a user to add a new task to the task.txt file.
        Prompt a user for the following: 
            - A username of the person whom the task is assigned to,
            - A title of a task,
            - A description of the task and 
            - The due date of the task
            """


    print("\n\n\n----- Add a new task -----\n")

    user_exists = False

    # Ensure that user assigns the task to a valid user before moving on
    while not user_exists:

        task_username = input("Name of person assigned to task: ")

        if task_username not in login_dict.keys():
            print("\nUser does not exist. Please enter a valid username: ")
            continue
        else:
            user_exists = True


    task_title = input("Title of Task: ")

    task_description = input("Description of Task: ")

    task_due_date = assign_date()   # Requests the user to enter a due date in the correct format

    # Stores and formats the current date
    curr_date = date.today()
    task_assigned_date = curr_date.strftime(DATETIME_STRING_FORMAT)

    # Appends the new task to the tasks.txt file
    with open("tasks.txt", "a", encoding="utf-8") as task_file:
        task_file.write(f"{task_username};{task_title};{task_description};{task_due_date};{task_assigned_date};No\n")

    print("Task added successfully.")
    return 1        # Returns 1 which add to the tasks_generated counter


def view_all():
    """Prints all the tasks listed in the tasks.txt file."""

    print("\n\n\n----- View all tasks -----")

    # Generates an up-to-date task list for all users using the create_task_list() function
    task_list = create_task_list("all_users")

    # Loops through each task and returns the task attributes in a user friendly format
    for task in task_list:
        disp_str = f"Task: \t\t\t {task['title']}\n"
        disp_str += f"Assigned to: \t\t {task['username']}\n"
        disp_str += f"Date Assigned: \t\t {task['assigned_date'].strftime(REPORT_DATETIME_FORMAT)}\n"
        disp_str += f"Due Date: \t\t {task['due_date'].strftime(REPORT_DATETIME_FORMAT)}\n"
        disp_str += f"Task Description: \t {task['description']}\n"

        if task['completed']:
            completion_status = "Yes"
        else:
            completion_status = "No"

        disp_str += f"Completed: \t\t {completion_status}\n"

        print("\n", disp_str, "_" * 50, sep = "\n")


def view_mine(user):
    """Prints all the tasks that have been assigned to the current user.
    Asks the user to select a task to update and returns the selected task in a dictionary.
    """

    print("\n\n\n----- View all tasks for current user -----")

    # Generates a up-to-date task list for the current user using the create_task_list() function
    task_list = create_task_list(user)
    task_count = 0

    # Loops through each task and outputs the task attributes and outputs each task
    for task in task_list:
        task_count += 1
        disp_str = f"Task {task_count}: \t\t {task['title']}\n"
        disp_str += f"Assigned to: \t\t {task['username']}\n"
        disp_str += f"Date Assigned: \t\t {task['assigned_date'].strftime(REPORT_DATETIME_FORMAT)}\n"
        disp_str += f"Due Date: \t\t {task['due_date'].strftime(REPORT_DATETIME_FORMAT)}\n"
        disp_str += f"Task Description: \t {task['description']}\n"

        if task['completed']:
            completion_status = "Yes"
        else:
            completion_status = "No"

        disp_str += f"Completed: \t\t {completion_status}\n"

        print("\n", disp_str, "_" * 50, sep = "\n")


    # Allows the user to select a task to change
    while True:
        task_number = input("""
        \nPlease select the task number you would like the edit: (-1 for main menu)\n> """)

        # Handles incorrect or invalid user input and returns a valid user input
        try:
            if 0 < int(task_number) <= len(task_list):
                selected_task = task_list[int(task_number)-1]
                if selected_task["completed"]:
                    print("You cannot change a completed task.")
                else:
                    return selected_task
            elif int(task_number) == -1:
                return -1
            else:
                print("Your selection is out of range. Please try again.")

        except ValueError:
            print("Please enter a number.")


def update_task(task_dict, login_dict):
    """Allows the user to update the selected task.
    The user can update the following:
        - Assigned user
        - Due date
        - Completion status
        """

    # Stores the task attributes with the original task details
    task_username = task_dict["username"]
    task_title = task_dict["title"]
    task_description = task_dict["description"]
    task_due_date = task_dict["due_date"].date()
    task_assigned_date = task_dict["assigned_date"].date()
    completed = "No"

    # Retains the old task format so that it can be identified and replaced in the tasks.txt file
    original_task = f"{task_username};{task_title};{task_description};{task_due_date};{task_assigned_date};No"


    while True:
        # Imports update menu and request user selection
        update_selection = input(update_menu).lower()

        if update_selection == "a":
            print("\nYou have selected: Change assigned user.")

            # Ensures the new username exists before accepting the change
            while True:
                task_username = input("Name of person assigned to task: ")
                if task_username not in login_dict.keys():
                    print("\nUser does not exist. Please enter a valid username: ")
                    continue
                else:
                    break

        elif update_selection == "d":
            print("\nYou have selected: Change due date.")

            task_due_date = assign_date()       # Validates data entry for new date

        elif update_selection == "m":
            print("\nYou have selected: Mark task as complete.")
            completed = "Yes"
            print("\nThe task has been marked as complete.")

        elif update_selection == "s":

            updated_task_format = f"{task_username};{task_title};{task_description};{task_due_date};{task_assigned_date};{completed}"

            with open("tasks.txt", "r", encoding="utf-8") as task_file:
                filedata = task_file.read()

            # Identifies original task and replaces it with the updates
            filedata = filedata.replace(original_task, updated_task_format)

            with open("tasks.txt", "w", encoding="utf-8") as task_file:
                task_file.write(filedata)

            print("\nYour changes have been saved.")
            break

        elif update_selection == "e":
            print("\nYour changes have not been saved.")
            break

        else:
            print("\nPlease select a valid option.")


def assign_date():
    """Requests the user to enter a valid due date and performs data validation.
    The due date must be entered in the specified format (YYYY-MM-DD)
    and must be a future date for the date to be returned by the function.
    """

    # Stores the current date
    curr_date = date.today()


    while True:
        # Ensures that the due date is entered in the correct format
        try:
            due_date = input("Due date of task (YYYY-MM-DD): ")
            task_due_date = datetime.strptime(due_date, DATETIME_STRING_FORMAT).date()

            # Ensures that the due date is set to a future date
            if task_due_date < curr_date:
                print("\nYou cannot set a task for a date in the past:")
                continue
            else:
                return task_due_date
        except ValueError:
            print("\nInvalid datetime format. Please use the format specified:")


def gen_report(t_gen, all_users):
    """Creates two reports named task_overview.txt and user_overview.txt based on
    the current contents of the tasks.txt and users.txt.
    """

    # Creates task_overview.txt

    current_date = date.today()
    time = datetime.now()
    current_time = time.strftime("%H:%M%p")

    task_data = read_task_file()        # Stores a list of tasks from the tasks.txt file

    tot_tasks = []
    comp_tasks = []
    overd_incomp = []

    # Identifies total tasks, completed tasks and overdue and incomplete tasks
    for t_str in task_data:

        task_components = t_str.split(";")

        tot_tasks.append(task_components[0])

        if task_components[5] == "Yes":
            comp_tasks.append(task_components[0])

        due_date = datetime.strptime(task_components[3], DATETIME_STRING_FORMAT).date()
        if due_date < current_date:
            if task_components[5] == "No":
                overd_incomp.append(task_components[0])

    # Generates report data from the 3 lists defined above
    total = len(tot_tasks)
    completed = len(comp_tasks)
    uncompleted = total - completed
    overdue = len(overd_incomp)
    percent_comp = 0 if total == 0 else (completed / (completed + uncompleted)) * 100
    percent_incomp = 0 if total == 0 else (uncompleted / (completed + uncompleted)) * 100

    # Records data in a user friendly format
    task_report = f"Report generated on {current_date} at {current_time}:\n"
    task_report += f"-" * 42 + "\n"
    task_report += f"Total number of tasks generated this session: \t\t{t_gen}\n"
    task_report += f"Total number of tasks: \t\t\t\t\t\t\t\t{total}\n"
    task_report += f"Total number of tasks completed: \t\t\t\t\t{completed}\n"
    task_report += f"Total number of tasks uncompleted: \t\t\t\t\t{uncompleted}\n"
    task_report += f"Total number of overdue tasks: \t\t\t\t\t\t{overdue}\n"
    task_report += f"Percentage of tasks completed: \t\t\t\t\t\t{round(percent_comp)}%\n"
    task_report += f"Percentage of tasks uncompleted: \t\t\t\t\t{round(percent_incomp)}%\n"
    task_report += f"-" * 55 + "\n\n\n"

    with open("task_overview.txt", "a", encoding="utf-8") as file:
        file.write(task_report)


    # Creates user_overview.txt

    # Generates a list of all users from users.txt
    list_of_users = all_users.keys()
    total_num_users = len(list_of_users)
    each_user = []


    for user in list_of_users:
        user_total = tot_tasks.count(user)
        # Handles users with no tasks in tasks.txt
        if user_total == 0:
            perc_tot = 0
            perc_comp = 0
            perc_uncomp = 0
            perc_over = 0
        else:
            perc_tot = round((user_total / len(tot_tasks)) * 100 )
            perc_comp = round((comp_tasks.count(user) / user_total) * 100)
            perc_uncomp = round(100 - perc_comp)
            perc_over = round((overd_incomp.count(user) / user_total) * 100)

        each_user.append([user, user_total, perc_tot, perc_comp, perc_uncomp, perc_over])

    # Formats current data for the report
    overview_report = f"Report generated on {current_date} at {current_time}:\n"
    overview_report += "-" * 50 + "\n"
    overview_report += f"Total number of users: \t\t\t{total_num_users}\n"
    overview_report += f"Total number of tasks: \t\t\t{total}"
    overview_report += "\n" + "-" * 50 + "\n"

    for user in each_user:
        overview_report += f"Current user: \t\t\t\t\t{user[0]}\n"
        overview_report += f"Number of tasks: \t\t\t\t{user[1]}\n"
        overview_report += f"Percentage all tasks: \t\t\t{user[2]}%\n"
        overview_report += f"Percentage completed tasks: \t{user[3]}%\n"
        overview_report += f"Percentage uncompleted tasks: \t{user[4]}%\n"
        overview_report += f"Percentage overdue tasks: \t\t{user[5]}%\n"
        overview_report += "-" * 50 + "\n"

    overview_report += "\n\n"

    with open("user_overview.txt", "a", encoding="utf-8") as user_file:
        user_file.write(overview_report)


    print("\n\n-- Reports have been generated successfully --")


def create_task_list(chosen_user):
    """Generates a dictionary for each task and nests each dictionary within a single list.
    The function returns the list as its output.
    To return all tasks, pass "all_users" as an argument.
    """

    # Creates tasks.txt if it doesn't exist
    if not os.path.exists("tasks.txt"):
        with open("tasks.txt", "w", encoding="utf-8") as file:
            pass

    task_data = read_task_file()

    task_list = []

    for each_task in task_data:
        current_task = {}

        if chosen_user == "all_users":
            # Split by semicolon and manually add each component
            task_components = each_task.split(";")
            current_task['username'] = task_components[0]
            current_task['title'] = task_components[1]
            current_task['description'] = task_components[2]
            current_task['due_date'] = datetime.strptime(task_components[3], DATETIME_STRING_FORMAT)
            current_task['assigned_date'] = datetime.strptime(task_components[4], DATETIME_STRING_FORMAT)
            current_task['completed'] = True if task_components[5] == "Yes" else False
        else:
            task_components = each_task.split(";")
            if task_components[0] == chosen_user:
                current_task['username'] = task_components[0]
                current_task['title'] = task_components[1]
                current_task['description'] = task_components[2]
                current_task['due_date'] = datetime.strptime(task_components[3], DATETIME_STRING_FORMAT)
                current_task['assigned_date'] = datetime.strptime(task_components[4], DATETIME_STRING_FORMAT)
                current_task['completed'] = True if task_components[5] == "Yes" else False

        if not current_task:
            pass
        else:
            task_list.append(current_task)

    return task_list



# ===== Login Section =====
# This code reads usernames and password from the user.txt file to allow a user to login

# If no user.txt file, write one with a default account
if not os.path.exists("user.txt"):
    with open("user.txt", "w", encoding="utf-8") as default_file:
        default_file.write("admin;password")


# Creates a dictionary with all listed users in the user.txt file
username_dict = read_user_file()


# Creates a tasks.txt file if it does not already exist
if not os.path.exists("tasks.txt"):
    with open("tasks.txt", "w", encoding="utf-8") as default_file:
        pass


# task_data = read_task_file()


logged_in = False

print("-"*58, greeting, "\n", "-"*58)

while not logged_in:
    print("\nLOGIN")

    curr_user = input("Username: ")
    curr_pass = input("Password: ")

    if curr_user not in username_dict.keys():
        print("User does not exist")
    elif username_dict[curr_user] != curr_pass:
        print("Wrong password")
    else:
        print("Login Successful!")
        logged_in = True



tasks_generated = 0         # Counts the number of tasks generated this login session


while True:

    # Presents the menu to the user and converts user input to lower case.
    # The admin is presented with a separate menu to other users.
    if curr_user == "admin":
        print("\n\n", "-"*46, menu_title, "\n", "-"*46, sep="")
        menu_selection = input(admin_menu_items).lower()
    else:
        print("\n\n", "-"*46, menu_title, "\n", "-"*46, sep="")
        menu_selection = input(menu_items).lower()


    if menu_selection == 'r':
        # Add a new user to the user.txt file
        reg_user(read_user_file())

    elif menu_selection == 'a':
        # Add a new task tasks.txt file and increases tasks_generated by 1
        tasks_generated += add_task(read_user_file())

    elif menu_selection == 'va':
        # Reads all task from task.txt file and prints to the console
        view_all()

    elif menu_selection == 'vm':
        # Reads and outputs all the task from task.txt assigned to the current user
        task_selection = view_mine(curr_user)

        if task_selection == -1:
            pass
        else:
            # Runs the task update menu once the user selects a task number
            update_task(task_selection, read_user_file())

    elif menu_selection == "gr":
        #  Generates report files
        gen_report(t_gen=tasks_generated, all_users=read_user_file())


    elif menu_selection == 'ds' and curr_user == 'admin':
        # If the user is an admin, they can view statistics about the number of users and tasks.
        username_dict = read_user_file()
        num_users = len(username_dict.keys())
        num_tasks = len(create_task_list("all_users"))


        print("\n\n----- Display Statistics -----")
        print("-----------------------------------")
        print(f"Number of users: \t\t {num_users}")
        print(f"Number of tasks: \t\t {num_tasks}")
        print("-----------------------------------")

    elif menu_selection == 'e':
        print("\n\n", "-"*34, goodbye, "\n", "-"*34)
        exit()

    else:
        print("\nYou have made a wrong choice, Please Try again")
