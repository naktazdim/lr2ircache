lr2ircache
===
Simple [LR2IR (LunaticRave2 Internet Ranking)](http://www.dream-pro.info/~lavalse/LR2IR/search.cgi) Cache Server


## Usage

```sh
$ uvicorn lr2ircache.main:app
```

- `lr2ircache/` に `PYTHONPATH` を通しておくこと。

- 環境変数 `LR2IRCACHE_DB_URL` にデータベースの URL ( postgres://foo:example.com:5432/bar など ) を指定しておくこと。