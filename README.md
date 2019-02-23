# raspi_FcTronto
- ラズパイ側プログラム
- 主に以下の処理を行う
  - カメラから取得した画像を解析
  - シリアル通信で取得した各センサの値および画像処理結果を用いてモータの値を計算
  - モータの値をシリアル通信で送信
  - webサーバを起動し、webブラウザからの入力を処理する

## 必要部品
- <a href="http://akizukidenshi.com/catalog/g/gM-11425/" target="_blank">RaspberryPi3 Model B</a>
- <a href="http://akizukidenshi.com/catalog/g/gM-11425/" target="_blank">Raspberry Pi Camera Module V2</a>
- <a href="http://akizukidenshi.com/catalog/g/gM-11425/]" target="_blank">3.5インチTFT LCD ディスプレイ</a>
- microSDカード(ラズパイOSインストール用)

## プログラム全体構成図
- データフローと処理フローがごちゃごちゃになっているが以下のような感じ
    
![component.jpg](https://github.com/FC-TRONTO/raspi_FcTronto/blob/master/pic/component.jpg)

## モータ制御パラメータ設定の説明
- 現状以下の設定ファイルが存在する
  - /webiopi/goal_mode.txt
  - /webiopi/motor_setting.txt
  - /webiopi/parameter.ini
- それぞれのファイルに関する説明は以下の通り
  - /webiopi/goal_mode.txt
    - シュートするゴールの色の設定
      - 現在は'yellow'または'blue'
  - /webiopi/motor_setting.txt
    - モータ値の特殊設定
      - 現在はモータ停止設定のみ存在
      - ファイルの中身が'STOP'の場合はモータ値を0, 0固定にする
  - /webiopi/parameter.ini
    - モータ値計算用のパラメータ設定
      - 以下のパラメータを設定でき、それぞれ以下の変数に対応している

        |パラメータ名|変数名|
        |---|---|
        |shoot_algo|DEBUG_SHOOT_ALGORITHM|
        |chase_algo|DEBUG_CHASE_ALGORITHM|
        |shoot_speed|SPEED_SHOOT|
        |k_shoot_angle|K_SHOOT_ANGLE|
        |chase_speed|SPEED_CHASE|
        |k_chase_angle|K_CHASR_ANGLE|
        |center_speed|SPEED_GO_CENTER|
        |k_center_angle|K_GO_CENTER_ANGLE|
    - configparserモジュールを使って書き込み読み込みをしている
      - configparserについては下記公式ドキュメント参照
        - https://docs.python.jp/3/library/configparser.html
      - python2とpython3でモジュール名が異なることに注意
        - python2 -> ConfigParser, python3 -> configparser

## シリアル通信部分の説明
- 主にラズパイ側の視点から説明する
### マインドストーム→ラズパイ
- ラズパイ側は常にマインドストーム側からのデータ転送を受け付けている
- マインドストームがデータを送信したら、改行コードが送られるまでひとまとまりのデータとして受信する
- データのフォーマットは以下の通り
  - (int)[ボールとの角度],(float)[距離センサの値]\n
    - 現在は2つのデータを受け取る形にしている
    - 1つ目の数値はボールとの角度、2つ目の数値は距離センサの値
    - 例えばボールとの角度が60度、距離センサの値が0.38だったら"60,0.38\n"というデータが来る
      - ちなみにIRシーカーを前向きにつけていたら角度の値は左方向が正、右方向が負になる
- 送られてきたデータは共有メモリshmemに格納される
  - 共有メモリshmemは以下の要素をもつ
    - irAngle : ボールとの角度(int)
    - uSonicDis : 距離センサの値(float)
  - 送られてきたデータを確認したい場合は以下のようにコードを書けばOK
    - hoge = shmem.irAngle
    - fuga = shmem.uSonicDis
  - 共有メモリshmemの生成はmain.pyで行っており、各プロセスを起動する際に引数の形で子プロセスに渡している
### ラズパイ→マインドストーム
- ラズパイ側はいつでもマインドストーム側にデータを送ることができる
  - ただし複数プロセス・スレッドが同時に送信処理を行うとエラーになる、たぶん
- ラズパイがデータを送信したら、改行コードが送られるまでひとまとまりのデータとして扱われる
- データのフォーマットは以下の通り
  - (int)[-100-100],(int)[-100-100]\n
    - 現在は2つのデータを送る形にしている
    - 1つ目の数値は左モータの速度、2つ目の数値は右モータの速度
    - 例えば"-100,100\n"という値を送れば全力で左旋回する
- データ送信処理はSerialControllerクラスのメソッドとして実装されている
  - データ送信を行いたい場合は以下のようにコードを書けばOK
    - serial.write("foo,bar\n")
  - SerialControllerインスタンスの生成はmain.pyで行っており、各プロセスを起動する際に引数の形で子プロセスに渡している
    - 今はmotorContl.pyはserialという名前でSerialControllerインスタンスを受け取っている

## WebIOPi関係の説明
- WebIOPiの設定方法については以下参考
  - https://dev.classmethod.jp/hardware/raspberrypi/python-script-in-raspberry-pi/
- 起動時にwebブラウザを自動で全画面表示させるため、以下の設定が必要
  1. マウスがしばらく動いていないと、マウスカーソルの表示を消すツール`unclutter`を入れる
      ```
      sudo apt-get install unclutter
      ```
  2. `/etc/xdg/lxsession/LXDE/autostart`を以下のように編集
        ```
        @lxpanel --profile LXDE-pi
        @pcmanfm --desktop --profile LXDE-pi
        @xscreensaver -no-splash
        -@point-rpi

        +@xset s off
        +@xset -dpms
        +@xset s noblank
        +@unclutter
        +@chromium-browser --noerrdialogs --kiosk --incognito http://localhost/
        ```
  - 参考ページ
    - http://klee-arc.hatenablog.com/entry/2017/06/12/041200
    - https://qiita.com/yyano/items/c08705994363b9526d07
    - http://goldenmilk.hatenablog.com/entry/2017/05/21/212016