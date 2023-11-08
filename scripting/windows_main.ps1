function windows_update(){
    Set-ExecutionPolicy remotesigned
    Install-Module PSWindowsUpdate -force
    Get-WindowsUpdate
    Install-WindowsUpdate -force
}

function remove_shares(){

    Remove-Item "C:\script" -Recurse
    New-Item -Path "C:\" -Name "script" -ItemType Directory
    New-Item "C:\script\log.txt"
    New-Item "C:\script\shares.txt"
    $Path = "C:\script\shares.txt"
    $Log = "C:\script\log.txt"
    get-WmiObject -class Win32_Share | Where-Object -Property Name -ne 'C$' | Where-Object -Property Name -ne 'ADMIN$' | Where-Object -Property Name -ne 'IPC$' | Select-Object -Property Name > $Path
    (get-content $Path) -replace "Name","" | Out-File $Path
    (get-content $Path) -replace "----","" | Out-File $Path
    $shares = $Path
    foreach ($share in Get-Content $Path){
        if(-not [string]::IsNullOrWhiteSpace($share)){
            Remove-SmbShare -Name $share -force
            Write-Host ""
            Write-Host "Removed Share '$share'!" | Out-File $Log
        }
    }
}

function update_secpol(){
    $URL="https://whoppenheimer.com/scripting/windows_main.inf"
    $Path="C:\script\windows.inf"
    Invoke-WebRequest -URI $URL -OutFile $Path
    secedit.exe /configure /db %windir%\security\local.sdb /cfg $Path
}

function main(){
    remove_shares
    update_secpol
}

main
