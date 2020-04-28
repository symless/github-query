import sys, getopt
from github import Github

organizationName = "Symless"
errorCode = 1

def usage():
  print "ghq.py\n\
  -i get issues\n\
  -p <project> -p <project>\n\
  -m <milestone>\n\
  -h html mode\n\
  -l add links"

def main(argv):
  try:
    opts, args = getopt.getopt(argv, "ip:m:hl")
  except:
    print "Those args don't look right"
    usage()
    return errorCode

  runGetIssues = False
  projects = []
  milestone = ""
  htmlMode = False
  addLinks = False

  for opt, arg in opts:
    if opt == '-i':
      runGetIssues = True
    elif opt == '-p':
      projects.append(arg)
    elif opt == '-m':
      milestone = arg
    elif opt == '-h':
      htmlMode = True
    elif opt == '-l':
      addLinks = True

  if runGetIssues:
    return getIssues(projects, milestone, htmlMode, addLinks)

  print "What do you want from me?"
  usage()
  return errorCode

def getIssues(projectNames, milestoneName, htmlMode, addLinks):
  token = readGitHubToken()

  if len(projectNames) <= 0:
    print "Specify a project name with: -p <project> -p <project>"
    return errorCode

  if not milestoneName:
    print "I need to know the milestone, use: -m <milestone>"
    return errorCode

  g = Github(token)

  organization = g.get_organization(organizationName)

  all = []

  for projectName in projectNames:
    print "Getting issues for " + milestoneName + " in " + projectName

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

    preHeader = ""
    postHeader = ""
    preList = ""
    postList = ""
    preItem = "- "
    postItem = ""

    if htmlMode:
      preHeader = "<p>"
      postHeader = "</p>"
      preList = "<ul>"
      postList = "</ul>"
      preItem = "<li>"
      postItem = "</li>"

    if len(bugs) != 0:
      print "\n" + preHeader + "Bug fixes:" + postHeader
      print preList
      for bug in bugs:
        item = getItem(bug, projectName, preItem, postItem, addLinks)
        all.append(item)
        print item
      print postList

    if len(enhancements) != 0:
      print "\n" + preHeader + "Enhancements:" + postHeader
      print preList
      for enhancement in enhancements:
        item = getItem(enhancement, projectName, preItem, postItem, addLinks)
        all.append(item)
        print item
      print postList

    if len(features) != 0:
      print "\n" + preHeader + "Features:" + postHeader
      print preList
      for feature in features:
        item = getItem(feature, projectName, preItem, postItem, addLinks)
        all.append(item)
        print item
      print postList

  print "\n\n#All issues\n"
  for issue in all:
    print issue

def getItem(bug, projectName, preItem, postItem, addLinks):  
  issueText = "#" + str(bug.number)
  if addLinks:
    issueText = (
      "<a href=\"https://github.com/symless/" + projectName + "/issues/" +
      str(bug.number) + "\" target=\"_blank\">" + issueText + "</a>")
  return preItem + issueText + " " + bug.title + postItem

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
