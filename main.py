# language: Python 3, file: report.py, target: any OS with terminal
# BCS REPORT TOOL — session manager + channel info + reporter.
# Requires: pip install telethon termcolor
#
# Credits:
#   Channel   : https://t.me/BLACK_CYBER_FORCE
#   Developer : @BcS_RaiFuL

import asyncio
import sys
import time
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.functions.messages import ReportRequest as MsgReportRequest, GetFullChatRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonFake,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonCopyright,
    InputReportReasonIllegalDrugs,
    InputReportReasonPersonalDetails,
    InputReportReasonOther,
    Channel,
    Chat,
    User,
)
from telethon.errors import (
    FloodWaitError,
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    ApiIdPublishedFloodError,
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneNumberBannedError,
)
from termcolor import colored

CHANNEL = "https://t.me/BLACK_CYBER_FORCE"
DEVELOPER = "@BcS_RaiFuL"
BANNER_NAME = "BCS REPORT TOOL"

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

REASONS = {
    1:  ("I don't like it",        InputReportReasonOther()),
    2:  ("Child abuse",            InputReportReasonChildAbuse()),
    3:  ("Violence",               InputReportReasonViolence()),
    4:  ("Illegal goods",          InputReportReasonIllegalDrugs()),
    5:  ("Illegal adult content",  InputReportReasonPornography()),
    6:  ("Personal data",          InputReportReasonPersonalDetails()),
    7:  ("Terrorism",              InputReportReasonViolence()),
    8:  ("Scam or spam",           InputReportReasonSpam()),
    9:  ("Copyright",              InputReportReasonCopyright()),
    10: ("Other",                  InputReportReasonOther()),
}


def show_banner():
    import os
    os.system("cls" if os.name == "nt" else "clear")
    line = "=" * 62
    pad = " " * 2
    print(colored(line, "cyan", attrs=["bold"]))
    print(colored(pad + "██████╗  ██████╗ ███████╗", "cyan", attrs=["bold"]))
    print(colored(pad + "██╔══██╗██╔════╝██╔════╝", "cyan", attrs=["bold"]))
    print(colored(pad + "██████╔╝██║     ███████╗", "cyan", attrs=["bold"]))
    print(colored(pad + "██╔══██╗██║     ╚════██║", "cyan", attrs=["bold"]))
    print(colored(pad + "██████╔╝╚██████╗███████║", "cyan", attrs=["bold"]))
    print(colored(pad + "╚═════╝  ╚═════╝╚══════╝", "cyan", attrs=["bold"]))
    print(colored(line, "cyan"))
    print(colored(pad + f"[ {BANNER_NAME} ]".center(58), "yellow", attrs=["bold", "reverse"]))
    print(colored(line, "cyan"))
    print(colored(f"   Channel   : {CHANNEL}", "green"))
    print(colored(f"   Developer : {DEVELOPER}", "green"))
    print(colored(line, "cyan"))
    print()


def typewrite(text, color="cyan", delay=0.005):
    for ch in text:
        sys.stdout.write(colored(ch, color))
        sys.stdout.flush()
        time.sleep(delay)
    print()


def pause():
    input(colored("\n[ press ENTER to continue ]", "yellow"))


def ask(prompt, color="red"):
    return input(colored(prompt, color)).strip()


def ask_int(prompt, valid, color="red"):
    while True:
        v = ask(prompt, color)
        try:
            n = int(v)
            if n in valid:
                return n
        except ValueError:
            pass
        print(colored(f"  [!] pick a number from {list(valid)}", "red"))


def list_sessions():
    return sorted(p.stem for p in SESSIONS_DIR.glob("*.session"))


