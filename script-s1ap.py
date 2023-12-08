from common.utils import cloneRepo, retrieveAsnDefinitions, sparseCheckout, writeText


def script_main(repo, definitions, repoDir, outputDir):
    cloneRepo(repo, repoDir)
    sparseCheckout(definitions, repoDir)
    for definition in definitions:
        retrieveAsnDefinitions(definition, repoDir, outputDir)


if __name__ == '__main__':
    repo = 'https://github.com/wireshark/wireshark'
    asn1dir = 'epan/dissectors/asn1/s1ap'
    repoDir = 'wireshark'
    outputDir = 'definitions/s1ap'
    definitions = [f'{asn1dir}/S1AP-CommonDataTypes.asn',
                   f'{asn1dir}/S1AP-Constants.asn',
                   f'{asn1dir}/S1AP-Containers.asn',
                   f'{asn1dir}/S1AP-IEs.asn',
                   f'{asn1dir}/S1AP-PDU-Contents.asn',
                   f'{asn1dir}/S1AP-PDU-Descriptions.asn']

    script_main(repo, definitions, repoDir, outputDir)
