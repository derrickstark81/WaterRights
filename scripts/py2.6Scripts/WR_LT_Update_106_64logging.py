# debugging script

import sys, string, os, arcpy, calendar, datetime, traceback, arcgisscripting, shutil, glob
from arcpy import env

try:

    d = datetime.datetime.now()
    log = open("E:\\Updates\\ArcUpdateScriptsLogs\WR_LT_Update_106_64logging.txt","a")
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


    ###Delete Shapefiles###

    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\Temp\\MasterCovs\\", "Pending_Areas_of_Use*")):
        os.remove(filename)

    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\Temp\\MasterCovs\\", "Pending_Dedicated_Lands*")):
        os.remove(filename)
        
    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\Temp\\MasterCovs\\", "Pending_GW_Wells*")):
        os.remove(filename)

    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\Temp\\MasterCovs\\", "Pending_SW_Diversions*")):
        os.remove(filename)

    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\Temp\\MasterCovs\\", "Permitted_Areas_of_Use*")):
        os.remove(filename)

    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\Temp\\MasterCovs\\", "Permitted_Dedicated_Lands*")):
        os.remove(filename)

    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\Temp\\MasterCovs\\", "Permitted_GW_Wells*")):
        os.remove(filename)

    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\Temp\\MasterCovs\\", "Permitted_SW_Diversions*")):
        os.remove(filename)

    print "Removed shapefiles successfully."

    # Import Z_LT_Water_Rights102 toolbox
    arcpy.AddToolbox(r'\\OWRBGIS\GeoDat\GIS\ArcGIS\Toolboxes\Z_LT_Water_Rights102.tbx')
   # try:
        #Run tools in the Z_LT_Water_Rights102 toolbox
    arcpy.aDeleteLTWRgdb_LTWR102()
    print "Ran aDeleteLTWRgdb successfully."
    arcpy.bCreateLTWRgdb_LTWR102()
    print "Ran bCreateLTWRgdb successfully."
    arcpy.cImportLTWRTables_LTWR102()
    print "Ran cImportLTWRTables successfully."
    arcpy.dImportLTWRFCs_LTWR102()
    print "Ran dImportLTWRFCs successfully."
    arcpy.dzCreateProposedWells_LTWR102()
    print "Ran dzCreateProposedWells successfully."
##    arcpy.dzzCreateAllocationByPurposeTable_LTWR102()
##    print "Ran dzzCreateAllocationByPurposeTable successfully."
    arcpy.eCreateLTWRSummaryTables_LTWR102()
    print "Ran eCreateLTWRSummaryTables successfully."
    arcpy.fCreateLTWRRelationshipClasses_LTWR102()
    print "Ran fCreateLTWRRelationshipClasses successfully."
    arcpy.gUpdateLTWRMetadataDate_LTWR102()
    print "Ran gUpdateLTWRMetadataDate successfully."

        
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
