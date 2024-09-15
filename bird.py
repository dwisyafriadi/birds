import requests
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
    url = "https://birdx-api2.birds.dog/minigame/egg/join"
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Extracting response details
        game_id = data.get('_id')
        telegram_id = data.get('telegramId')
        turns_left = data.get('turn')
        last_play_at = data.get('lastPlayAt')
        results = data.get('results', [])
        total_points = data.get('total')

        # Check if there are any results
        if results:
            last_result = results[-1]  # Get the latest result
            played_at = last_result.get('playedAt')
            points = last_result.get('point')
            result_id = last_result.get('_id')

            # Displaying game information
            print(Fore.GREEN + f"Game ID: {game_id}")
            print(Fore.GREEN + f"Telegram ID: {telegram_id}")
            print(Fore.GREEN + f"Turns Left: {turns_left}")
            print(Fore.GREEN + f"Last Played At: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_play_at / 1000))}")
            print(Fore.GREEN + f"Last Play Time (Server): {played_at}")
            print(Fore.GREEN + f"Points Gained: {points}")
            print(Fore.GREEN + f"Result ID: {result_id}")
            print(Fore.GREEN + f"Total Points: {total_points}")

            # Handling turns
            if turns_left > 1:
                print(Fore.YELLOW + f"Playing the game. {turns_left} turns left.")
                # Implement your logic to play the game if needed
            elif turns_left < 1:
                print(Fore.RED + "No more turns left. Waiting for 1 hour before retrying...")
                time.sleep(3600)  # Sleep for 1 hour
            else:
                print(Fore.RED + "Unexpected situation.")
        else:
            print(Fore.YELLOW + "No game results found yet.")

    else:
        print(Fore.RED + f"Failed to play the game. Status Code: {response.status_code}")
        print(Fore.RED + f"Response Content: {response.text}")



def main():
    print_welcome_message()
    print(Fore.WHITE + f"\nDisplaying user information...")
    user()
    
    tokens = get_authorization_tokens()
    for token in tokens:
        headers = get_headers(token)
        print(Fore.WHITE + f"\nDisplaying Task information for token {token[:10]}...")
        tasks = fetch_tasks(headers)
        if tasks:
            print(Fore.WHITE + "Task data received.")
        else:
            print(Fore.RED + "No tasks available.")

    print(Fore.WHITE + f"\nRun auto complete task information...")
    complete_all_tasks()
    print(Fore.WHITE + f"\nRun auto Playing Game...")
    play_game(headers)

# Example usage
if __name__ == "__main__":
    main()