# ------------------------------------------------------------------
# 1. SESSION ADD
# ------------------------------------------------------------------
def add_session_menu():
    show_banner()
    typewrite("  >> SESSION MANAGER", "yellow")
    print()

    existing = list_sessions()
    if existing:
        print(colored("  existing sessions:", "green"))
        for s in existing:
            print(colored(f"    - {s}", "green"))
        print()
    else:
        print(colored("  no sessions yet\n", "red"))

    name = ask("  session name (e.g. main): ", "red")
    if not name:
        print(colored("  [!] name required", "red"))
        return pause()

    api_id_s = ask("  api_id (numbers): ", "red")
    try:
        api_id = int(api_id_s)
    except ValueError:
        print(colored("  [!] api_id must be numeric", "red"))
        return pause()

    api_hash = ask("  api_hash: ", "red").strip()
    if len(api_hash) != 32:
        print(colored("  [!] api_hash must be 32 chars (hex)", "red"))
        return pause()

    phone = ask("  phone (+880...): ", "red")
    if not phone.startswith("+"):
        print(colored("  [!] phone must start with +", "red"))
        return pause()

    session_path = str(SESSIONS_DIR / name)
    print()
    print(colored(f"  [*] sending login code to {phone}...", "cyan"))

    async def _login():
        client = TelegramClient(session_path, api_id, api_hash)
        await client.connect()
        try:
            if await client.is_user_authorized():
                me = await client.get_me()
                print(colored(f"  [+] already logged in as {me.username or me.id}", "green"))
                return

            try:
                sent = await client.send_code_request(phone)
            except ApiIdPublishedFloodError:
                print(colored("\n  [X] ApiIdPublishedFloodError — ei api_id publicly leaked, Telegram block koreche.", "red", attrs=["bold"]))
                print(colored("      my.telegram.org theke nijer API creds nao.", "yellow"))
                return
            except ApiIdInvalidError:
                print(colored("  [X] ApiIdInvalidError — api_id/api_hash pair bhul", "red"))
                return
            except PhoneNumberInvalidError:
                print(colored("  [X] PhoneNumberInvalidError — country code soho de (+880...)", "red"))
                return
            except PhoneNumberBannedError:
                print(colored("  [X] PhoneNumberBannedError — number banned", "red"))
                return

            code = ask("  OTP code: ", "red")
            try:
                await client.sign_in(phone, code, phone_code_hash=sent.phone_code_hash)
            except SessionPasswordNeededError:
                pwd = ask("  2FA password: ", "red")
                await client.sign_in(password=pwd)

            me = await client.get_me()
            print(colored(f"  [+] logged in as {me.username or me.id}", "green"))
            print(colored(f"  [+] session saved: {name}.session", "green"))
        finally:
            await client.disconnect()

    try:
        asyncio.get_event_loop().run_until_complete(_login())
    except PhoneCodeInvalidError:
        print(colored("  [!] wrong OTP", "red"))
    except PhoneCodeExpiredError:
        print(colored("  [!] OTP expired", "red"))
    except Exception as e:
        print(colored(f"  [x] {type(e).__name__}: {e}", "red"))

    pause()


# ------------------------------------------------------------------
# CHANNEL INFO
# ------------------------------------------------------------------
async def fetch_channel_info(client, target):
    entity = await client.get_entity(target)
    info = {
        "title": getattr(entity, "title", None),
        "username": getattr(entity, "username", None),
        "id": entity.id,
        "type": None,
        "members": None,
        "description": None,
    }

    if isinstance(entity, Channel):
        info["type"] = "Channel" if entity.broadcast else "Supergroup"
        try:
            full = await client(GetFullChannelRequest(channel=entity))
            info["members"] = full.full_chat.participants_count
            info["description"] = full.full_chat.about
        except Exception:
            pass
    elif isinstance(entity, Chat):
        info["type"] = "Group (legacy)"
        try:
            full = await client(GetFullChatRequest(chat_id=entity.id))
            info["members"] = getattr(full.full_chat, "participants_count", None)
            info["description"] = getattr(full.full_chat, "about", None)
        except Exception:
            pass
    elif isinstance(entity, User):
        info["type"] = "Bot" if entity.bot else "User"
        info["title"] = ((entity.first_name or "") + (" " + entity.last_name if entity.last_name else "")).strip()

    return entity, info


def print_info(info):
    line = "+" + "-" * 48 + "+"
    print(colored("\n  " + line, "cyan"))
    print(colored("  | " + "TARGET INFO".center(46) + " |", "cyan"))
    print(colored("  " + line, "cyan"))
    rows = [
        ("Title",    str(info["title"] or "—")[:44]),
        ("Username", ("@" + str(info["username"]))[:44] if info["username"] else "—"),
        ("Type",     str(info["type"] or "—")[:44]),
        ("ID",       str(info["id"])[:44]),
        ("Members",  f"{info['members']:,}" if info["members"] is not None else "—"),
    ]
    if info["description"]:
        rows.append(("About", info["description"].replace("\n", " ")[:44]))
    for label, val in rows:
        print(colored(f"  | {label:<9}: {val:<34} |", "green"))
    print(colored("  " + line, "cyan"))


# ------------------------------------------------------------------
# REPORT DISPATCH — verified working paths only
# ------------------------------------------------------------------
async def send_report(client, entity, reason_obj, comment, post_id=None):
    """
    Working Telethon report paths:
      - post_id given -> messages.ReportRequest(peer, id=[post_id], option=bytes(reason), message)
      - everything else (Channel, Chat, User, Bot) -> account.ReportPeerRequest(peer, reason, message)
    account.ReportPeerRequest is the current, working, universal report endpoint.
    """
    if post_id is not None:
        await client(MsgReportRequest(
            peer=entity,
            id=[int(post_id)],
            option=bytes(reason_obj),
            message=comment,
        ))
        return "post"

    await client(ReportPeerRequest(
        peer=entity,
        reason=reason_obj,
        message=comment,
    ))
    return "peer"


