from github import Github
from github.GithubException import BadCredentialsException
from datetime import datetime, timedelta

class Git_Link:
    def __init__(self,gitToken,repositoryURL):
        self.gitToken = gitToken
        self.repositoryURL = repositoryURL 
        self.repo = self.getRepo(gitToken,repositoryURL)
    
    def getRepo(self, token, URL):
        try:
            g = Github(token)
            for repo in g.get_user().get_repos():
                if repo.full_name == URL:
                    return repo
        except:
            return None
    
    def checkToken(self,token):
        try:
            g = Github(token)
            user = g.get_user()
            repos = user.get_repos()
            for repo in repos:
                print(repo.name)
            return True
        except BadCredentialsException:
            return False
    

    def checkURL(self, token, URL):
        repo = self.getRepo(token,URL)
        if repo is not None:
            return True
        else:
            return False

    def getRepoList(self, token):
        repos = []
        try:
            g = Github(token)
            for repo in g.get_user().get_repos():
                repos.append(repo.full_name)
            return repos
        except:
            return repos
    
    def getIssueCount(self):
        issues = self.repo.get_issues(state='open')
        count = 0
        for issue in issues:
            count+=1
        return count

    def getCommitFreq(self):
        #Alter for different frequencies
        since = datetime.now() - timedelta(1)
        commits = self.repo.get_commits(since=since)
        commitCount = 0
        for commit in commits:
            commitCount+=1
        return commitCount



def main(): 
    gl = Git_Link("","")

    # validToken = False
    # while not validToken:
    #     print("Please enter a valid token:")
    #     token = input()
    #     if gl.checkToken(token):
    #         validToken = True
    token = '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'

    # validURL = False
    # while not validURL:
    #     print("Please enter a valid URL:")
    #     print(gl.getRepoList(token))
    #     url = input()
    #     if gl.checkURL(token,url):
    #         validURL = True

    url = 'ZekromMarkII/FEH-Discord-Bot'
    
    gitLink = Git_Link(token,url)

    print(gitLink.getIssueCount())
    print(gitLink.getCommitFreq())

main()


    



    

