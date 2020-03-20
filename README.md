# ポケモン徹底攻略育成論チェッカー
[ポケモン徹底攻略](https://yakkun.com)の注目の育成論の新規投稿をSlackへ通知する [AWS Lambda](https://aws.amazon.com/lambda/) 用の関数です。

# 使用方法
このリポジトリをクローンします。
```
git clone https://github.com/tkazusa/poketetsu-checker.git
```

関数と必要な Python モジュールを zip ファイルに固めます。
```
> mkdir upload
> cd upload
> pip install requests_html --system -t lib/
> cp ../src/lambda_scraping.py .
> zip -r zip_file ./*
```

zip ファイルを AWS Lambda の関数としてアップロードして活用します。
