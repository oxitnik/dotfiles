#!/usr/bin/env python3

import sys
import json
import asyncio
import functools
import subprocess
import signal


MOUSE_LEFT = 1
MOUSE_RIGHT = 3
MOUSE_SCROLL_UP = 4
MOUSE_SCROLL_DOWN = 5

CLICK_HANDLERS = {
    'volume': {
        MOUSE_LEFT: 'pactl set-sink-mute 0 toggle',
        MOUSE_RIGHT: 'pactl set-sink-mute 0 toggle',
        MOUSE_SCROLL_UP: 'pactl set-sink-volume 0 +5%',
        MOUSE_SCROLL_DOWN: 'pactl set-sink-volume 0 -5%'
    }
}


def on_i3bar_message(message):
    block = message.get('name')
    button = message.get('button')

    if block and button:
        cmd = CLICK_HANDLERS.get(block, {}).get(button)
        if cmd:
            try:
                subprocess.run(
                    cmd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2
                )
            except:
                raise


async def handle_i3status_stdio(cmd, loop): 
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    first_line_data = await process.stdout.readline()
    first_line_str = first_line_data.decode('utf-8').strip()

    data = json.loads(first_line_str)
    if not 'version' in data:
        raise ValueError('unknown output')

    data['click_events']=True
    print(json.dumps(data), flush=True)

    while True:
        try:
            line = await process.stdout.readline()
            if line:
                sys.stdout.write(line.decode('utf-8'))
                sys.stdout.flush()
            else:
                break
        except KeyboardInterrupt:
            process.kill()


class StdinJsonProtocol(asyncio.Protocol):
    STATE_INIT = 'init'
    STATE_ARRAY = 'array'
    STATE_MESSAGE = 'msg'
    
    def __init__(self, message_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = self.STATE_INIT
        self.buffer = ''
        self.message_callback = message_callback

    def handle_input(self, char):
        if char == '[' and self.state == self.STATE_INIT:
            self.state = self.STATE_ARRAY
        elif self.state == self.STATE_ARRAY and char == '{':
            self.state = self.STATE_MESSAGE
            self.buffer += char
        elif self.state == self.STATE_MESSAGE and char == '}':
            self.buffer += char
            self.state = self.STATE_ARRAY
            parsed_message = json.loads(self.buffer)
            self.message_callback(parsed_message)
        elif self.state == self.STATE_MESSAGE:
            self.buffer += char
        elif self.state == self.STATE_ARRAY and char == ',':
            self.buffer = ''
        elif self.state in (self.STATE_INIT, self.STATE_ARRAY) and char == '\n':
            pass
        else:
            raise Exception(
                'unexpected state: '
                f'buf={self.buffer}, char={char}, state={self.state}'
            )

    def data_received(self, data):
        for c in data.decode():
            self.handle_input(c)
        super().data_received(data)


def main():
    cmd = sys.argv[1:]
    if not cmd:
        print('command expected')
        return 1

    loop = asyncio.get_event_loop()
    protocol_factory = functools.partial(
            StdinJsonProtocol,
            message_callback=on_i3bar_message
    )
    json_stdin_pipe_reader = loop.connect_read_pipe(
        protocol_factory,
        sys.stdin
    )
    loop.run_until_complete(asyncio.gather(
        handle_i3status_stdio(cmd, loop),
        json_stdin_pipe_reader
    ))
    loop.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())

