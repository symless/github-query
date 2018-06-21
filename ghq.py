import sys, getopt
from github import Github

organizationName = "Symless"
errorCode = 1

def usage():
  print "ghq.py\n\
  -i get issues\n\
  -p <project>\n\
  -m <milestone>\n"

def main(argv):
  try:
    opts, args = getopt.getopt(argv, "ip:m:")
  except:
    print "Those args don't look right"
    usage()
    return errorCode

  runGetIssues = False
  project = ""
  milestone = ""

  for opt, arg in opts:
    if opt == '-i':
      runGetIssues = True
    elif opt == '-p':
      project = arg
    elif opt == '-m':
      milestone = arg

  if runGetIssues:
    return getIssues(project, milestone)

  print "What do you want from me?"
  usage()
  return errorCode

def getIssues(projectName, milestoneName):
  token = readGitHubToken()

  if not projectName:
    print "Specify a project name with: -p <project>"
    return errorCode

  if not milestoneName:
    print "I need to know the milestone, use: -m <milestone>"
    return errorCode

  print "Getting issues for " + milestoneName + " in " + projectName

  g = Github(token)
  organization = g.get_organization(organizationName)
  
  try:
    repo = organization.get_repo(projectName)
  except Exception as e:
    print "GitHub didn't like that project name, try one of these:"
    for repo in organization.get_repos():
      print repo.name
    return errorCode

  milestones = repo.get_milestones()
  if not any(True for _ in milestones):
    print "There are no open milestones"
    return errorCode

  milestone = None
  for milestone_ in milestones:
    if milestone_.title == milestoneName:
      milestone = milestone_ 

  if milestone:
    print "Found your milestone: " + milestone.title
  else:
    print "Sorry, couldn't find that milestone, how about these?"
    for milestone_ in milestones:
      print milestone_.title
    print "Note: your milestone has to be open"
    return errorCode

  issues = repo.get_issues(milestone, "all")
  bugs = []
  enhancements = []
  features = []

  print "Organizing issues into neat piles..."
  for issue in issues:
    for label in issue.get_labels():
      if label.name == "bug":
        bugs.append(issue)
      elif label.name == "enhancement":
        enhancements.append(issue)
      elif label.name == "feature":
        features.append(issue)
  
  if len(bugs) != 0:
    print "\nBug fixes:"
    for bug in bugs:
      print "- #" + str(bug.number) + " " + bug.title

  if len(enhancements) != 0:
    print "\nEnhancements:"
    for enhancement in enhancements:
      print "- #" + str(enhancement.number) + " " + enhancement.title

  if len(features) != 0:
    print "\nFeatures:"
    for feature in features:
      print "- #" + str(feature.number) + " " + feature.title

def readGitHubToken():
  filename = "github-token"
  try:
    f = open(filename, "r")
  except:
    print (
      "Please create a file called " + filename + " containing a GitHub token.\n"
      "Tick the first `repo` option (yeah, a bit scary I suppose).\n"
      "Here's some help: http://bit.ly/github-access-token")
    sys.exit(errorCode)

  return f.readline().strip()

if __name__ == "__main__":
  main(sys.argv[1:])
