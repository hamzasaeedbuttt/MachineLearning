Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\Stock Recommendations.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)

' Get the script directory
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

oLink.TargetPath = scriptDir & "\LAUNCH.bat"
oLink.WorkingDirectory = scriptDir
oLink.Description = "Launch Stock Investment Recommendations"
oLink.IconLocation = "shell32.dll,137"  ' Folder icon, change if you have a custom icon
oLink.Save

WScript.Echo "Desktop shortcut created successfully!"
WScript.Echo "You can now launch the program by double-clicking the shortcut on your desktop."

