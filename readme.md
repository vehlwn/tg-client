# tg-client

Simple console Telegram client.

## Examples

```bash
# Example api_id.ini:
$ cat api_id.ini
[general]
api_id=10050036
api_hash=1rp690rns112n78s361468s16r100s2o224
username=vehlwn

$ python main.py --print-me
$ python main.py --get-messages --chat-id=-88005553535 --limit=10
$ python main.py --send-message --chat-id=me --text=hello
$ python main.py --delete-messages --chat-id=me --from-user=me --limit=5
$ python main.py --get-located --lat=55.74618 --long=37.613266
$ python main.py --get-sent-messages --days=30
$ python main.py --delete-sent-messages --days=30
```
