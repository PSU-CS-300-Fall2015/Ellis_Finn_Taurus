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
    sender.settimeout(1)
    try:
        sender.connect((tnu.host, tnu.port))
        sender.send(tnm.ciphertext)
        sender.shutdown(socket.SHUT_RDWR)
    except (socket.error, socket.timeout) as e:
        # Commented out to save it for the message queue later.
        # print("Unable to reach {user}: {reason}".format(user=user_string, reason=str(e)))
        if tnm.ciphertext:
            # Only log for real messages, not status checks
            logger.error("Failed to send a message to {user}: {reason}".format(user=user_string, reason=str(e)))
        sender.close()
        return False
    else:
        if tnm.ciphertext:
            logger.info("Sent a message to {user}.".format(user=user_string))
            filesystem.write_message(tnu.name, tnm)
        sender.close()
        return True

def is_online(tnu):
    """
    Attempt to send an empty message, to see if a TauNet node is online.
    """
    if ship_tnm(tnu, taunet.TauNetMessage().test()):
        taunet.users.by_name(tnu.name).is_on = True
        return True
    taunet.users.by_name(tnu.name).is_on = False
    return False

def send_message(stdscr, username=None):
    """
    Prompt for a user and message, generate a TauNetMessage, and send it.
    The optional keyword argument is a username; if this is supplied,
    the user won't be prompted for one.
    """
    # Show the cursor and echo output.
    curses.curs_set(1)
    curses.echo()
    stdscr.clear()
    stdscr.refresh()
    if username is None:
        safe_put(stdscr, "Recipient username: ", (0, 0))
        username = stdscr.getstr(0, 20)
        stdscr.clear()
        stdscr.refresh()
    tnu = taunet.users.by_name(username)
    if tnu == None:
        print("No such user. Known users: " + ", ".join(sorted([u.name for u in taunet.users.all()])))
        return
    if not is_online(tnu):
        print("Couldn't connect to that user's host.")
        return
    safe_put(stdscr, "Message:", (0, 0))
    message = stdscr.getstr(0, 9)
    stdscr.clear()
    stdscr.refresh()
    ship_tnm(tnu, taunet.TauNetMessage().outgoing(tnu.name, message))

def update_status(stdscr):
    """
    Update the online status of the users in the table.
    """
    safe_put(stdscr, "Checking node status, please wait ...", (2, 1))
    users = taunet.users.all()
    i = 0
    j = len(users)
    for user in users:
        i += 1
        safe_put(stdscr, "({i}/{j}) {name}".format(i=i, j=j, name=user.name.ljust(30)), (2, 39))
        is_online(user)
        stdscr.refresh()
    stdscr.clear()
    stdscr.refresh()

def view_users(stdscr):
    """
    View the list of users and their status.
    """
    stdscr.clear()
    safe_put(stdscr, "* marks a user online at last update. Hit any key to return to menu.", (2, 1))
    row = 4
    for user in taunet.users.all():
        if user.is_on:
            safe_put(stdscr, "*", (row, 1))
        safe_put(stdscr, user.name, (row, 3))
        row += 1
    stdscr.refresh()

    # Wait for any key, then clear and return to menu.
    stdscr.getch()
    stdscr.clear()
    stdscr.refresh()

def list_messages(stdscr):
    """
    List the messages available to be read and prompt to read one.
    """
    # Show the cursor and echo output.
    curses.curs_set(1)
    curses.echo()
    conversations = filesystem.conversations()
    stdscr.clear()
    row = 1
    column = 1
    for name in conversations:
        safe_put(stdscr, name, (row, column))
        row += 1
    safe_put(stdscr, "Start typing a name: ", (row+1, column))
    stdscr.refresh()
    selection = ""
    possibilities = conversations
    while len(possibilities) > 1:
        selection += chr(stdscr.getch())
        if selection.endswith("\n") and selection[:-1] in possibilities:
            # Hit enter to confirm the choice of a username when it's a
            # substring of another username.
            possibilities = [selection[:-1]]
            break
        possibilities = [p for p in possibilities if p.startswith(selection)]
    curses.curs_set(0)
    curses.noecho()
    stdscr.clear()
    stdscr.refresh()
    if possibilities:
        read_message(stdscr, possibilities[0])
    else:
        print("No user matched '{selection}'".format(selection=selection))

def read_message(stdscr, conversation):
    """
    View the backlog of a specific message.
    """
    backlog = []
    tail = filesystem.tail_conversation(conversation)
    old_backlog = 0
    while True:
        # These settings are inside the loop because the reply mode disables them.
        stdscr.nodelay(1)
        curses.noecho()
        for line in tail:
            if line:
                backlog.append(line.replace("\r", ""))
            else:
                break
        if old_backlog != len(backlog):
            stdscr.erase()
            safe_put(stdscr, "Viewing conversation with {user}. You can (r)eply or (q)uit.".format(user=conversation), (2, 0))
            safe_put(stdscr, "\r".join(backlog[-20:]), (4, 0))
            stdscr.refresh()
        old_backlog = len(backlog)

        selection = stdscr.getch()
        if selection == ord("q"):
            break
        if selection == ord("r"):
            stdscr.nodelay(0)
            send_message(stdscr, conversation)
            # Trigger a redraw after sending a message
            old_backlog = 0
        time.sleep(0.1)
    stdscr.nodelay(0)
    stdscr.clear()
    stdscr.refresh()

def menu(stdscr):
    """
    Display the menu of basic commands and execute the requested one.
    """
    options = {}
    options["v"] = ("(V)iew user list", view_users)
    options["r"] = ("(R)ead messages", list_messages)
    options["s"] = ("(S)end a new message", send_message)
    options["u"] = ("(U)pdate node status (slow!)", update_status)
    while True:
        # Don't show the cursor or echo output.
        # These are inside the loop so menu items can unset them.
        curses.curs_set(0)
        curses.noecho()
        row = 4
        column = 5
        for o in sorted(options):
            safe_put(stdscr, options[o][0], (row, column))
            row += 1
        safe_put(stdscr, "(Q)uit Taurus", (row+1, column))
        stdscr.refresh()

        c = stdscr.getch()
        if not 0 < c < 255:
            continue
        if chr(c) == "q":
            break
        if chr(c) in options:
            options[chr(c)][1](stdscr)

if __name__ == "__main__":
    curses.wrapper(menu)
