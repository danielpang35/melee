param([string]$Evidence='Saved/WorkingBodyRepair')
Add-Type -AssemblyName System.Drawing
$base=Join-Path (Split-Path -Parent $PSScriptRoot) $Evidence
function Make-Sheet([string[]]$paths,[string[]]$labels,[string]$output,[int]$size=450) {
    $columns=2
    $rows=[int][math]::Ceiling($paths.Count/$columns)
    $sheet=New-Object System.Drawing.Bitmap ($columns*$size),($rows*($size+26))
    $g=[System.Drawing.Graphics]::FromImage($sheet)
    $g.Clear([System.Drawing.Color]::FromArgb(35,35,35))
    $font=New-Object System.Drawing.Font 'Arial',11
    for($i=0;$i -lt $paths.Count;$i++) {
        $im=[System.Drawing.Image]::FromFile($paths[$i])
        $x=($i%$columns)*$size; $y=[int][math]::Floor($i/$columns)*($size+26)
        $g.DrawImage($im,[int]$x,[int]($y+26),$size,$size)
        $g.DrawString($labels[$i],$font,[System.Drawing.Brushes]::White,[single]($x+8),[single]($y+4))
        $im.Dispose()
    }
    $sheet.Save($output,[System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose();$font.Dispose();$sheet.Dispose()
}
$views=@('front','rear','left','right')
foreach($type in @('source-current','textured-current')) {
    foreach($lod in 0..3) {
        $dir=Join-Path $base ($type+'/LOD'+$lod)
        Make-Sheet ($views | ForEach-Object {Join-Path $dir ($_+'.png')}) ($views | ForEach-Object {'LOD'+$lod+' '+$_}) (Join-Path $base ($type+'-LOD'+$lod+'-sheet.png'))
    }
}
foreach($pose in @('rest','shoulders','elbows','forearm_twist','wrists','torso','hips_knees')) {
    $dir=Join-Path $base ('joint-validation-current/deformation/'+$pose)
    Make-Sheet ($views | ForEach-Object {Join-Path $dir ($_+'.png')}) ($views | ForEach-Object {$pose+' '+$_}) (Join-Path $base ('pose-'+$pose+'-sheet.png'))
}
