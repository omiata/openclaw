param(
    [string]$PayloadPath = ".\camper_packliste_microsoft_todo_import_2026-06-04.json"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $PayloadPath)) {
    throw "No existe el payload JSON: $PayloadPath"
}

$payload = Get-Content -Raw -Path $PayloadPath | ConvertFrom-Json

if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.Authentication)) {
    Install-Module Microsoft.Graph.Authentication -Scope CurrentUser -Force
}

Import-Module Microsoft.Graph.Authentication
Connect-MgGraph -Scopes "Tasks.ReadWrite" -NoWelcome

$listBody = @{
    displayName = $payload.listTitle
} | ConvertTo-Json

$list = Invoke-MgGraphRequest `
    -Method POST `
    -Uri "https://graph.microsoft.com/v1.0/me/todo/lists" `
    -Body $listBody `
    -ContentType "application/json"

foreach ($task in $payload.tasks) {
    $taskBody = @{
        title = $task.title
        status = $task.status
        body = @{
            content = "Importado desde $($payload.source) el $($payload.generatedAt)"
            contentType = "text"
        }
    } | ConvertTo-Json -Depth 5

    Invoke-MgGraphRequest `
        -Method POST `
        -Uri "https://graph.microsoft.com/v1.0/me/todo/lists/$($list.id)/tasks" `
        -Body $taskBody `
        -ContentType "application/json" | Out-Null
}

Write-Host "Importadas $($payload.tasks.Count) tareas en Microsoft To Do: $($payload.listTitle)"
