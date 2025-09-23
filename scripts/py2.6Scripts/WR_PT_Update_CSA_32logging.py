# debugging script

import sys, string, os, arcpy, calendar, datetime, traceback, arcgisscripting, shutil, glob
from arcpy import env

try:

    d = datetime.datetime.now()
    log = open("E:\\Updates\\ArcUpdateScriptsLogs\WR_PT_Update_CSA_32logging.txt","a")
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

    # Import system modules
    import fileinput, glob, string, sys, os, time, shutil, arcgisscripting
    from os.path import join


    # Import ZWRDailyUpdates toolbox
    arcpy.AddToolbox(r'\\owrbgis\geodat\GIS\ArcGIS\Toolboxes\ZWRDailyUpdates.tbx')
   
    #Run tools in the ZWRDailyUpdates toolbox
    arcpy.aWRPTPrepareNewRecords_ZWRDU()
    print "Ran aWRPTPrepareNewRecords successfully."
    arcpy.bWRPTCopyNewRecords_ZWRDU()
    print "Ran bWRPTCopyNewRecords successfully."
    arcpy.cUploadDashboardDate_ZWRDU()
    print "Ran cUploadDashboardDate successfully."


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
