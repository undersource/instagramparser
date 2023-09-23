# InstaParser

Instagram parser with MySQL

# Setup
```
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```



# Usage
```
-h              display help
-a ACCOUNT      parsed account
-l LOGIN        login of your account
-p PASSWORD     password of your account
-d DIR          output dir
-c COUNT        count of posts
-C CONFIG       path to config
-L LOG          path to log
```

Example
`python main.py -a <account> -l <login> -p <password> -d <account_dir> -c 5`