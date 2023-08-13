using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;



using WMPLib;

namespace オセロ
{
    public class Music
    {
        WindowsMediaPlayer _mediaPlayer = new WindowsMediaPlayer();

		public void SE()
		{
			//以下追加
			_mediaPlayer.settings.volume = 20;
			_mediaPlayer.URL = @"crrect_answer3.mp3"; 
			_mediaPlayer.controls.play();
		}
	}
}
