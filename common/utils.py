import os
import re
import subprocess

def writeText(filepath, text):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def versiontuple(v):
    return tuple(map(int, (v.split('.'))))


def cloneRepo(repo, repoDir):
    alreadyCloned = os.path.exists(f'{repoDir}/.git')
    if not alreadyCloned:
        print('Cloning repo...')
        # clone no checkout, no blob
        os.system(f'git clone --quiet -n --filter=blob:none {repo} {repoDir}')
    else:
        print('Repo already cloned, not cloning again.')
        print('Fetching...')
        os.system(f'git -C {repoDir} fetch --quiet')
        os.system(f'git -C {repoDir} pull --quiet')


def sparseCheckout(files, repoDir):
    # disable git gc to speedup processing
    os.system(f'git -C {repoDir} config gc.auto 0')

    # files to string
    filesString = ' '.join('/' + file for file in files)
    # configure sparse-checkout
    print('Pulling asn files...')
    subprocess.run(f'git -C {repoDir} sparse-checkout set --no-cone {filesString}',
                   encoding='utf-8', errors='ignore', capture_output=True, text=True, shell=True)
    # checkout
    subprocess.run(f'git -C {repoDir} checkout',
                   encoding='utf-8', errors='ignore', capture_output=True, text=True, shell=True)


def retrieveAsnDefinitions(file, repoDir, outputDir):
    basename = os.path.basename(file)
    print(f'Retrieving {basename} versions...')
    revs = subprocess.run(
        f'git -C {repoDir} rev-list --all {file}', encoding='utf-8', errors='ignore', capture_output=True, text=True, shell=True)
    revList = revs.stdout.splitlines()
    revList.reverse()
    for rev in revList:
        output = subprocess.run(
            f'git -C {repoDir} cat-file blob {rev}:{file}', encoding='utf-8', errors='ignore', capture_output=True, text=True, shell=True)
        stdout = output.stdout
        versionMatch = re.search(r'V([\d\.]+) ', stdout)
        if versionMatch:
            version = versionMatch.group(1)
            # ignore patch
            version = '.'.join(version.split('.')[0:-1])
            writeText(f'{outputDir}/{version}/{basename}', stdout)
    print('Completed')