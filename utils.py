"""
Utility functions.
"""
import json
import os
import re
import subprocess
import stat
import urllib.request
import zipfile


def create_dir(abs_path):
    """
    Creates a directory
    """
    if not os.path.isdir(abs_path):
        subprocess.call(["mkdir", "-p", abs_path])


def make_executable(abs_path):
    """
    Add the exec permission to a file
    """
    os.chmod(abs_path, os.stat(abs_path).st_mode | stat.S_IEXEC)


def get_main_file(possible_filenames, install_path):
    """
    Tries to detect the main file of a plugin directory
    """
    content = os.listdir(install_path)
    if len(content) == 1:
        # FIXME: shitty var name..
        tmp_file = os.path.join(install_path, content[0])
        if not os.path.isdir(tmp_file):
            # There is only one file, this is the main one !
            return tmp_file
        else:
            # The archive actually contained a directory, let's clean it up
            for f in os.listdir(tmp_file):
                os.rename(os.path.join(tmp_file, f),
                          os.path.join(install_path, f))
            os.rmdir(tmp_file)
            content = os.listdir(install_path)
    # Iterate through all files to check if one could be the main one
    for filename in [f for f in content
                     if os.path.isfile(os.path.join(install_path, f))]:
        # FIXME: Should really do this with regex..
        for possible_filename in possible_filenames:
            if possible_filename in filename:
                return os.path.join(install_path, filename)
    return None


def dl_github_repo(install_path, url):
    """
    Downloads a whole Github repo, then delete the '.git'.

    :param install_path: Where to clone the repo.
    :param url: Repo url.
    """
    # Let's download it as a zip
    dl_url = url + "archive/master.zip" if url[:-1] == '/' \
             else url + '/' + "archive/master.zip"
    zip_path, _ = urllib.request.urlretrieve(dl_url,
                               os.path.join(install_path, url.split("/")[-1]))
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        zip_file.extractall(install_path)
    os.remove(zip_path)


def dl_folder_from_github(install_path, url):
    """
    Recursively fetches files from a github repo's folder.

    :param install_path: Where to store the folder.
    :param url: From where to fetch the folder (Github API url).
    """
    if not re.search(r"[api.github.com/repos/]+[/contents/]+", url):
        raise ValueError("Unsupported url")
    json_content = json.load(urllib.request.urlopen(url))
    if not isinstance(json_content, list):
        if "submodule_git_url" in json_content:
            dl_github_repo(install_path, json_content["submodule_git_url"])
            return
        else:
            raise ValueError("Could not parse json: {}".format(json_content))
    for i in json_content:
        if "download_url" in i:
            if i["download_url"]:
                dest = os.path.join(install_path, i["name"])
                urllib.request.urlretrieve(i["download_url"], dest)
            # This is a folder
            else:
                new_install_path = os.path.join(install_path, i["name"])
                create_dir(new_install_path)
                dl_folder_from_github(new_install_path,
                                      url + i["name"] if url[:-1] == '/' else
                                      url + '/' + i["name"])
        # Unlikely
        if "submodule_git_url" in i:
            dl_github_repo(os.path.join(install_path, i["name"]),
                           json_content["submodule_git_url"])