# ------------------------------------------------------------------
# 2. REPORT
# ------------------------------------------------------------------
def pick_session():
    sessions = list_sessions()
    if not sessions:
        print(colored("  [!] no session — add one first", "red"))
        return None
    print(colored("  sessions:", "green"))
    for i, s in enumerate(sessions, 1):
        print(colored(f"    {i}) {s}", "green"))
    print()
    n = ask_int("  pick session number: ", {i for i in range(1, len(sessions) + 1)})
    return sessions[n - 1]


def pick_reason():
    print(colored("\n  reasons:", "green"))
    for n, (name, _) in REASONS.items():
        print(colored(f"    {n}) {name}", "green"))
    print()
    n = ask_int("  pick reason number: ", set(REASONS.keys()))
    return REASONS[n]


async def _report_flow(session_name):
    path = str(SESSIONS_DIR / session_name)
    client = TelegramClient(path, 1, "x")
    await client.connect()
    try:
        if not await client.is_user_authorized():
            print(colored(f"  [!] session '{session_name}' not authorized", "red"))
            return

        me = await client.get_me()
        print(colored(f"  [*] account: {me.username or me.id}", "cyan"))

        print()
        print(colored("  what to report:", "green"))
        print(colored("    1) Channel / Group / User by username", "green"))
        print(colored("    2) Post link (https://t.me/chan/12345)", "green"))
        mode = ask_int("  pick [1-2]: ", {1, 2})

        post_id = None
        if mode == 2:
            while True:
                link = ask("  post link: ", "red")
                if not link.startswith("https://t.me/"):
                    print(colored("  [!] must start with https://t.me/", "red"))
                    continue
                parts = link.replace("https://t.me/", "").split("/")
                if len(parts) != 2 or not parts[1].isdigit():
                    print(colored("  [!] format: https://t.me/chan/12345", "red"))
                    continue
                target = parts[0]
                post_id = parts[1]
                break
        else:
            target = ask("  username / @username: ", "red").lstrip("@")

        print(colored("\n  [*] fetching target info...", "cyan"))
        try:
            entity, info = await fetch_channel_info(client, target)
        except Exception as e:
            print(colored(f"  [x] {type(e).__name__}: {e}", "red"))
            return

        print_info(info)

        confirm = ask("\n  proceed to report this target? (y/n): ", "yellow").lower()
        if confirm != "y":
            print(colored("  [*] cancelled", "yellow"))
            return

        reason_name, reason_obj = pick_reason()
        count = ask_int("\n  how many reports: ", set(range(1, 501)))

        if post_id:
            comment = f"Reported post {post_id} in @{target} for {reason_name}"
        else:
            comment = ask("\n  evidence comment (optional): ", "red") or f"Reported @{target} for {reason_name}"

        print(colored(f"\n  [*] sending {count} reports -> @{target}", "cyan"))

        ok = 0
        fail = 0
        last_err = None
        for i in range(count):
            try:
                kind = await send_report(client, entity, reason_obj, comment, post_id)
                ok += 1
                print(colored(f"    [+] report {i + 1}/{count} sent ({kind})", "green"))
                await asyncio.sleep(2)
            except FloodWaitError as fw:
                print(colored(f"    [!] flood wait {fw.seconds}s — resting", "yellow"))
                await asyncio.sleep(fw.seconds + 5)
            except Exception as e:
                fail += 1
                last_err = f"{type(e).__name__}: {e}"
                print(colored(f"    [x] {last_err}", "red"))

        print(colored(f"\n  [+] done — {ok}/{count} sent, {fail} failed", "green" if ok else "red"))
        if fail and last_err:
            print(colored(f"  [!] last error: {last_err}", "yellow"))
    finally:
        await client.disconnect()


def report_menu():
    show_banner()
    typewrite("  >> REPORT", "yellow")
    print()

    session = pick_session()
    if not session:
        return pause()

    asyncio.get_event_loop().run_until_complete(_report_flow(session))
    pause()


# ------------------------------------------------------------------
# MAIN MENU
# ------------------------------------------------------------------
def main_menu():
    while True:
        show_banner()
        typewrite("  >> MAIN MENU\n", "yellow")
        print(colored("    1) Add Session   (api_id / api_hash / phone / OTP)", "green"))
        print(colored("    2) Report", "green"))
        print(colored("    3) Exit", "green"))
        print()
        choice = ask_int("  choose [1-3]: ", {1, 2, 3}, "red")

        if choice == 1:
            add_session_menu()
        elif choice == 2:
            report_menu()
        elif choice == 3:
            show_banner()
            print(colored(f"  {BANNER_NAME} — goodbye.", "cyan"))
            print(colored(f"  {CHANNEL}", "green"))
            sys.exit(0)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(colored("\n  [*] interrupted", "yellow"))
        sys.exit(0)