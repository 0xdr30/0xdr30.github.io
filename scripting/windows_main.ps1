Set-ExecutionPolicy remotesigned
Install-Module PSWindowsUpdate -force
Get-WindowsUpdate
Install-WindowsUpdate -force
