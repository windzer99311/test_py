from pytube import YouTube, Playlist


path = "Downloads"


def playlist_downloader(playlist_url, start, end):
    
    playlist = Playlist(playlist_url)
    
    print(f"Downloading : {playlist.title}")
    
    print("-------------")
    print(playlist.title)
    print(f"Video Sayısı: {len(playlist.videos)}")
    print("-------------")
    
    for url in playlist.video_urls[start:end]:
        video = YouTube(url,use_oauth=True)
        print(f"{video.title} İndiriliyor...")
        video.streams.get_highest_resolution().download(path, filename=video.title + ".mp4")
        print(f"{video.title} indirildi.")

    
def video_downloader(video_url):
    
    video = YouTube(video_url)
    video_stream = video.streams.get_highest_resolution()
    print(f"{video.title} Dönüştürülüyor...")
    video_stream.download(path, filename=video.title + ".mp4")
    print(f"{video.title} indirildi.")

def main():

        
    # start = int(input("Başlangıç: "))
    # end = int(input("Bitiş: "))
    pass

if __name__ == "__main__":
    main()
    
    