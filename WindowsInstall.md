How to INSTALL the Pledge Drive Tracker on the Windows operating system.

1) Install python 2.5.4:

http://www.python.org/download/releases/2.5.4/

2) Install mercurial client:

http://tortoisehg.bitbucket.org/

3) Download web2py source into the directory where you develop your apps:

http://www.web2py.com/examples/static/web2py_src.zip

4) CD into web2py directory. Ex: cd C:\Users\johntynan\webdev\web2py\_src\web2py

5) Rename web2py's applications directory to applications\_default.

6) Download the pledgedrivetracker repository using hg. Ex:

cmd

cd C:\Users\johntynan\webdev\web2py\_src\web2py

C:\Users\johntynan\webdev\web2py\_src\web2py>hg clone https://pledgedrivetracker.googlecode.com/hg/ applications

7) copy admin and welcome app directories from the applications\_default directory into your newly created applications directory.

8) run:

c:\python25\python.exe web2py.py

9) Create/enter your own administrative password

10) in your browser, go to:

http://localhost:8000/pledgedrives/

11) to look under the hood, go to:

http://localhost:8000/admin/default/design/pledgedrives

12) Login using the administrative password you created in step 9