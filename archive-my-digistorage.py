import os
import requests
from argparse import ArgumentParser

api_base = 'https://storage.rcs-rds.ro'
download_folder = 'downloads/digistorage/'


def archive_path(mount, path):
    target_path = download_folder + mount['name'] + '-' + mount['type']
    mount_files = s.get(api_base + '/api/v2/mounts/' + mount['id'] + '/files/list', params={'path': path}).json()[
        'files']
    for mount_file in mount_files:
        if mount_file['type'] == 'dir':
            local_dir = target_path + path + '/' + mount_file['name']
            print("Creating folder: " + local_dir)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            archive_path(mount, path + '/' + mount_file['name'])
        else:
            local_file = target_path + path + '/' + mount_file['name']
            print("Downloading file: " + local_file)
            r = s.get(api_base + '/content/api/v2/mounts/' + mount['id'] + '/files/get',
                      params={'path': path + '/' + mount_file['name']}, stream=True)
            with open(local_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()


def main():
    global download_folder
    global s
    parser = ArgumentParser(description="Archive my DigiStorage")
    parser.add_argument("email", metavar="EMAIL_ADDRESS", type=str, help="Email address used for DigiStorage login")
    parser.add_argument("password", metavar="PASSWORD", type=str, help="Password for DigiStorage login")
    parser.add_argument("--download-folder", dest="download_folder", metavar="DOWNLOAD_FOLDER", type=str,
                        help="Path of folder where to download DigiStorage files", default="downloads/digistorage/")
    args = parser.parse_args()
    download_folder = args.download_folder

    s = requests.Session()

    # get auth token
    token = s.get(api_base + '/token', headers={
        'X-Koofr-Email': args.email,
        'X-Koofr-Password': args.password
    }).headers['X-Koofr-Token']
    s.headers['Authorization'] = 'Token ' + token

    mounts = s.get(api_base + '/api/v2/mounts').json()['mounts']
    for my_mount in mounts:
        print("Mount type: " + my_mount['type'])
        print("Mount name: " + my_mount['name'])
        print("Mount ID: " + my_mount['id'])
        archive_path(my_mount, '/')


if __name__ == "__main__":
    main()
