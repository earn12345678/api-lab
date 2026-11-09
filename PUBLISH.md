# Submitting this lab

The teacher asks for one **public GitHub repository named `api-lab`** and a link on MyCourses.

## 1. Run the work on your own computer

From the extracted `api-lab` folder in PowerShell:

```powershell
python -m pip install -r requirements.txt
python -m pytest -v --html=report.html --self-contained-html | Tee-Object -FilePath pytest_output.txt
python collect_results.py
```

The first command installs the packages. The second runs the full suite and creates the actual HTML report. The third records the other API responses in `RESULTS.md`. Open both files and check them. If something fails, investigate before submitting.

Expected according to the exercise: **32 passed, 1 xfailed**. Don't write this down as the observed result if your computer shows a different result.

## 2. Create your GitHub repository

Sign in to your own GitHub account (`earn12345678`) and create a new **Public** repository called `api-lab` on https://github.com/new. Leave README, gitignore and license unchecked because they are already in this folder.

Check the Git identity on this computer before making your own commit:

```powershell
git config user.name
git config user.email
```

If these show the wrong person, set **your own** GitHub name and email first (use the address your account is configured to use):

```powershell
git config --global user.name "YOUR_GITHUB_NAME"
git config --global user.email "YOUR_GITHUB_EMAIL"
```

Then publish your completed work:

```powershell
git init
git branch -M main
git add .
git commit -m "Complete Week 11 QuickPizza API lab"
git remote add origin https://github.com/earn12345678/api-lab.git
git push -u origin main
```

If Git says `remote origin already exists`, check `git remote -v` and use `git remote set-url origin https://github.com/earn12345678/api-lab.git` only if it points to the wrong repository.

## 3. Final check

Open https://github.com/earn12345678/api-lab and check that README, RESULTS, report.html and all test files are available. Submit that URL in MyCourses. Do not submit `pytest_output.txt` unless your instructor specifically asks for it.

The local ZIP contains **no fake Git history**. Its owner should review, test and commit it using their own identity.
