import configparser
import argparse
import telethon
import datetime
import collections

config = configparser.ConfigParser()
config.read("api_id.ini")

API_ID = config["general"]["api_id"]
API_HASH = config["general"]["api_hash"]
USERNAME = config["general"]["username"]

client = telethon.TelegramClient(USERNAME, API_ID, API_HASH)


async def print_me():
    me = await client.get_me()
    print(me.stringify())
    print(me.username)
    print(me.phone)
    async for dialog in client.iter_dialogs():
        print(dialog.name, "has id", dialog.id)


async def _get_messages_arr(chat_id, limit, from_user):
    ret = []
    async for message in client.iter_messages(
        chat_id, limit=limit, from_user=from_user
    ):
        ret.append(message)
    return ret


async def get_messages(chat_id, limit, from_user):
    ret = await _get_messages_arr(chat_id, limit, from_user)
    for message in ret:
        print(message.date, message.id, message.from_id, message.text)
    print("len =", len(ret))


async def send_message(chat_id, text):
    await client.send_message(chat_id, text)


async def delete_messages(chat_id, limit, from_user):
    messages = await _get_messages_arr(chat_id, limit, from_user)
    await client.delete_messages(chat_id, [x.id for x in messages], revoke=True)


async def get_located(lat, long):
    result = await client(
        telethon.functions.contacts.GetLocatedRequest(
            geo_point=telethon.types.InputGeoPoint(lat=lat, long=long),
            background=False,
        )
    )
    # print(result.stringify())

    class PeerUser:
        def __init__(self, user_id, distance):
            self.user_id = user_id
            self.distance = distance

    peer_users = []
    for x in result.updates[0].peers:
        if isinstance(x, telethon.tl.types.PeerSelfLocated) or not isinstance(
            x.peer, telethon.tl.types.PeerUser
        ):
            continue
        peer_users.append(PeerUser(x.peer.user_id, x.distance))
    peer_users.sort(key=lambda x: x.distance)
    for x in peer_users:
        user = next(u for u in result.users if u.id == x.user_id)
        print(
            ("@" + user.username) if user.username else "",
            ": " + user.first_name if user.first_name else "",
            user.last_name if user.last_name else "",
            ": id = " + str(x.user_id),
            ": ",
            str(x.distance) + " m ",
        )


async def get_sent_messages(days: int):
    me = await client.get_me()
    print(me.id)
    ret: dict[int, list[int]] = collections.defaultdict(list)
    offset_date = (datetime.datetime.now() - datetime.timedelta(days=days)).date()
    async for dialog in client.iter_dialogs():
        if dialog.id == me.id or dialog.is_channel:
            continue
        print(
            dialog.name,
            "has id",
            dialog.id,
            f"{dialog.is_user=}",
            f"{dialog.is_group=}",
            f"{dialog.is_channel=}",
        )
        async for message in client.iter_messages(
            dialog.id, from_user="me", offset_date=offset_date
        ):
            if message.date.date() >= offset_date:
                continue
            ret[dialog.id].append(message.id)
            print(message.date, message.id, message.from_id, message.text)
    count = sum(map(lambda x: len(x), ret.values()))
    print(f"{count=}")
    return ret


async def delete_sent_messages(message_ids: dict[int, list[int]]):
    for dialog_id in message_ids.keys():
        await client.delete_messages(dialog_id, message_ids[dialog_id], revoke=True)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-me", action="store_true")
    parser.add_argument("--get-messages", action="store_true")
    parser.add_argument("--send-message", action="store_true")
    parser.add_argument("--delete-messages", action="store_true")
    parser.add_argument("--get-located", action="store_true")
    parser.add_argument("--get-sent-messages", action="store_true")
    parser.add_argument("--delete-sent-messages", action="store_true")
    parser.add_argument("--days", type=int)
    parser.add_argument("--limit", default=None)
    parser.add_argument("--from-user", default=None)
    parser.add_argument("--chat-id", default="me")
    parser.add_argument("--text", default="")
    parser.add_argument("--lat", type=float)
    parser.add_argument("--long", type=float)
    args = parser.parse_args()
    if args.chat_id != "me":
        args.chat_id = int(args.chat_id)
    if args.from_user and args.from_user != "me":
        args.from_user = int(args.from_user)
    if args.limit:
        args.limit = int(args.limit)

    if args.print_me:
        await print_me()
    elif args.get_messages:
        print(f"{args.from_user=}")
        print(f"{args.chat_id=}")
        await get_messages(args.chat_id, args.limit, args.from_user)
    elif args.send_message:
        await send_message(args.chat_id, args.text)
    elif args.delete_messages:
        await delete_messages(args.chat_id, args.limit, args.from_user)
    elif args.get_located:
        print(f"{args.lat=}")
        print(f"{args.long=}")
        await get_located(args.lat, args.long)
    elif args.get_sent_messages:
        ids = await get_sent_messages(args.days)
    elif args.delete_sent_messages:
        ids = await get_sent_messages(args.days)
        await delete_sent_messages(ids)


with client:
    print("Client created")
    client.loop.run_until_complete(main())
