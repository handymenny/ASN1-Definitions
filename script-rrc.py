import os

from common.utils import cloneRepo, retrieveAsnDefinitions, sparseCheckout, versiontuple, writeText


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
