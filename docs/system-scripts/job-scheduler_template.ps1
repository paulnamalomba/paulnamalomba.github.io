# Prepend here your script path
$scriptpath = ""

# Define the scheduler action
$action = New-ScheduledTaskAction 
            -Execute 'powershell.exe' 
            -Argument "-File "$scriptpath""

# Define the scheduler trigger (e.g., daily at 2:00 AM)
$trigger = New-ScheduledTaskTrigger 
            -Daily 
            -At '11:59 PM'

# Define the principal executor
$principal = New-ScheduledTaskPrincipal 
            -UserId "SYSTEM" 
            -LogonType ServiceAccount

# Define settings for the scheduler
$settings = New-ScheduledTaskSettingsSet 
            -DontStartOnBatteries

# Register the scheduled task
Register-ScheduledTask -TaskName "Wiping SEAT Password Resets" -Action $action -Trigger $trigger -Principal $principal -Settings $settings