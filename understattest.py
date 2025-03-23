import requests
from bs4 import BeautifulSoup


url = "https://understat.com/league/Serie_A"
page_tree = requests.get(url)
page_tree.content

# print(page_tree.content)

url = "https://understat.com/league/Serie_A"
page_tree = requests.get(url)

# Parse the page content with BeautifulSoup
soup_page = BeautifulSoup(page_tree.content, "lxml")
scripts = soup_page.find_all("script")

# Print out the contents of each script tag to inspect them
for i, script in enumerate(scripts):
    print(f"Script {i}:")
    if script.string:  # Check if the script tag has content
        print(script.string[:100])  # Print the first 100 characters to avoid too much output
    else:
        print("No content in this script tag")
    print("\n---\n")


third_script = scripts[2]  # This is the third script tag found in the last block
if third_script.string:
    s_string = third_script.string
    print(s_string[:100])  # Print the entire string to inspect its content
else:
    print("No content in this script tag")

for year in range(2014, 2026):
        print(year)