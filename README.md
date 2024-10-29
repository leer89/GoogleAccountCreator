# GoogleAccountCreator
Selenium project to randomize and create new accounts for testing oAuth.

You'll need Python, Pip properly set up on your System Variables PATH

Pip install Selenium

Start a cmd/powershell window from the folder where you downloaded the project.

Type in "Python accountCreation.py"

The script pulls from the firstNames and lastNames text files to randomly generate a new person to create a Google Account for. 

If the account creation is successful, it will append the credentials to the text file "account_credentials"

If you're having issues, don't run this in headless mode or set the sleep/wait timers for a little longer. 
