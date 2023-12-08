import os
from common.utils import cloneRepo, retrieveAsnDefinitions, sparseCheckout, writeText


def postProcess(root, version, files):
    for filename in files:
        path = f'{root}/{version}/{filename}'
        if not os.path.isfile(path):
            continue
        with open(path, encoding='utf-8', errors='ignore') as file:
            content = file.read()
            content = content.replace('--}', '--\n}')
            writeText(f'{root}/{version}/{filename}', content)


def script_main(repo, definitions, repoDir, outputDir):
    cloneRepo(repo, repoDir)
    sparseCheckout(definitions, repoDir)
    for definition in definitions:
        retrieveAsnDefinitions(definition, repoDir, outputDir)
    for ver in os.listdir(outputDir):
        basenames = map(lambda n: os.path.basename(n), definitions)
        postProcess(outputDir, ver, basenames)


if __name__ == '__main__':
    repo = 'https://github.com/wireshark/wireshark'
    asn1dir = 'epan/dissectors/asn1/ngap'
    repoDir = 'wireshark'
    outputDir = 'definitions/ngap'
    definitions = [f'{asn1dir}/NGAP-CommonDataTypes.asn',
                   f'{asn1dir}/NGAP-Constants.asn',
                   f'{asn1dir}/NGAP-Containers.asn',
                   f'{asn1dir}/NGAP-IEs.asn',
                   f'{asn1dir}/NGAP-PDU-Contents.asn',
                   f'{asn1dir}/NGAP-PDU-Descriptions.asn']

    script_main(repo, definitions, repoDir, outputDir)
