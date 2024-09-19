import requests
import time
from tabulate import tabulate
from colorama import Fore, Style
import sys

# Function to read all authorization tokens from query.txt
def get_authorization_tokens():
    try:
        with open('query.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(Fore.RED + "Error: 'query.txt' file not found.")
        sys.exit(1)

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
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
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
    except requests.RequestException as e:
        print(Fore.RED + f"Error fetching tasks: {e}")
        return []

def clear_task(task_id, headers):
    url = "https://birdx-api.birds.dog/project/join-task"
    payload = {
        "taskId": task_id,
    }
    
    try:
        response = requests.get(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()
        if response_data.get('msg') == "Successfully":
            print(Fore.GREEN + f"Task {task_id} successfully marked as completed.")
        else:
            print(Fore.YELLOW + f"Task {task_id} might already be completed or there is another message: {response_data}")
    except requests.RequestException as e:
        print(Fore.RED + f"Failed to mark task {task_id} as completed.")
        print(Fore.RED + f"Please run the task manually.")
        print(Fore.RED + f"Error: {e}")

def print_welcome_message():
    print(Fore.GREEN + Style.BRIGHT + "CATS BOT")
    print(Fore.RED + Style.BRIGHT + "NOT FOR SALE! Ngotak dikit bang. Ngoding susah-susah kau tinggal rename :)\n\n")        

def check_task_completion(task_id, headers):
    url = "https://birdx-api.birds.dog/user-join-task/"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Check if task_id is present in the response data
        for task in data:
            if task.get('taskId') == task_id:
                print(Fore.YELLOW + f"Task {task_id} already completed.")
                return True
        # If task_id is not found
        return False
    except requests.RequestException as e:
        print(Fore.RED + f"Failed to fetch task completion status.")
        print(Fore.RED + f"Error: {e}")
        return False

# Persistent variable to store user's confirmation
user_confirmation_saved = None  # Will store True or False

def complete_all_tasks(skip_confirmation=False):
    global user_confirmation_saved  # Use the global variable to track user choice
    tokens = get_authorization_tokens()
    
    if user_confirmation_saved is None and not skip_confirmation:  # Ask for confirmation only if not already saved and not skipping
        confirmation = input(Fore.WHITE + f"Do you want to complete all tasks? (y/n): ").strip().lower()
        if confirmation == 'y':
            user_confirmation_saved = True  # Save the user's choice
        else:
            user_confirmation_saved = False  # User chose not to complete tasks
    
    if user_confirmation_saved:
        for token in tokens:
            headers = get_headers(token)
            tasks = fetch_tasks(headers)  # Fetch the tasks directly
    
            if isinstance(tasks, list):
                for task in tasks:
                    if task.get('is_enable'):
                        task_id = task['_id']
                        if not check_task_completion(task_id, headers):
                            try:
                                clear_task(task_id, headers)
                            except Exception as e:
                                print(Fore.WHITE + f"Skipping task {task_id} due to an error: {e}")
            else:
                print(Fore.RED + "No valid tasks found or tasks data format is incorrect.")
    else:
        print(Fore.YELLOW + "Task completion skipped based on user selection.")

def get_user_info(token):
    headers = get_headers(token)
    url = "https://birdx-api.birds.dog/user"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        first_name = data.get('telegramUserName', 'Unknown')
        last_name = data.get('telegramId', 'Unknown')
        telegram_age = data.get('telegramAge', 'Unknown')
        total_rewards = data.get('telegramAgePoint', 0)
        return first_name, last_name, telegram_age, total_rewards
    except requests.RequestException as e:
        print(Fore.RED + f"Failed to fetch user data for token {token}.")
        print(Fore.RED + f"Error: {e}")
        return 'Unknown', 'Unknown', 'Unknown', 0

def play_game(headers, username):
    play_url = "https://birdx-api2.birds.dog/minigame/egg/play"
    turn_url = "https://birdx-api2.birds.dog/minigame/egg/turn"
    
    high_score = 0        # Initialize the high score variable
    total_points = 0      # Keep track of total points earned

    try:
        # Check the number of turns available
        turn_response = requests.get(turn_url, headers=headers)
        if turn_response.status_code == 200:
            turn_data = turn_response.json()
            turns_left = turn_data.get('turn', 0)
            
            if turns_left > 0:
                print(Fore.GREEN + f"Turns Available: {turns_left}")
                
                # Loop through the available turns
                while turns_left > 0:
                    # Play the game using POST request
                    response = requests.get(play_url, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        result_points = data.get('result', 0)
                        turns_left = data.get('turn', 0)
                        
                        # Update high score and total points
                        if result_points > high_score:
                            high_score = result_points
                        total_points += result_points
                        
                        print(Fore.GREEN + f"Played the game. Points Earned: {result_points}")
                        print(Fore.GREEN + f"Turns Left after play: {turns_left}")
                        
                        # If no more turns are left, break the inner loop to check again
                        if turns_left <= 0:
                            print(Fore.YELLOW + "No more turns left.")
                            break
                    else:
                        print(Fore.RED + f"Failed to play the game. Status Code: {response.status_code}")
                        print(Fore.RED + f"Response Content: {response.text}")
                        break  # Exit the inner loop if play fails
            else:
                print(Fore.YELLOW + f"No turns available for user {username}. Skipping to the next user...")
        else:
            print(Fore.RED + f"Failed to get turn information for user {username}. Status Code: {turn_response.status_code}")
            print(Fore.RED + f"Response Content: {turn_response.text}")
    
    except KeyboardInterrupt:
        print(Fore.RED + "\nBot stopped by user.")
        print(Fore.CYAN + f"Final High Score: {high_score}")
        print(Fore.CYAN + f"Total Points Earned: {total_points}")
        sys.exit()


def upgrade(headers, username):
    # Fetch the incubation info
    info_url = "https://birdx-api2.birds.dog/minigame/incubate/info"
    try:
        info_response = requests.get(info_url, headers=headers)
        info_response.raise_for_status()
        upgrade_info = info_response.json()
        
        current_level = upgrade_info.get('level')
        current_birds = upgrade_info.get('birds')
        status = upgrade_info.get('status')
        next_level_info = upgrade_info.get('nextLevel', {})
        
        next_level = next_level_info.get('level', current_level + 1)
        next_level_type = next_level_info.get('type', 'egg')
        next_level_birds = next_level_info.get('birds', 200)
        next_level_worms = next_level_info.get('worms', 80)
        next_level_duration = next_level_info.get('duration', 1)
        
        # Print the current status and upgrade details
        print(Fore.WHITE + f"\nAuto Upgrade information for token query_id={username}...")
        print(Fore.GREEN + f"Current Level: {current_level}")
        print(Fore.GREEN + f"Current Birds: {current_birds}")
        print(Fore.GREEN + f"Next Level: {next_level}")
        print(Fore.GREEN + f"Upgrade Status: {status}")
        
        # Check if the upgrade is still processing
        if status == 'processing':
            print(Fore.YELLOW + "Upgrade already processing, waiting for confirmation...")
            # Optionally, can check the status periodically
        else:
            # Prepare the payload with the next level information
            upgrade_url = "https://birdx-api2.birds.dog/minigame/incubate/upgrade"
            upgrade_payload = {
                "level": current_level,
                "upgradedAt": int(time.time() * 1000),  # Convert to milliseconds
                "status": "processing",
                "duration": next_level_duration,
                "birds": current_birds,
                "nextLevel": {
                    "level": next_level,
                    "type": next_level_type,
                    "birds": next_level_birds,
                    "worms": next_level_worms,
                    "duration": next_level_duration
                }
            }
            print(Fore.GREEN + f"Upgrading to Level {next_level}...")
            try:
                upgrade_response = requests.get(upgrade_url, headers=headers, json=upgrade_payload)
                upgrade_response.raise_for_status()
                print(Fore.GREEN + "Upgrade initiated successfully.")
                # Confirm the upgrade
                confirm_upgrade(headers, username)
            except requests.RequestException as e:
                print(Fore.RED + f"Failed to initiate upgrade. Error: {e}")

    except requests.RequestException as e:
        print(Fore.RED + f"Failed to fetch upgrade info. Error: {e}")

def confirm_upgrade(headers, username):
    confirm_url = "https://birdx-api2.birds.dog/minigame/incubate/confirm-upgraded"
    
    try:
        # Making a POST request to the API
        response = requests.post(confirm_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data is True:
            print(Fore.GREEN + "Upgrade confirmed successfully.")
        else:
            print(Fore.YELLOW + f"Upgrade confirmation returned unexpected result: {data}")
    except requests.RequestException as e:
        print(Fore.RED + f"Failed to confirm upgrade. Error: {e}")

def main():
    print_welcome_message()
    while True:
        try:
            tokens = get_authorization_tokens()
            if not tokens:
                print(Fore.RED + "No tokens found! Exiting...")
                break

            for token in tokens:
                headers = get_headers(token)
                # Fetch user info
                first_name, last_name, telegram_age, total_rewards = get_user_info(token)
                username = first_name if first_name else "Unknown"
                
                try:
                    # Display user info
                    print(Fore.CYAN + f"\nProcessing token for user: {username} (ID: {last_name})")
                    
                    # Perform upgrade
                    upgrade(headers, username)
                    
                    # Complete all tasks
                    print(Fore.WHITE + f"\nRun auto complete task information for user {username}...")
                    complete_all_tasks(skip_confirmation=True)
                    
                    # Play the game
                    print(Fore.WHITE + f"\nRun auto Playing Game for user {username}...")
                    play_game(headers, username)
                
                except Exception as e:
                    print(Fore.RED + f"An error occurred while processing user {username}: {e}")
                    print(Fore.YELLOW + "Skipping to the next user...\n")
            
            # After processing all tokens, sleep for a short duration before restarting
            print(Fore.CYAN + "\nAll tokens processed. Restarting the bot in 5 seconds...\n")
            time.sleep(1800)  # Sleep for 5 seconds before restarting

        except KeyboardInterrupt:
            print(Fore.RED + "\nBot stopped by user.")
            sys.exit()

if __name__ == "__main__":
    main()
