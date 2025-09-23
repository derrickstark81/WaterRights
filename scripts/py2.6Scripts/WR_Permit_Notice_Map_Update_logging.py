#!/usr/bin/env python2.7
# debugging script

import sys, string, os, arcpy, calendar, datetime, traceback, arcview
from arcpy import env

try:

    d = datetime.datetime.now()
    log = open("E:\\Updates\\ArcUpdateScriptsLogs\\WR_Permit_Notice_Map_Update_logging.txt","a")
    log.write("----------------------------" + "\n")
    log.write("----------------------------" + "\n")
    log.write("Log: " + str(d) + "\n")
    log.write("\n")    

# Start process...
    starttime = datetime.datetime.now()
    log.write("Begin process:\n")
    log.write("     Process started at " 
               + str(starttime) + "\n")
    log.write("\n")

# Import ZWRPermitProposals toolbox
    arcpy.ImportToolbox ("\\\\OWRBGIS.OWRB.THINKBIG\\Geodat\\GIS\\ArcGIS\\Toolboxes\\ZWRPermitProposals.tbx")
   # try:
        #Run tools in the ZWRPermitProposals toolbox 
    arcpy.aPermitTableUpdate_ZWRPermitProposals()
    print "Ran aPermitTableUpdate successfully."
    arcpy.bNoticePoints_ZWRPermitProposals()
    print "Ran bNoticePoints successfully."
    arcpy.cUploadPointsToTest_ZWRPermitProposals()
    print "Ran cUploadPointsToTest successfully."
    arcpy.dCopyPointsToOWRPAndCSA_ZWRPermitProposals()
    print "Ran dCopyPointsToOWRPAndCSA successfully."
    print "Script ran successfully."
    
   # except arcpy.ExecuteError:
   #     print(arcpy.GetMessages(2))


    endtime = datetime.datetime.now()
    
# Process Completed...
    log.write("     Completed successfully in " 
               + str(endtime - starttime) + "\n")
    log.write("\n")
    log.close()

    
except:
 # Get the traceback object
 tb = sys.exc_info()[2]
 tbinfo = traceback.format_tb(tb)[0]
 # Concatenate information together concerning 
 # the error into a message string
 pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
 msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
# Return python error messages for use in 
# script tool or Python Window
 arcpy.AddError(pymsg)
 arcpy.AddError(msgs)
# Print Python error messages for use in 
# Python / Python Window
 log.write("" + pymsg + "\n")
 log.write("" + msgs + "")
 log.close()
