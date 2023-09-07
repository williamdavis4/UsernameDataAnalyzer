import requests
import re

# Function to parse usernames and create modified usernames in 'output.txt'
def parse_usernames():
    with open("usernames.txt", "r") as f:
        usernames = f.read().splitlines()

    # Remove duplicates
    usernames = list(set(usernames))

    # Create new list of modified usernames
    modified_usernames = []
    for username in usernames:
        if " " in username:
            # Replace space with underscore
            modified_usernames.append(username.replace(" ", "_"))
        elif "_" in username:
            # Replace underscore with space
            modified_usernames.append(username.replace("_", " "))
        else:
            # Add original username to the list only once
            modified_usernames.append(username)

    # Write modified usernames to 'output.txt'
    with open("output.txt", "w") as f:
        f.write("\n".join(modified_usernames))

# Function to run IP lookup
def run_ip_lookup(ip_address):
    api_key = "ADD YOUR API KEY HERE"
    url = f"http://api.ipapi.com/{ip_address}?access_key={api_key}"
    response = requests.get(url)
    data = response.json()

    country_name = data["country_name"]
    city = data["city"]
    region_name = data["region_name"]
    zip_code = data["zip"]

    isp_url = f"http://ip-api.com/json/{ip_address}"
    isp_response = requests.get(isp_url)
    isp_data = isp_response.json()
    isp = isp_data.get("isp", "N/A")

    # Print IP information without the IP address itself
    print("Country:", country_name)
    print("City:", city)
    print("Region:", region_name)
    print("ZIP Code:", zip_code)
    print("ISP:", isp)

# Function to search databases and print results
def search_databases():
    with open('usernames.txt', 'r') as f:
        lines = f.read().splitlines()

    # Add your databases here in the format:
    # "filename.txt": "filename.txt"
    databases = {}

    # Read the blacklist file
    with open('blacklist.txt', 'r') as f:
        blacklist = f.read().splitlines()

    # Create a set to store the usernames that have already been found
    found_usernames = set()

    # Create a dictionary to store the number of times a username has been found
    num_times_found = {}

    # Search for each username in the databases (case-insensitive)
    for username in lines:
        # Ignore usernames with four characters or fewer
        if len(username) <= 4:
            continue
        # Check if the username is in the blacklist
        if username.lower() in blacklist:
            continue
        # Convert the username to bytes and lowercase
        username_bytes = username.lower().encode('utf-8')
        # Keep track of whether IP lookup has been performed for this username
        ip_found = False
        # Search through each database
        for db_name, db_file in databases.items():
            with open(db_file, 'rb') as f:
                db_binary = f.read()
                try:
                    db_text = db_binary.decode('ascii', errors='ignore')  # Use 'ascii' encoding
                except UnicodeDecodeError:
                    continue  # Skip files that can't be decoded
                db_lines = db_text.splitlines()
                # Simplified regular expression to avoid false positives
                if re.search(rf'\b{re.escape(username)}\b', db_text, re.IGNORECASE):
                    if username not in found_usernames:
                        print(f"Username: {username}")
                        for db_line in db_lines:
                            if re.search(rf'\b{re.escape(username)}\b', db_line, re.IGNORECASE):
                                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', db_line)
                                password_match = re.search(rf'\b(?![0-9]+$)(?!{re.escape(username)}$)[A-Za-z0-9]{{5,12}}\b', db_line)
                                if email_match:
                                    email = email_match.group()
                                    print(f"Email Address: {email}")
                                if password_match and password_match.group() != username:
                                    password = password_match.group()
                                else:
                                    password = ""
                                ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', db_line)
                                if ip_match and not ip_found:  # Perform IP lookup only once
                                    ip_address = ip_match.group()
                                    run_ip_lookup(ip_address)  # Call IP lookup without printing IP address
                                    ip_found = True  # Set the flag to indicate IP lookup has been performed
                                    break  # Exit the loop after the IP lookup
                        found_usernames.add(username)
                        if username in num_times_found:
                            num_times_found[username] += 1
                        else:
                            num_times_found[username] = 1

# Main program
if __name__ == "__main__":
    parse_usernames()
    search_databases()
