param(
    [string]$remote = 'origin'
)

Write-Output "Creating chapter branches and pushing to $remote..."

git fetch $remote
$current = git rev-parse --abbrev-ref HEAD
if ($LASTEXITCODE -ne 0) { Write-Error "git command failed"; exit 1 }

git checkout develop 2>$null
if ($LASTEXITCODE -ne 0) { git checkout -b develop }
git pull $remote develop

function create-and-push($b) {
    git checkout -b $b
    git push -u $remote $b
}

create-and-push 'chapters'
for ($i=1; $i -le 5; $i++) {
    $b = "chapters/ch$i"
    create-and-push $b
}

git checkout $current
Write-Output "Done. Branches created: chapters and chapters/ch1..ch5"
