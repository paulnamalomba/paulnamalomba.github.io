# Media Download Functions
# Functions for downloading media from YouTube and other sources

function YtDL-Playlist {
    <#
    .SYNOPSIS
    Downloads YouTube playlist as MP3 files
    
    .DESCRIPTION
    Uses yt-dlp to download an entire YouTube playlist with metadata and thumbnails
    
    .PARAMETER playlistUrl
    URL of the YouTube playlist
    
    .PARAMETER ffmpegPath
    Path to ffmpeg executable (default: system PATH)
    
    .PARAMETER ytdlpPath
    Path to yt-dlp executable
    
    .EXAMPLE
    YtDL-Playlist -playlistUrl "https://youtube.com/playlist?list=..."
    #>
    param (
        [string]$playlistUrl,
        [string]$ffmpegPath = "ffmpeg",
        [string]$ytdlpPath = "<path/to/yt-dlp.exe>"
    )
    Write-Host "--------------------------------------------------------"
    Write-Host "Downloading YouTube playlist from: $playlistUrl"
    
    if ($null -ne $playlistUrl -and $playlistUrl -ne "") {
        & $ytdlpPath `
            --ffmpeg-location $ffmpegPath `
            -x --audio-format mp3 --embed-thumbnail --add-metadata "duration > 0" `
            -o "%(playlist_index)s - %(title)s.%(ext)s" `
            $playlistUrl
        Write-Host "Download completed." -ForegroundColor Green
    } else {
        Write-Host "No playlist URL provided." -ForegroundColor Yellow
    }
    Write-Host "--------------------------------------------------------"
}

function YtDL-Song {
    <#
    .SYNOPSIS
    Downloads a single YouTube video as MP3
    
    .DESCRIPTION
    Uses yt-dlp to download a YouTube video with metadata and thumbnail
    
    .PARAMETER songUrl
    URL of the YouTube video
    
    .PARAMETER ffmpegPath
    Path to ffmpeg executable (default: system PATH)
    
    .PARAMETER ytdlpPath
    Path to yt-dlp executable
    
    .EXAMPLE
    YtDL-Song -songUrl "https://youtube.com/watch?v=..."
    #>
    param (
        [string]$songUrl,
        [string]$ffmpegPath = "ffmpeg",
        [string]$ytdlpPath = "<path/to/yt-dlp.exe>"
    )
    Write-Host "--------------------------------------------------------"
    Write-Host "Downloading YouTube song from: $songUrl"
    
    if ($null -ne $songUrl -and $songUrl -ne "") {
        & $ytdlpPath `
            --ffmpeg-location $ffmpegPath `
            -x --audio-format mp3 --embed-thumbnail --add-metadata "duration > 0" `
            -o "%(title)s.%(ext)s" `
            $songUrl
        Write-Host "Download completed." -ForegroundColor Green
    } else {
        Write-Host "No song URL provided." -ForegroundColor Yellow
    }
    Write-Host "--------------------------------------------------------"
}

# Export functions
Export-ModuleMember -Function YtDL-Playlist, YtDL-Song
