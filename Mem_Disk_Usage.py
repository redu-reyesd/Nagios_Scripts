#!/usr/bin/python
import commands
import sys
import getopt
#strCommunity,strHostname,serviceOID
def returnservice_snmpQuery(strCommunity, strHostname,serviceName):
      return ("snmpwalk -v2c -c " + strCommunity + " " + strHostname + " " + serviceName + "  -t 40  | sed 's/ STRING://g'  | sed 's/\''(''//g' |sed 's/\'')''//g' | awk -F '=' '{print $2}' ",
          "snmpwalk -v2c -c " + strCommunity + " " + strHostname + " " + serviceName.replace("hrStorageDescr","hrStorageSize") + " -t 40  | sed 's/ STRING://g' | awk -F '=' '{print $2}' ",
          "snmpwalk -v2c -c " + strCommunity + " " + strHostname + " " + serviceName.replace("hrStorageDescr","hrStorageUsed") + "  -t 40  | sed 's/ STRING://g' | awk -F '=' '{print $2}' ",   )

def return_resouce(serviceName1):

    if serviceName1 == "Disk" or serviceName1 == "disk":
        return "C:"
    if serviceName1 == "Memory" or serviceName1 == "mem" or serviceName1 =="ram":
        return "Physical Memory"


def identify_Service(Community,host,resource_to_Monitor):
    service_oid="snmpwalk -v2c -c  " + Community + " " + str(host) + " HOST-RESOURCES-MIB::hrStorageDescr  -t 40 | grep " + resource_to_Monitor + " | awk -F '=' '{print $1}' "
    service_oid=commands.getstatusoutput(service_oid)
    return service_oid[1]

def output( size,usage):
    return " | 'Disk C:'=" + str(usage)+';'+  str(((size*80)/100)) + ';' + str(((size*90)/100)) + ';1;' + str(size) +';;'


def winservice(argv):
    strHostname=""
    strCommunity=""
    services=""
    arg_help = "{0}  <Host ip address>  <Comunity >  <service to monitor>".format(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], ["help", "Host", "Comunity", "Service"])

    except:
        print(arg_help)
        sys.exit(2)

    strHostname,strCommunity,serviceName = args
    serviceOID = identify_Service(strCommunity,strHostname,return_resouce(serviceName))
    SNMP_Desc,SNMP_Size,SNMP_Current_use=returnservice_snmpQuery( strCommunity,strHostname,serviceOID)
    SNMP_Desc=commands.getstatusoutput(SNMP_Desc)
    SNMP_Size=commands.getstatusoutput(SNMP_Size)
    SNMP_Current_use=commands.getstatusoutput(SNMP_Current_use)


    if serviceName == 'Disk' :
       try:

            Disk_use=int(SNMP_Current_use[1].replace("INTEGER: ", ""))
            Disk_Size=int(SNMP_Size[1].replace("INTEGER: ", ""))


            if (Disk_use/1024) < (((Disk_Size*80)/100)/1024) :
                print( "Disk Use ok < 80% : " + str(Disk_use/1024) + " " + str(SNMP_Desc[1].replace('\ Label:', " Label: OS ")) + output(Disk_Size,Disk_use))
                return(0)

            elif Disk_use/1024 >= ((Disk_Size*80)/100)/1024 and Disk_use/1024 < ((Disk_Size*90)/100)/1024 :
                print( "Disk Use Warning > 80% : " + str(Disk_use/1024) + " " + SNMP_Desc[1].replace("\ Label:", " Label: OS ") + + output(Disk_use,Disk_Size))
                return(1)

            elif Disk_use/1024 > ((Disk_Size*90)/100)/1024  :
                print( "Disk Use Critical > 90% : " + str(Disk_use/1024) + " " + SNMP_Desc[1].replace("\ Label:", " Label: OS ") + + output(Disk_use,Disk_Size))
                return(2)
       except:
            print("Disk Usage Unknow")
            return(3)

#    else:  










if __name__== "__main__" :

        winservice(sys.argv)
