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
    
    #Number of Bugs marked as open
    def getOpenBugCount(self):
        if self.repo is None:
            return 0
        bugs = self.repo.get_issues(state='open',labels=[self.repo.get_label('bug')])
        count = 0
        for bug in bugs:
            count+=1
        return count
    
    #Number of Bugs marked as resolved
    def getClosedBugCount(self):
        if self.repo is None:
            return 0
        bugs = self.repo.get_issues(state='closed',labels=[self.repo.get_label('bug')])
        count = 0
        for bug in bugs:
            count+=1
        return count

    #Number of total Bugs over the project lifespan
    def getTotalBugCount(self):
        if self.repo is None:
            return 0
        return self.getOpenBugCount() + self.getClosedBugCount()

    #Number of commits over project lifespan
    def getTotalCommits(self):
        if self.repo is None:
            return 0
        commits = self.repo.get_commits()
        count = 0
        for commit in commits:
            count+=1
        return count
    
    #Ratio of closed Bugs to total Bugs
    def getDefectFixRate(self):
        if self.repo is None:
            return 0
        #potential to divide by 0
        try:
            rate = self.getClosedBugCount()/self.getTotalBugCount()
        except:
            rate = 0
        return rate
    



    

