Set-ExecutionPolicy remotesigned
Install-Module PSWindowsUpdate -force
Get-WindowsUpdate
Install-WindowsUpdate -force
New-Item -Path "C:\" -Name "script" -ItemType Directory
$URL="https://whoppenheimer.com/scripting/windows_main.inf"
$Path="C:\script\windows.inf"
Invoke-WebRequest -URL $URL -OutFile $Path
secedit.exe /configure /db %windir%\security\local.sdb /cfg C:\script\windows.inf

$shares = get-WmiObject -class Win32_Share where {($_.name -ne "ADMIN$") -or ($_.name -ne "IPC$") -or ($_.name -ne "C$") -or ($_.name -ne "PRINT$")}
Write-Host $shares