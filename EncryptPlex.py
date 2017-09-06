#!/usr/bin/python
# Certificate creation:
# original credit to @lokulin
# updated by Will Foster @sadsfae
#
# Extraction and Updating of Preferences XML @stiggle
#
# Use at own risk, etc.

import sys
import hashlib
from OpenSSL.crypto import *
from xml.dom.minidom import parse, parseString, getDOMImplementation


def main():
        if(len(sys.argv) != 6):
                print sys.argv[0] + " /path/to/Plex/Preferences.xml PlexFQDN /path/to/read/ssl.cert /path/to/read/ssl.key /path/to/write/ssl.p12"
                print ""
                print "REMEMBER TO RESTART PLEX WHEN YOU RUN THIS TO READ THE UPDATED PREFERENCES"
                print""
                print "/path/to/Plex/Preferences.xml"
                print "This is the path to your Plex Preferences.xml file (remember to put it in quotes)"
                print "Usually something like: '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server'"
                print ""
                print "PlexFQDN"
                print "This is the fully qualified domain name, as contained in the SSL certificate, that Plex runs on."
                print ""
                print "/path/to/read/ssl.cert"
                print "This is the SSL Certificate file  we read in to make the PKCS12 file"
                print "If using LetsEncrypt, it will be something like: /etc/letsencrypt/live/{hostname}/cert.pem"
                print ""
                print "/path/to/read/ssl.key"
                print "This is the SSL Private Key file we read in to make the PKCS12 file"
                print "If using LetsEncrypt, it will be something like: /etc/letsencrypt/live/{hostname}/privkey.pem"
                print ""
                print "/path/to/read/ssl.p12"
                print "This is the SSL PKCS12 file"
                print "This is where we write the PKCS12 file."
                print "I stick mine with the other LetsEncrypt files: /etc/letsencrypt/live/{hostname}/ssl.p12"
                print ""
                sys.exit(0)
        else:
# Read in the commandline options
# Plex Preferences File
                PlexPrefPath = sys.argv[1]
# Plex Server Host Name
                PlexFQDN = sys.argv[2]
# Read in the Certificate file
                with open(sys.argv[3], 'rb') as f:
                        PlexSSLCert = f.read()
# Read in the Private Key file
                with open(sys.argv[4], 'rb') as f:
                        PlexSSLKey = f.read()
# PKCS12 File (as used by Plex)
                PlexPFXCert = sys.argv[5]

# Read in the Plex Preferences XML file
                PlexPrefXML = parse(PlexPrefPath)

# Select the Preferences XML object
# One we keep
                PlexPrefOrig = PlexPrefXML.getElementsByTagName("Preferences")[0]
# One we change
                PlexPrefVal = PlexPrefXML.getElementsByTagName("Preferences")[0]

# Select the PMI
                PlexPMI = PlexPrefVal.getAttribute("ProcessedMachineIdentifier")

                hash = hashlib.sha512()
                hash.update('plex')
                hash.update(PlexPMI)
                PlexKey = hash.hexdigest()

# Create the PKCS12 file from the certificate and private key
                key = load_privatekey(FILETYPE_PEM, PlexSSLKey)
                cert = load_certificate(FILETYPE_PEM, PlexSSLCert)
                p12 = PKCS12()
                p12.set_certificate(cert)
                p12.set_privatekey(key)
# Export the key with the PMI based password
                open(PlexPFXCert, "w").write( p12.export(PlexKey) )

# Update the Preferences with the new certificate values
                PlexPrefVal.setAttribute( "customCertificateDomain", PlexFQDN )
                PlexPrefVal.setAttribute( "customCertificateKey", PlexKey )
                PlexPrefVal.setAttribute( "customCertificatePath", PlexPFXCert )

# Replace the <Preferences> node in the XML
                PlexPrefXML.replaceChild(PlexPrefOrig, PlexPrefVal)

# Open the Preferences.xml file for updating
                PlexPref = open(PlexPrefPath, "w")

# Update the XML file
                PlexPrefXML.writexml(PlexPref)

if __name__ == '__main__':
        main()
