import requests
import time
from tabulate import tabulate
from colorama import Fore, Style

# Function to read all authorization tokens from query.txt
def get_authorization_tokens():
    with open('query.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Function to set headers with the provided token
def get_headers(token):
    return {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "telegramauth": f"tma {token}",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Microsoft Edge\";v=\"127\", \"Chromium\";v=\"127\", \"Microsoft Edge WebView2\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Referer": "https://birdx.birds.dog/home",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

def fetch_tasks(headers):
    url = "https://birdx-api.birds.dog/project"
    response = requests.get(url, headers=headers)
    
    # Print full response content for debugging
    print(Fore.YELLOW + "API Response:", response.json())  # Print entire response JSON
    if response.status_code == 200:
        projects = response.json()
        if isinstance(projects, list):
            all_tasks = []
            for project in projects:
                tasks = project.get('tasks', [])
                if isinstance(tasks, list):
                    all_tasks.extend(tasks)  # Add tasks from this project to the all_tasks list
            return all_tasks  # Return the combined list of tasks
        else:
            print(Fore.RED + "Unexpected format: Response is not a list.")
            return []
    else:
        response.raise_for_status()

def clear_task(task_id, channel_id, slug, point, headers):
    # Update the URL to the correct endpoint
    url = "https://birdx-api.birds.dog/project/join-task"
    
    # Prepare the payload according to the provided sample
    payload = {
        "taskId": task_id,
        "channelId": channel_id,
        "slug": slug,
        "point": point
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get('msg') == "Successfully":
            print(Fore.GREEN + f"Task {task_id} successfully marked as completed.")
        else:
            print(Fore.YELLOW + f"Task {task_id} might already be completed or there is another message: {response_data}")
    else:
        # Display error if task completion fails
        print(Fore.RED + f"Failed to mark task {task_id} as completed.")
        print(Fore.RED + f"Please Running task Manually")
        response.raise_for_status()




def print_welcome_message():
    print(Fore.GREEN + Style.BRIGHT + "CATS BOT")
    print(Fore.RED + Style.BRIGHT + "NOT FOR SALE ! Ngotak dikit bang. Ngoding susah2 kau tinggal rename :)\n\n")        

def check_task_completion(task_id, headers):
    url = "https://birdx-api.birds.dog/user-join-task/"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Check if task_id is present in the response data
        for task in data:
            if task.get('taskId') == task_id:
                print(Fore.YELLOW + f"Task {task_id} already completed.")
                return True
        # If task_id is not found
        return False
    else:
        print(Fore.RED + f"Failed to fetch task completion status.")
        print(Fore.RED + f"Status Code: {response.status_code}")
        response.raise_for_status()


def complete_all_tasks():
    tokens = get_authorization_tokens()
    
    confirmation = input(Fore.WHITE + f"Apakah Anda ingin menyelesaikan semua task? (y/n): ").strip().lower()
    if confirmation != 'y':
        return
    
    for token in tokens:
        headers = get_headers(token)
        tasks = fetch_tasks(headers)  # Fetch the tasks directly
        
        if isinstance(tasks, list):  # Ensure tasks is a list
            for task in tasks:
                if task.get('is_enable'):
                    task_id = task['_id']
                    if not check_task_completion(task_id, headers):  # Check if the task is already completed
                        try:
                            clear_task(
                            task['_id'],                # taskId
                            task.get('channelId', ''),  # channelId
                            task.get('slug', 'none'),   # slug
                            task.get('point', 0),       # point
                            headers
                            )
                        except requests.RequestException:
                            # Handle any request exception and move on to the next task
                            print(Fore.WHITE + f"Skipping task {task_id} due to an error.")
        else:
            print(Fore.RED + "No valid tasks found or tasks data format is incorrect.")



def user():
    tokens = get_authorization_tokens()
    if not tokens:
        print(Fore.RED + "No tokens found!")
        return
    
    all_user_data = []
    total_rewards_sum = 0
    
    for token in tokens:
        headers = get_headers(token)
        url = "https://birdx-api.birds.dog/user"
        response = requests.get(url, headers=headers)
        
        # Print token and response status for debugging
        print(f"Token: {token[:10]}...")  # Print first 10 characters of the token
        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            first_name = data.get('telegramUserName')
            last_name = data.get('telegramId')
            telegram_age = data.get('telegramAge')
            total_rewards = data.get('telegramAgePoint')
            
            all_user_data.append([first_name, last_name, telegram_age, total_rewards])
            total_rewards_sum += total_rewards
        else:
            print(Fore.RED + f"Failed to fetch user data for token {token}.")
            response.raise_for_status()
    
    # Display data
    table_data = [["First Name", "Id Telegram", "Umur Telegram", "Total Rewards"]]
    table_data.extend(all_user_data)
    print(tabulate(table_data, headers='firstrow', tablefmt='grid'))
    print(Fore.GREEN + f"\nTotal Rewards: " + Fore.WHITE + f"{total_rewards_sum}" + Style.RESET_ALL)

def play_game(headers):
    play_url = "https://birdx-api2.birds.dog/minigame/egg/play"
    
    high_score = 0        # Initialize the high score variable
    total_points = 0      # (Optional) Keep track of total points earned

    # First, make a POST request to play the game and get the initial turn value
    response = requests.get(play_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        turns_left = data.get('turn', 0)
        result_points = data.get('result', 0)
        
        # Update high score if current result is greater
        if result_points > high_score:
            high_score = result_points
        
        total_points += result_points  # Update total points

        # Display the first play result
        print(Fore.GREEN + f"Played the game. Points Earned: {result_points}")
        print(Fore.GREEN + f"Turns Left: {turns_left}")
        
        # Now, loop as many times as the 'turn' value indicates
        while turns_left > 0:
            response = requests.get(play_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                result_points = data.get('result', 0)
                turns_left = data.get('turn', 0)
                
                # Update high score if current result is greater
                if result_points > high_score:
                    high_score = result_points

                total_points += result_points  # Update total points

                print(Fore.GREEN + f"Played the game. Points Earned: {result_points}")
                print(Fore.GREEN + f"Turns Left: {turns_left}")
                
                # If no more turns are left, break the loop
                if turns_left <= 0:
                    print(Fore.YELLOW + "No more turns left.")
                    break
            else:
                print(Fore.RED + f"Failed to play the game. Status Code: {response.status_code}")
                print(Fore.RED + f"Response Content: {response.text}")
                break

        # After the game loop, display the high score and total points
        print(Fore.CYAN + f"High Score: {high_score}")
        print(Fore.CYAN + f"Total Points Earned: {total_points}")
    else:
        print(Fore.RED + f"Failed to play the game. Status Code: {response.status_code}")
        print(Fore.RED + f"Response Content: {response.text}")

def confirm_upgrade(headers):
    url = "https://birdx-api2.birds.dog/minigame/incubate/confirm-upgraded"
    
    # Making a POST request to the API
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'confirmed':
            print(Fore.GREEN + "Upgrade confirmed successfully.")
        else:
            print(Fore.YELLOW + f"Upgrade status: {data}")
    else:
        print(Fore.RED + f"Failed to confirm upgrade. Status Code: {response.status_code}")
        print(Fore.RED + f"Response Content: {response.text}")


def system_check(headers):
    system_url = "https://birdx-api.birds.dog/system"
    response = requests.get(system_url, headers=headers)
    
    if response.status_code == 200:
        system_data = response.json()
        countdown = system_data.get('countdown')
        has_news = system_data.get('hasNews')
        
        print(f"System Countdown: {countdown}")
        print(f"Has News Timestamp: {has_news}")
        return system_data
    else:
        print(f"Failed to check system. Status Code: {response.status_code}")
        return None

def upgrade(headers):
    # Fetch the incubation info
    upgrade_url = "https://birdx-api2.birds.dog/minigame/incubate/upgrade"
    upgrade_response = requests.get(upgrade_url, headers=headers)

    if upgrade_response.status_code == 200:
                print("Upgrade initiated successfully.")
    else:
                print(f"Failed to initiate upgrade. Status Code: {upgrade_response.status_code}")
                print(f"Response Content: {upgrade_response.text}")

def main():
    print_welcome_message()
    print(Fore.WHITE + f"\nDisplaying user information...")
    user()
    print(Fore.WHITE + f"\n............................")
    tokens = get_authorization_tokens()
    for token in tokens:
        headers = get_headers(token)
        print(Fore.WHITE + f"\nDisplaying Task information for token {token[:10]}...")
        tasks = fetch_tasks(headers)
        if tasks:
            print(Fore.WHITE + "Task data received.")
        else:
            print(Fore.RED + "No tasks available.")
        print(Fore.WHITE + f"\nAuto Upgrade information for token query_id={token[:10]}...")
        system_check(headers)
        upgrade(headers)  # Pass 'headers' to upgrade()
        print(Fore.WHITE + f"\nRun auto complete task information...")
        complete_all_tasks()
        print(Fore.WHITE + f"\nRun auto Playing Game...")
        play_game(headers)

if __name__ == "__main__":
    main()