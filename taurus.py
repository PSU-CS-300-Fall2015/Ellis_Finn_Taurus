#!/usr/bin/python

"""
Copyright (c) 2015 Finn Ellis, licensed under the MIT License.
(See accompanying LICENSE file for details.)
"""

import socket
import sys
import curses
import time

import taunet
import filesystem


# Set up logger.
logger=filesystem.get_logger("taurus")

def safe_put(stdscr, string, loc):
    """
    Print to the given location. This is a workaround because curses won't
    print properly to the bottom-right location.
    """
    if loc[0] == curses.LINES-1 and loc[1] == curses.COLS-1:
        stdscr.addstr(loc[0], loc[1]-1, string.encode("utf-8"))
        stdscr.insstr(loc[0], loc[1]-1, " ")
    else:
        stdscr.addstr(loc[0], loc[1], string.encode("utf-8"))

def ship_tnm(tnu, tnm):
    """
    Send a TauNetMessage over the network to its recipient.
    """
    user_string = "{user} ({host}:{port})".format(user=tnu.name, host=tnu.host, port=str(tnu.port))
    sender = socket.socket()
    sender.settimeout(3)
    try:
        sender.connect((tnu.host, tnu.port))
        sender.send(tnm.ciphertext)
        sender.shutdown(socket.SHUT_RDWR)
    except (socket.error, socket.timeout) as e:
        print("Unable to reach {user}: {reason}".format(user=user_string, reason=str(e)))
        logger.error("Failed to send a message to {user}: {reason}".format(user=user_string, reason=str(e)))
        sender.close()
        return False
    else:
        logger.info("Sent a message to {user}.".format(user=user_string))
        filesystem.write_message(tnu.name, tnm)
        sender.close()
        return True

def is_online(tnu):
    """
    Attempt to send an empty message, to see if a TauNet node is online.
    """
    if ship_tnm(tnu, taunet.TauNetMessage().outgoing(tnu.name, "")):
        return True
    return False

def send_message(stdscr):
    """
    Prompt for a user and message, generate a TauNetMessage, and send it.
    """
    # Show the cursor and echo output.
    curses.curs_set(1)
    curses.echo()
    stdscr.clear()
    stdscr.refresh()
    safe_put(stdscr, "Recipient username: ", (0, 0))
    username = stdscr.getstr(0, 20)
    tnu = taunet.users.by_name(username)
    if tnu == None:
        print("No such user. Known users: " + ", ".join(sorted([u.name for u in taunet.users.all()])))
        return
    if not is_online(tnu):
        # The error message is printed in ship_tnm.
        return
    safe_put(stdscr, "Message:", (1, 0))
    message = stdscr.getstr(1, 9)
    ship_tnm(tnu, taunet.TauNetMessage().outgoing(tnu.name, message))

def menu(stdscr):
    """
    Display the menu of basic commands and execute the requested one.
    """
    while True:
        # Don't show the cursor or echo output.
        # These are inside the loop so menu items can unset them.
        curses.curs_set(0)
        curses.noecho()
        safe_put(stdscr, "(S)end a new message", (5, 5))
        safe_put(stdscr, "(Q)uit Taurus", (6, 5))
        stdscr.refresh()

        c = stdscr.getch()
        if c == ord("q"):
            break
        if c == ord("s"):
            send_message(stdscr)


if __name__ == "__main__":
    curses.wrapper(menu)
