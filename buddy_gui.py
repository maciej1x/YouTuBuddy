#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpass
import io
import logging
import os
import platform
import requests
import string
import sys
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as messagebox
from datetime import timedelta
from PIL import Image, ImageTk

from buddy_downloader import BuddyDownloader

class BuddyGUI:
    """
    GUI that helps download video and/or audio from YouTube link
    """
    def __init__(self):
        self.logger = logging.getLogger('YouTuBuddy')
        self.buddy_downloader = BuddyDownloader()
        self.run()


    def check_url(self):
        """
        Check given url and refresh summary and download boxes

        Returns
        -------
        None.

        """

        # Clear frames
        self.clear_frame(self.frame_info)
        self.clear_frame(self.frame_download)

        # Load videodata
        self.logger.info('Loading videodata...')

        try:
            self.buddy_downloader.load_url(self.url.get())
        except Exception as e:
            self.logger.error(f'Could not load video. Error: {str(e)[:400]}')
            messagebox.showerror(title='Error',
                                    message='Invalid url. Enter proper url to YouTube video.')
            return

        self.yt = self.buddy_downloader.yt
        self.logger.info('Videodata loaded')

        # Show frames
        self.show_info()
        self.show_downloadbox()

        # Change urlbutton color
        self.button_url.configure(bg='lightblue')


    def show_info(self):
        """
        Show info about loaded video in Summary box

        Returns
        -------
        None.

        """
        # Show title
        self.label_info = tk.Label(self.frame_info,
                                   text='Summary:',
                                   font=('', 12, 'bold')
                                   )
        self.label_info.pack(side=tk.TOP, anchor='nw', expand='YES')

        # Show thumbnail image
        raw_image = requests.get(self.yt.thumbnail_url).content
        im = Image.open(io.BytesIO(raw_image))
        im.thumbnail((350, 500), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(im)
        self.thumbnail_image = tk.Label(self.frame_info, image=self.image)
        self.thumbnail_image.pack(side=tk.TOP, anchor='nw')

        # Show video details
        info_texts = [
            f'Title:  {self.yt.title[:50]}',
            f'Added:  {self.yt.publish_date}',
            f'Length: {timedelta(seconds=self.yt.length)}',
            f'Views:  {self.yt.views}'
            ]

        for text in info_texts:
            self.label_info_text = tk.Label(self.frame_info, text=text, anchor='w')
            self.label_info_text.pack(side=tk.TOP, anchor='nw')


    def show_downloadbox(self):
        """
        Show download options

        Returns
        -------
        None.

        """
        # Show title
        self.label_download = tk.Label(self.frame_download,
                                       text='Download:',
                                       font=('', 12, 'bold')
                                       )
        self.label_download.pack(side=tk.TOP, anchor='nw', expand='YES')

        # Empty space
        self.space = tk.Label(self.frame_download, text='\n', font=('', 8, 'bold'))
        self.space.pack()

        # Checkbuttons
        self.checkbutton_video = tk.Checkbutton(self.frame_download,
                                                text="Video",
                                                variable=self.video_var,
                                                font=('', 12, 'bold')
                                                )
        self.checkbutton_video.pack()

        self.checkbutton_audio = tk.Checkbutton(self.frame_download,
                                                text="Audio",
                                                variable=self.audio_var,
                                                font=('', 12, 'bold')
                                                )
        self.checkbutton_audio.pack()

        # Empty space
        self.space = tk.Label(self.frame_download, text='\n', font=('', 8, 'bold'))
        self.space.pack()

        # Add download button
        self.download_button = tk.Button(self.frame_download,
                                         height=4, width=14,
                                         text='Download',
                                         command=self.download,
                                         bg='lightgreen',
                                         font=('', 12, 'bold')
                                         )
        self.download_button.pack(side=tk.RIGHT)


    @staticmethod
    def enable_frame(frame: tk.Frame) -> None:
        """
        Set all children's status as normal in given frame

        Parameters
        ----------
        frame : tk.Frame
            frame object.

        Returns
        -------
        None.

        """
        for child in frame.winfo_children():
            child.configure(state='normal')

    @staticmethod
    def disable_frame(frame: tk.Frame) -> None:
        """
        Set all children's status as disable in given frame

        Parameters
        ----------
        frame : tk.Frame
            frame object.

        Returns
        -------
        None.

        """
        for child in frame.winfo_children():
            child.configure(state='disable')

    @staticmethod
    def clear_frame(frame: tk.Frame) -> None:
        """
        Deletes all children in given frame

        Parameters
        ----------
        frame : tk.Frame
            frame object.

        Returns
        -------
        None.

        """
        for child in frame.winfo_children():
            child.destroy()

    def init_download_path(self):
        """
        Get default download_path for proper OS
        Linux: ~/Downloads
        Windows: C://Users/{username}/Downloads


        Returns
        -------
        download_path : str
            default downloads path.

        """
        # Detect os
        system = platform.system()

        username = getpass.getuser()

        if system == 'Linux':
            download_path = os.path.join(os.path.expanduser("~"), 'Downloads')
        elif system  == 'Windows':
            download_path = f'C://Users/{username}/Downloads'
        else:
            self.logger.error(f'Ooops, YouTuBuddy does not support system {system}')
            sys.exit(0)

        return download_path

    def choose_download_path(self):
        """
        Choose download path.
        Changes entry bar with download path
        For button Change (download directory)

        Returns
        -------
        None.

        """
        new_directory = fd.askdirectory()
        if new_directory:
            self.entry_path.configure(state='normal')
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(tk.INSERT, new_directory)

    def download(self):
        """
        Download video and/or audio. For button Download

        Returns
        -------
        None.

        """

        video_var = self.video_var.get()
        audio_var = self.audio_var.get()

        if video_var and audio_var:
            downloaded_video = self.buddy_downloader.download_video(output_path=self.download_path.get())
            self.buddy_downloader.convert_mp4_to_mp3(downloaded_video)
        elif video_var and not audio_var:
            self.buddy_downloader.download_video(output_path=self.download_path.get())
        elif not video_var and audio_var:
            allowed_chars = string.ascii_letters + string.digits + ' '
            filename = ''.join(letter for letter in self.yt.title if letter in allowed_chars) + '_audio'
            downloaded_video = self.buddy_downloader.download_video(output_path=self.download_path.get(),
                                                                    filename=filename)
            self.buddy_downloader.convert_mp4_to_mp3(downloaded_video)
            os.remove(downloaded_video)
        else:
            messagebox.showinfo(title='Warning', message='Select at least one checkbox')
            return

        messagebox.showinfo(title='Success', message='Downloading finished.')


    def run(self):
        """
        Runs GUI

        Returns
        -------
        None.

        """

        # Window
        self.win = tk.Tk()
        self.win.title('YouTuBuddy')
        self.win.geometry('600x450+20+20')

        # Variables
        self.download_path = tk.StringVar()
        self.url = tk.StringVar()
        self.video_var = tk.IntVar()
        self.audio_var = tk.IntVar()

        # =====================================================================
        # TOP FRAME/INPUT URL
        # =====================================================================
        self.frame_url = tk.Frame(self.win, borderwidth=10)
        self.frame_url.pack(side=tk.TOP, anchor='w')

        self.label_url = tk.Label(self.frame_url,
                                  text='Enter URL:',
                                  font=('', 12, 'bold')
                                  )
        self.label_url.pack(side=tk.LEFT, anchor='w')

        self.entry_url = tk.Entry(self.frame_url,
                                  width=50,
                                  state='normal',
                                  textvariable=self.url,
                                  font=('', 10, '')
                                  )
        self.entry_url.pack(side=tk.LEFT, anchor='w')


        self.button_url = tk.Button(self.frame_url,
                                    text='Check',
                                    command=self.check_url,
                                    bg='lightgreen'
                                    )
        self.button_url.pack(side=tk.RIGHT)

        # =====================================================================
        # TOP FRAME/DOWNLOAD PATH
        # =====================================================================
        self.frame_path = tk.Frame(self.win, borderwidth=10)
        self.frame_path.pack(side=tk.TOP, anchor='w')

        self.label_path = tk.Label(self.frame_path,
                                   text='Folder:',
                                   font=('', 12, 'bold')
                                   )
        self.label_path.pack(side=tk.LEFT, anchor='w')

        self.entry_path = tk.Entry(self.frame_path,
                                   width=53,
                                   state='normal',
                                   textvariable=self.download_path,
                                   font=('', 10, '')
                                   )
        self.entry_path.pack(side=tk.LEFT, anchor='w')
        self.entry_path.insert(0, self.init_download_path())

        self.button_path = tk.Button(self.frame_path,
                                     text='Change',
                                     command=self.choose_download_path,
                                     bg='LightGoldenrod1')
        self.button_path.pack(side=tk.RIGHT)


        # =====================================================================
        # BOTTOM FRAME
        # =====================================================================
        self.frame_bottom = tk.Frame(self.win)
        self.frame_bottom.pack(side=tk.TOP, anchor='nw')

        # =====================================================================
        # INFO FRAME
        # =====================================================================
        self.frame_info = tk.Frame(self.frame_bottom, borderwidth=10)
        self.frame_info.pack(side=tk.LEFT)


        # =====================================================================
        # DOWNLOAD FRAME
        # =====================================================================
        self.frame_download = tk.Frame(self.frame_bottom, borderwidth=10)
        self.frame_download.pack(side=tk.RIGHT, anchor='ne')


        # Run
        self.win.mainloop()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO)

    gui = BuddyGUI()