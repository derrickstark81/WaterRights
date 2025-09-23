# debugging script; needs to run in 32-bit Python because metadata tools are not 64-bit

import sys, string, os, arcpy, calendar, datetime, traceback
from arcpy import env

try:

    d = datetime.datetime.now()
    log = open("E:\\Updates\\ArcUpdateScriptsLogs\WR_LT_Update_106_32logging.txt","a")
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
    
# Import Z_LT_Water_Rights102 toolbox
    arcpy.AddToolbox (r'\\OWRBGIS\GeoDat\GIS\ArcGIS\Toolboxes\Z_LT_Water_Rights102.tbx')
    #try:
        #Run tools in the Z_LT_Water_Rights102 toolbox 
    arcpy.hUpdateLTWRMetadata_LTWR102()
    print "Ran hUpdateLTWRMetadata successfully."
    arcpy.h1UpdateLTWRMetadata_LTWR102()
    print "Ran h1UpdateLTWRMetadata successfully."
    arcpy.iCreateLTWRShps_LTWR102()
    print "Ran iCreateLTWRShps successfully."
    arcpy.jUpdateExportLTWRSHPMetadata_LTWR102()
    print "Ran jUpdateExportLTWRSHPMetadata successfully."
    arcpy.kDeleteLTWRSummaryTables_LTWR102()
    print "Ran kDeleteLTWRSummaryTables successfully."
    arcpy.lExportLTWRSummaryTables_LTWR102()
    print "Ran lExportLTWRSummaryTables successfully."
    arcpy.mDeleteArapahoLTWRGDBCopyNewGDB_LTWR102()
    print "Ran mDeleteArapahoLTWRGDBCopyNewGDB successfully."
    arcpy.nDeleteLTWRMetadataLogfiles_LTWR102()
    print "Ran nDeleteLTWRMetadataLogfiles successfully."

        
    #10 THIS SCRIPT WILL CREATE .ZIP FILES FOR THE WATER RIGHTS LAYERS,
    #DELETE THE OLD FILES FROM THE TEST WEB SERVERS AND COPY THE NEW FILES TO THE TEST WEB SERVER
    #LAST UPDATED: 20121102 MPS
    #CREATED: 20121102 MPS
    #Modified 20140806 by RPS and 20140814 by TS for transfer to Sandstone server

    import fileinput, glob, string, sys, os, time, shutil, arcgisscripting
    os.system(r"C:\7-Zip\7zG.exe a \\OWRBGIS\Geodat\temp\mastercovs\Surface_Water_Rights.zip \\OWRBGIS\Geodat\temp\mastercovs\Permitted_Areas*")
    os.system(r"C:\7-Zip\7zG.exe a \\OWRBGIS\Geodat\temp\mastercovs\Surface_Water_Rights.zip \\OWRBGIS\Geodat\temp\mastercovs\Permitted_SW*")
    os.system(r"C:\7-Zip\7zG.exe a \\OWRBGIS\Geodat\temp\mastercovs\Groundwater_Rights.zip \\OWRBGIS\Geodat\temp\mastercovs\Permitted_Dedicated_Lands*")
    os.system(r"C:\7-Zip\7zG.exe a \\OWRBGIS\Geodat\temp\mastercovs\Groundwater_Rights.zip \\OWRBGIS\Geodat\temp\mastercovs\Permitted_GW*")

    ###Delete old .zip and .htm files ###

    #Surface Water rights
    for filename in glob.glob(os.path.join("\\\\\172.30.73.39\\WebFinal\\maps\\data\\layers\\water_rights\\", "Surface_Water_Rights.zip")): #Previously Surface_Water_Permits.zip
        os.remove(filename)

    for filename in glob.glob(os.path.join("\\\\172.30.73.39\\WebFinal\\maps\\data\\layers\\water_rights\\", "Permitted_SW_Diversions.htm")):
        os.remove(filename)


    #Groundwater Rights
    for filename in glob.glob(os.path.join("\\\\172.30.73.39\\WebFinal\\maps\\data\\layers\\water_rights\\", "Groundwater_Rights.zip")): #Previously Groundwater_Permits.zip
        os.remove(filename)

    for filename in glob.glob(os.path.join("\\\\172.30.73.39\\WebFinal\\maps\\data\\layers\\water_rights\\", "Permitted_GW_Wells.htm")): 
        os.remove(filename)


    ###copy new .zip and .htm files ###
    dst = "\\\\172.30.73.39\\WebFinal\\maps\\data\\layers\\Water_Rights\\"

    #Surface Water rights
    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\temp\\MasterCovs\\", "Surface_Water_Rights.zip")):
        shutil.copy(filename, dst)

    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\temp\\MasterCovs\\", "Permitted_SW_Diversions.htm")):
        shutil.copy(filename, dst)


    #Groundwater Rights
    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\temp\\MasterCovs\\", "Groundwater_Rights.zip")):
        shutil.copy(filename, dst)

    for filename in glob.glob(os.path.join("\\\\OWRBGIS\\Geodat\\temp\\MasterCovs\\", "Permitted_GW_Wells.htm")):
        shutil.copy(filename, dst)

    print "New .zip and .htm files copied."
    print "LT WR update completed."
    
#except arcpy.ExecuteError:
#   print(arcpy.GetMessages(2))

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
    

