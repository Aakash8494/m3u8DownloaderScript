Get-ChildItem -File | Rename-Item -NewName { $_.Name -replace '-', '' }
# remove - from name 