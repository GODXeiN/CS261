from github import Github
from github.GithubException import BadCredentialsException

# Before running, make sure to install pyGithub.
# You'll also need to get your own Token (see link below).
# Feel free to play around with the other repo info as necessary.
# Also, I know this isn't great Python code. It's more of a demo.

# Creating Personal Access Tokens
# https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

# Webhooks for constant connection; POST on Pull-Request (for later)
# https://pygithub.readthedocs.io/en/latest/examples/Webhook.html

def print_topics(repo):
    print("     Topics:" , str(repo.get_topics()))

def print_open_issues(repo):
    num_open = repo.open_issues_count
    print("     Open Issues:", num_open)
    if num_open > 0:
        for issue in repo.get_issues(state='open'):
            print(" >>", issue)

def print_creation(repo):
    print("     Created at:", str(repo.created_at))

def print_last_pushed_at(repo):
    print("     Last pushed:", str(repo.pushed_at))

def print_contributors(repo):
    conts = []
    for contr in repo.get_contributors():
        conts.append(contr.login)
    print("     Contributors:", str(conts))



def print_repo(repo):
    if repo != None:
        print(repo.full_name)
        print_topics(repo)
        print_open_issues(repo)
        print_creation(repo)
        print_last_pushed_at(repo)
        print_contributors(repo)
    else:
        print(str(repo))
        print()


token = input("Input your access token: ")

try:
    g = Github(token)
except:
    print("Error: your token is incorrect or invalid")
    exit(1)

# Repository look-up by full-name
repoDict = {}
# Maps repository name to list of full repository names
nameDict = {}

user = g.get_user()

try:
    for repo in user.get_repos():
        repoDict[repo.full_name] = repo
        # Store a list of repos with the same name
        nameDict[repo.name] = nameDict.get(repo.name, [])
        nameDict[repo.name].append(repo.full_name)
except BadCredentialsException:
    print("Error: could not fetch user's repositories. Please check your token is correct and not expired.")
    exit(1)

print(" >>> Valid GitHub token")
print("\nAvailable Repositories:")
for fn in repoDict.keys():
    print("   ", fn)

chosenRepoName = input("\nInput the repo to display: ")

# If repo identified by full name/uniquely
if chosenRepoName in repoDict.keys():
    print_repo(repoDict[chosenRepoName])
elif chosenRepoName in nameDict.keys():
    # Print all repos with that same name
    for fn in nameDict.get(chosenRepoName):
        print_repo(repoDict[fn])
else:
    print("Invalid repository? Check your spelling or try a different account")