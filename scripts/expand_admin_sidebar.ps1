$root = 'C:\Users\DELL\Desktop\PROJEXT\stitch_role_based_exam_platform'

$items = @(
  @{icon='dashboard'; label='Dashboard'},
  @{icon='event_note'; label='Exam Schedule'},
  @{icon='swap_horiz'; label='Swap Requests'},
  @{icon='assignment_ind'; label='Room Attendance'},
  @{icon='how_to_reg'; label='Check-ins'},
  @{icon='history_edu'; label='Admin Audit Logs & Statistics'},
  @{icon='health_and_safety'; label='Admin System Health'},
  @{icon='manage_accounts'; label='Admin User Management (Excel Import)'},
  @{icon='qr_code_scanner'; label='Admin Check-in Feed (Operational)'},
  @{icon='person_search'; label='Admin Student Management'},
  @{icon='fact_check'; label='Admin Submissions Oversight'},
  @{icon='hub'; label='Admin Logistics Control Center'},
  @{icon='print'; label='Faculty Exam Printing Oversight'},
  @{icon='library_books'; label='Admin Course Management'},
  @{icon='meeting_room'; label='Admin Room Availability & Management'},
  @{icon='payments'; label='Admin Financial Oversight & Payouts'},
  @{icon='assessment'; label='Admin Comprehensive Attendance Report'},
  @{icon='dashboard_customize'; label='Admin Operations Command Dashboard'},
  @{icon='calendar_view_month'; label='Admin Optimization Dashboard'},
  @{icon='playlist_add_check'; label='Admin Manual Subject Assignment'},
  @{icon='grid_view'; label='Admin Venue & Staff Allocation'},
  @{icon='settings'; label='Admin Settings'},
  @{icon='lock_clock'; label='Admin Check-in Feed (Time-Locked)'},
  @{icon='insights'; label='Admin Swap Analytics Dashboard'},
  @{icon='warning'; label='Admin Attendance Anomaly Report'},
  @{icon='receipt_long'; label='Admin Attendance Audit Log'},
  @{icon='gavel'; label='Admin Audit & Compliance Dashboard'}
)

$newNavInner = ($items | ForEach-Object {
  '<a class="flex items-center gap-3 px-4 py-2.5 text-[#323233] dark:text-[#eae8e7] opacity-80 hover:bg-[#eae8e7] dark:hover:bg-[#3a3a3a] transition-all duration-300 rounded-lg group" href="#"><span class="material-symbols-outlined text-[20px]">' + $_.icon + '</span><span class="font-[""IBM_Plex_Sans_Thai""] text-[0.875rem]">' + $_.label + '</span></a>'
}) -join "`r`n"

$files = Get-ChildItem -Path $root -Directory -Filter 'admin_*' |
  ForEach-Object { Join-Path $_.FullName 'code.html' } |
  Where-Object { Test-Path $_ }

$updated = New-Object System.Collections.Generic.List[string]
$skippedNoAside = New-Object System.Collections.Generic.List[string]
$skippedNoNav = New-Object System.Collections.Generic.List[string]

foreach ($f in $files) {
  $txt = Get-Content -Raw -Path $f
  $aside = [regex]::Match($txt, '(?is)<aside[\s\S]*?</aside>')
  if (-not $aside.Success) {
    $skippedNoAside.Add($f)
    continue
  }

  $asideText = $aside.Value
  $replacedAside = [regex]::Replace(
    $asideText,
    '(?is)(<nav[^>]*>)([\s\S]*?)(</nav>)',
    "$1`r`n$newNavInner`r`n$3",
    1
  )

  if ($replacedAside -eq $asideText) {
    $skippedNoNav.Add($f)
    continue
  }

  $newTxt = $txt.Substring(0, $aside.Index) + $replacedAside + $txt.Substring($aside.Index + $aside.Length)
  if ($newTxt -ne $txt) {
    Set-Content -Path $f -Value $newTxt -NoNewline
    $updated.Add($f)
  }
}

Write-Output "UPDATED=$($updated.Count)"
Write-Output "SKIPPED_NO_ASIDE=$($skippedNoAside.Count)"
Write-Output "SKIPPED_NO_NAV=$($skippedNoNav.Count)"
if ($skippedNoAside.Count -gt 0) {
  Write-Output 'NO_ASIDE_FILES:'
  $skippedNoAside | ForEach-Object { Write-Output $_ }
}
if ($skippedNoNav.Count -gt 0) {
  Write-Output 'NO_NAV_FILES:'
  $skippedNoNav | ForEach-Object { Write-Output $_ }
}
