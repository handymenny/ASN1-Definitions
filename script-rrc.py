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


def postProcess(root, version, fileEutra, fileNr):
    # Add filterCommon to Eutra from NR
    if versiontuple(version) < versiontuple('15.6'):
        return

    filterCommon = ''
    content = ''
    pathNr = f'{root}/{version}/{fileNr}'
    pathLte = f'{root}/{version}/{fileEutra}'

    if not os.path.isfile(pathNr) or not os.path.isfile(pathLte):
        return

    with open(pathNr, encoding='utf-8', errors='ignore') as file:
        content = file.read()

        startString = '-- TAG-UE-CAPABILITYREQUESTFILTERCOMMON-START'
        stopString = '-- TAG-UE-CAPABILITYREQUESTFILTERCOMMON-STOP'
        start = content.index(startString)
        end = content.index(stopString) + len(stopString) + 1
        filterCommon = content[start:end]

        # FreqBandIndicatorNR is FreqBandIndicatorNR-r15 in EUTRA
        filterCommon = filterCommon.replace('FreqBandIndicatorNR', 'FreqBandIndicatorNR-r15')

        if filterCommon.find('maxCellGroupings-r16') != -1:
            filterCommon += '\nmaxCellGroupings-r16                    \
                INTEGER ::= 32      -- Maximum number of cell groupings for NR-DC'

    with open(pathLte, encoding='utf-8', errors='ignore') as file:
        content = file.read()

        endIndex = content.rfind('END') - 1
        # remove END
        content = content[:endIndex]

        # add containing
        searchStr = 'appliedCapabilityFilterCommon-r15		OCTET STRING'
        replaceStr = searchStr + \
            '(CONTAINING UE-CapabilityRequestFilterCommon)'
        content = content.replace(searchStr, replaceStr)

        # add filterCommon and re-add END
        content += filterCommon + '\n\n\nEND\n'

    writeText(f'{root}/{version}/{fileEutra}', content)


def script_main(repo, definitions, repoDir, outputDir):
    cloneRepo(repo, repoDir)
    sparseCheckout(definitions, repoDir)
    for definition in definitions:
        retrieveAsnDefinitions(definition, repoDir, outputDir)
    for ver in os.listdir(outputDir):
        postProcess(outputDir, ver, os.path.basename(
            definitions[0]), os.path.basename(definitions[1]))


if __name__ == '__main__':
    repo = 'https://github.com/wireshark/wireshark'
    asn1dir = 'epan/dissectors/asn1'
    definitions = [f'{asn1dir}/lte-rrc/EUTRA-RRC-Definitions.asn',
                   f'{asn1dir}/nr-rrc/NR-RRC-Definitions.asn',
                   f'{asn1dir}/lte-rrc/EUTRA-InterNodeDefinitions.asn',
                   f'{asn1dir}/nr-rrc/NR-InterNodeDefinitions.asn']
    repoDir = 'wireshark'
    outputDir = 'definitions/rrc'
    script_main(repo, definitions, repoDir, outputDir)
