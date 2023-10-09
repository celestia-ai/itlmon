import argparse
import atexit
from collections import defaultdict
import curses
from glob import glob
import json
import asyncio
import boto3
import threading

import yaml

from .directory_watcher import DirectoryWatcher
from .s3_file_downloader import S3FileDownloader, split_s3_url
from .chat_interface import ChatInterface
from itllib import Itl


class StreamInterface:
    def __init__(self, itl, streams):
        self.itl = itl
        self.chat = ChatInterface()
        self.streams = streams
        self.message_handlers = defaultdict(list)

        self._attach_chat_handlers(self.chat)
        self._attach_streams()
    
    def onmessage(self, channel=None):
        def decorator(func):
            async def wrapped(*args, **kwargs):
                await func(*args, **kwargs)

            self.message_handlers[channel].append(wrapped)
            return func

        return decorator

    
    def _create_handler(self, _key):
        async def ondata(*args, **kwargs):
            if args:
                self.chat.display_message(_key, args[0])
            else:
                self.chat.display_message(_key, f"/obj {json.dumps(kwargs)}")
        
        return ondata

    def _attach_streams(self):
        for _key in self.streams:
            self.itl.ondata(_key)(self._create_handler(_key))
            self.chat.add_channel(_key)
            

    def _attach_chat_handlers(self, chat):
        @chat.onmessage()
        async def message_handler(channel, msg):
            self.chat.display_message("#system", f'sending to {channel}: {msg}')
            await self.itl.stream_send(channel, msg)

        @chat.oncommand("/help")
        async def help_handler(channel, msg):
            chat.display_message("#system", "Available commands:")
            for command in self.chat.command_handlers:
                chat.display_message("#system", command)

        @chat.oncommand("/obj")
        async def obj_handler(channel, msg):
            try:
                json_data = json.loads(msg)
            except json.JSONDecodeError:
                chat.display_message("#system", f"Invalid JSON: {msg}")
                return
            await self.itl.stream_send(channel, json_data)

        @chat.oncommand("/quit")
        async def quit_handler(channel, msg):
            chat.exit()
            
    
    def display_message(self, channel, msg):
        self.chat.display_message(channel, msg)

    def start(self):
        self.chat.run()

    def stop(self):
        self.chat.exit()

    def onput(self, stream_name):
        def decorator(func):
            async def wrapped(*args, **kwargs):
                await func(*args, **kwargs)

            return wrapped

    def ondelete(self, stream_name):
        def decorator(func):
            async def wrapped(*args, **kwargs):
                await func(*args, **kwargs)

            return wrapped

    def ondata(self, stream_name):
        def decorator(func):
            async def wrapped(*args, **kwargs):
                await func(*args, **kwargs)

            return wrapped