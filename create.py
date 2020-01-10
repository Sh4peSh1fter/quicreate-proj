# Things to check every first run:
# projects folder path - change the constant if needed.


# Imports
import os
import argparse
import subprocess
from selenium import webdriver
import time

# Constants
DESCRIPTION = "Automates the creation of new project for you to work on.\n" \
              "The stages include:\n" \
              "* Creating a folder with the given name in the projects folder.\n" \
              "* Making a new readme file with the given description.\n" \
              "* Git init-ing the project folder.\n" \
              "* Creating a new repository in Github.\n" \
              "* Adding remote to the local project folder.\n" \
              "* Git add, commit and push the local project folder to Github.\n" \
              "* Opening given code editor.\n"
PROJECTS_FOLDER_PATH = r"D:\Projects"
README_FILE_NAME = "README.md"
DEFAULT_DESC = "Cool project."
DEFAULT_COMMIT = "Initial commit"
DEFAULT_USERNAME = ""  # You can enter your username here
DEFAULT_PASS = ""  # And the password here
GITHUB_URL = 'http://github.com/login'
CHROMEDRIVER_PATH = r"D:\Projects\auto_create\chromedriver.exe"
SLEEP_TIME = 3

# Globals
git_command_list = ["git init", "git add .", "git commit -m", "git remote add origin", "git push -u origin master",
                    "git status"]


def setup():
    if not os.path.exists(PROJECTS_FOLDER_PATH):
        print("Default Projects folder \"{}\" doesn't exist.".format(PROJECTS_FOLDER_PATH))
        exit()


def conn_github(username, password, proj_name, proj_desc, proj_commit, proj_full_path, pv):
    browser = webdriver.Chrome(CHROMEDRIVER_PATH)
    browser.get(GITHUB_URL)
    input_field = browser.find_element_by_xpath("//*[@id=\"login_field\"]")
    input_field.send_keys(username)
    input_field = browser.find_element_by_xpath("//*[@id=\"password\"]")
    input_field.send_keys(password)
    button = browser.find_element_by_xpath("//*[@id=\"login\"]/form/div[3]/input[8]")
    button.click()

    browser.get('https://github.com/new')
    input_field = browser.find_element_by_xpath("//*[@id=\"repository_name\"]")
    input_field.send_keys(proj_name)
    input_field = browser.find_element_by_xpath("//*[@id=\"repository_description\"]")
    input_field.send_keys(proj_desc)

    if pv:
        pv_button = browser.find_element_by_xpath("//*[@id=\"repository_visibility_private\"]")
        pv_button.click()

    time.sleep(SLEEP_TIME)
    button = browser.find_element_by_xpath("//*[@id=\"new_repository\"]/div[3]/button")
    button.click()

    git_remote = browser.find_element_by_xpath("// *[ @ id = \"empty-setup-new-repo-echo\"] / span[5] / span").text
    git_remote = git_remote.split("//")
    git_remote = git_remote[0] + "//{}:{}@".format(username.replace("@", "%40"), password) + git_remote[1]
    print("git_remote: " + git_remote)

    for command in git_command_list:
        command = command.split(" ")

        if "remote" in command:
            command.append(git_remote)
        elif "commit" in command:
            command.append("\"{}\"".format(proj_commit))
        print("command: " + " ".join(command))

        output = subprocess.Popen(command, shell=True, cwd=proj_full_path, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE).communicate()
        print("goodies: {}\n"
              "errors: {}".format(output[0], output[1]))


def main():
    global git_command_list

    setup()

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('proj_name', metavar='PROJ_NAME', type=str, help='The name of the project')
    parser.add_argument('-d', '--proj_description', type=str, default=DEFAULT_DESC, dest='proj_desc',
                        help='The description of the project')
    parser.add_argument('-m', '--commit_msg', type=str, default=DEFAULT_COMMIT, dest='commit_msg',
                        help='The commit message in git')
    parser.add_argument('-u', '--username', type=str, default=DEFAULT_USERNAME, dest='username',
                        help='The Github username')
    parser.add_argument('-p', '--password', type=str, default=DEFAULT_PASS, dest='password',
                        help='The Github password')
    parser.add_argument('-pv', '--private', action='store_true',
                        help='If used, the created repository will be private.')

    args = parser.parse_args()
    proj_full_path = r'{}\{}'.format(PROJECTS_FOLDER_PATH, args.proj_name.lower())

    if not os.path.exists(proj_full_path):
        os.makedirs(proj_full_path)
        os.chdir(proj_full_path)
        with open(README_FILE_NAME, "w+") as readme:
            readme.write("# {}\n"
                         "## Description\n"
                         "{}".format(args.proj_name.replace("_", " ").title(), args.proj_desc))

        conn_github(args.username, args.password, args.proj_name, args.proj_desc, args.commit_msg, proj_full_path,
                    args.private)
    else:
        print("A folder with this name already exists.")
        exit()


if __name__ == '__main__':
    main()
