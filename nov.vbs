Set WshShell = CreateObject("WScript.Shell")

scriptDirectory = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
relativePath = "nov.bat"

absolutePath = scriptDirectory & relativePath

WshShell.Run Chr(34) & absolutePath & Chr(34), 0, False