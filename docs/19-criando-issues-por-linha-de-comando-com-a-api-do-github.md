# 19 - Criando Issues por linha de comando com a api do github

<a href="https://youtu.be/XwT2CMrGfiE">
    <img src="../.gitbook/assets/youtube.png">
</a>


## [github cli](https://docs.github.com/en/rest/reference/issues#create-an-issue)

`pip install requests`

```python
import json

import requests
from decouple import config

# Autenticação
REPO_USERNAME = config('REPO_USERNAME')
REPO_PASSWORD = config('REPO_PASSWORD')

# O repositório para adicionar a issue
REPO_OWNER = config('REPO_OWNER')
REPO_NAME = config('REPO_NAME')


def make_github_issue(title, body=None, assignee=None, milestone=None, labels=None):
    '''
    Create an issue on github.com using the given parameters.
    '''
    url = 'https://api.github.com/repos/%s/%s/issues' % (REPO_OWNER, REPO_NAME)
    session = requests.Session()
    session.auth = (REPO_USERNAME, REPO_PASSWORD)
    # Create our issue
    issue = {
        'title': title,
        'body': body,
        'assignee': assignee,
        'milestone': milestone,
        'labels': labels
    }
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        print('Successfully created Issue "%s"' % title)
    else:
        print('Could not create Issue "%s"' % title)
        print('Response:', r.content)


if __name__ == '__main__':
    title = 'Criar github cli'
    body = 'API para criar issues por linha de comando.'
    make_github_issue(
        title=title,
        body=body,
        assignee='rg3915',
        milestone=None,
        labels=['enhancement']
    )
```
