#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import moviepy.editor as mp
from pytube import YouTube

class BuddyDownloader:
    """
    Download video and/or audio for given YouTube url

    Returns
    -------
    None.

    """
    def __init__(self) -> None:
        self.logger = logging.getLogger('BuddyDownloader')

    def load_url(self, url: str) -> None:
        """
        Load YouTube URL

        Parameters
        ----------
        url : str
            YouTube url.

        Returns
        -------
        None.

        """
        self.logger.info(f'Getting video for url: {url}')
        self.yt = YouTube(url)

    def download_video(self, output_path=None, filename=None) -> str:
        """
        Download video from previously loaded url

        Parameters
        ----------
        output_path : str, optional
            path to output videofile. The default is None.
        filename : str, optional
            name of videofile. The default is None, which means title of video.

        Returns
        -------
        downloaded_file_path : str
            path to videofile.

        """
        self.logger.info('Downloading video...')
        ys = self.yt.streams.get_highest_resolution()
        downloaded_file_path = ys.download(output_path=output_path,
                                                filename=filename)
        self.logger.info('Downloading finished')
        return downloaded_file_path

    def convert_mp4_to_mp3(self, videofile: str) -> None:
        """
        Convert given videofile (mp4) to mp3

        Parameters
        ----------
        videofile : str
            path to videofile.mp4.

        Returns
        -------
        None.

        """
        self.logger.info('Converting video')
        clip = mp.VideoFileClip(videofile)
        self.logger.info('Saving audio')
        audiofilename = os.path.basename(videofile).split('.')[0] + '.mp3'
        clip.audio.write_audiofile(
            os.path.join(os.path.split(videofile)[0], audiofilename)
            )
