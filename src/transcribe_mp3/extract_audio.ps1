# SINGLE FOLDER
Get-ChildItem -Filter *.mp4 | ForEach-Object { ffmpeg -i $_.FullName -q:a 0 -map a "$($_.BaseName).mp3" }

# RECURSIVE FOLDER + CHECK IF mp3 already present 
Get-ChildItem -Filter *.mp4 -Recurse | ForEach-Object {
    $output = "$($_.DirectoryName)\$($_.BaseName).mp3"
    if (-not (Test-Path $output)) {
        ffmpeg -i $_.FullName -q:a 0 -map a $output
    }
}

# Usage Instructions
# Navigate to your files: Open the folder containing your .mp4 files in Windows File Explorer.

# Open PowerShell: Hold Shift + Right-click on an empty space inside the folder. Select Open PowerShell window here.

# Note for Windows 11 users: You can just Right-click the empty space and select Open in Terminal.

# Run the command: Paste the following snippet into the terminal and press Enter.


$shell = New-Object -ComObject Shell.Application
$folder = $shell.Namespace((Get-Location).Path)
$folder.Items() | Select-Object Name, @{Name="Length";Expression={$folder.GetDetailsOf($_, 27)}}

## ps to list name and length

venv\Scripts\Activate.ps1