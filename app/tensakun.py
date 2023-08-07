import MeCab
import sys
import csv
import difflib
import re
from rules import *
from keigo import *

sentence = []
genkei = []
katuyo = []
hinshi = []

# 変換表
# 辞書型 {key, value}


# 助動詞の活用
jodoshi = ["せる", "させる", "れる", "られる", "がる"]

# //////////////// Mecabで形態素解析する関数 /////////////////////////////////////////////////////////////////// #

def mecab(task):
    tagger = MeCab.Tagger("-Owakati")  # 単語の間に [, ]

    tagger.parse('')  # パーサーにデータを渡す前にこれを挟むことで、UnicodeDecodeErrorを避けることが出来る。

    # nodeにsurface(単語)feature(品詞情報)を持つ解析結果を代入
    # node.surface/node.featureでそれぞれにアクセス出来る
    # node.feature部分のデータ構造 ➝ 品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
    node = tagger.parseToNode(task)

    sentence = []  # 原文を単語に区切ったリスト
    genkei = []  # それぞれの単語の原型
    katuyo = []  # 単語の活用形
    hinshi = []  # 単語の品詞

    # 全ての単語を1つずつ解析
    while node:
        word = node.surface  # 単語情報
        wclass = node.feature.split(',')  # データ構造を , ごとにリスト化

        # BOS 文頭、EOS 文末
        if not wclass[0] == "BOS/EOS":
            sentence.append(word)
            genkei.append(wclass[7])  # 7
            katuyo.append(wclass[5])  # 4か5
            hinshi.append(wclass[0])

        node = node.next  # 次の単語へ

    return sentence, genkei, katuyo, hinshi


# //////////////// 指定された活用形の動詞を検索する関数 //////////////////////////////////////////////////// #

def kensaku(hinsi, word, katuyokei):
    if hinsi == "動詞":
        file_name = "Verb.csv"
    elif hinsi == "助動詞":
        file_name = "Auxil.csv"
    else:
        sys.exit()

    # file_nameを読み込みモードで開く
    f = open(file_name, 'r')
    dataReader = csv.reader(f)

    # リストdataReaderの要素をrowに取り出して検索
    # Verd.csvを一行ずつ取り出し

    for row in dataReader:  # 1行ずつrowに読み出し
        if word == row[10]:  # 添え字10　動詞、助動詞の原形
            if katuyokei == row[9]:  # 添え字 9  動詞、助動詞の活用形
                print(row[0])
                return row[0]  # 原型を活用した状態を返す
    return None


# ////////////////// 活用形をタ接続,ウ接続に変換する関数 ///////////////////////////////////////////////////// #

def henkan(keigo, hinsi, katuyokei, num, sentence):
    result = mecab(keigo)
    print()
    print("敬語に直した動詞")
    print(result)

    tango = result[0]  # ['カレー', 'を', '食べる']
    print(tango)
    a = tango[-1]  # 1番後ろの要素
    print(a)

    # 指定された活用形の動詞を検索する
    new_result = kensaku(hinsi, a, katuyokei)

    if len(sentence) > num + 1:
        if sentence[num + 1] == "う":  # 動詞の後ろが「う」なら
            if "ウ接続" in katuyokei:
                if new_result == None:
                    katuyokei = katuyokei.strip("ウ接続")
            else:
                katuyokei = katuyokei.strip("形") + "ウ接続"
                if kensaku(hinsi, a, katuyokei) == None:  # 敬語をウ接続した形がなかったら, 元の活用形に戻す
                    katuyokei = katuyokei.strip("ウ接続") + "形"

        if sentence[num + 1] == "た" or sentence[num + 1] == "て":  # 動詞の後ろが「た」「て」なら
            if "タ接続" in katuyokei:
                if new_result == None:
                    katuyokei = katuyokei.strip("タ接続")
            else:
                katuyokei = katuyokei.strip("形") + "タ接続"  # 例:連用タ接続
                print(katuyokei)

                if kensaku(hinsi, a, katuyokei) == None:  # 敬語をタ接続した形がなかったら, 元の活用形に戻す
                    katuyokei = katuyokei.strip("タ接続") + "形"

    final_result = (kensaku(hinsi, a, katuyokei))
    print()
    print("final")
    print(final_result)

    if not final_result == None:
        tango[-1] = final_result

    semifinal = ""
    for a in tango:
        semifinal = semifinal + a

    return semifinal


# /////////////////// 句点句読点を変換する関数 /////////////////////////////////////////////////////////////// #

def Full_Half(flag, text):
    num = -1  # 0から始めるため
    # --------------- 前処理：半角 ➝ 全角 （形態素解析が通らないから）- ------------ #
    if flag == 0:
        text = text.replace(' ', '')  # 文字列から半角空白を削除
        text = text.replace('　', '')  # 全角空白
        text_list = list(text)  # 文字列をリスト化

        for key in text_list:
            num = num + 1
            if key in han_zen_rules.keys():
                text_list[num] = han_zen_rules[key]

        text = ''.join(text_list)

    # ---------------- 後処理：全角 ➝ 半角 ----------------------------------- ------ #
    if flag == 1:
        for key in text:
            num = num + 1
            if key in zen_han_rules.keys():
                text[num] = zen_han_rules[key]

    # ------------------------------------------------------------------------------- #
    return text


# /////////////////  数字を処理する関数  /////////////////////////////////////////////////////////////////// #

def Num_con(flag, text):
    num = -1  # 0から始めるため
    # --------------- 半角数字　➝　漢数字 -------------------------------------------- #
    if flag == 0:
        for key in text:
            num = num + 1
            if key in suji_han.keys():
                text[num] = suji_han[key]  # text は text_list

        text = ''.join(text)

    # --------------- 漢数字　➝　半角数字 -------------------------------------------- #
    if flag == 1:
        for key in text:
            num = num + 1
            if key in suji_zen.keys():
                text[num] = suji_zen[key]  # text は sentence

    # ------------------------------------------------------------------------------- #
    return text


# /////////////////  補助記号を削除する関数  //////////////////////////////////////////////////////// #

def delete(sentence, hinshi):
    num = -1
    for hinshi_word in hinshi:
        num = num + 1
        if hinshi_word == "補助記号":
            # 記号はsentenceで半角になる
            if not ((sentence[num] == "、") or (sentence[num] == "。") or (sentence[num] == "!") or (
                    sentence[num] == "?")):
                sentence[num] = ''

    print("余計なものをのけたやつ↓")
    print(sentence)

    return sentence


# /////////////////  する　の原形verを変更する関数  //////////////////////////////////////////////////////// #
# 「する」の 連用の活用形をVerd.csvで変更　42399行目：連用形「する」➝「し」(初期のVerd.csvでは「する」の変換が古いため) 

def do(genkei):
    for num in range(len(genkei)):  # 0~len(genkei)
        if genkei[num] == "為る":
            genkei[num] = "する"
            print("変更")

    return genkei


# /////////////////  文末「だ」➝「た」にする関数  //////////////////////////////////////////////////////////// #

def da(sentence):
    if sentence[-2] == "だ":
        sentence[-2] = "た"

    return sentence


# /////////////////  丁寧語があるか確認する関数  //////////////////////////////////////////////////////// #

def check(sentence, hinshi):
    num = -1  # 1番後ろは「。」
    # ---------------- すでに「ます」がついているか確認 ➝　添削終了 ------------------- #
    if (sentence[num - 1] == "ます") or (sentence[num - 2] == "まし"):
        return 1, sentence

    # ---------------- すでに「です」がついているか確認 ➝　添削終了 ------------------- #
    if (sentence[num - 1] == "です") or (sentence[num - 2] == "でし"):
        return 1, sentence

    # ---------------- すでに「たい」についているか確認　➝　「です」を追記 ------------ #
    if (sentence[num - 1] == "たい"):
        sentence.insert(-1, "です")  # 末尾に追加
        return 1, sentence

    # --------------- 品詞に動詞がなかった場合　➝　「です」を追記 --------------------- #
    if (hinshi[num - 1] == "名詞") or (hinshi[num - 1] == "形状詞") or (hinshi[num - 1] == "形容詞"):
        sentence.insert(-1, "です")  # 末尾に追加
        return 1, sentence
        # final = "".join(sentence)
        # print(final)
        # exit()

    return 0, sentence  # 上記以外なら丁寧語なし


# /////////////////  文中の助動詞「だ」➝「です」に変換する関数  ///////////////////////////////////////////// #

# 社長はテレビが好き➝そのまま、好きだ➝好きですになる
def desu(sentence, genkei, hinshi, katuyo):
    num = -2

    if genkei[num] == "だ":
        if hinshi[num] == "助動詞":
            katuyokei = katuyo[num]
            result = henkan("です", "助動詞", katuyokei, num, sentence)
            sentence[num] = result

    return sentence


# /////////////////  文末を助動詞「ます」を追記する関数  //////////////////////////////////////////////////////////// #

def masu(sentence, genkei, hinshi, katuyo):
    # 助動詞のリストを用いて、文末の単語が[ます]を接続できる助動詞か動詞か判定し、その単語をaとする
    # 「ます」は連用形に接続する➝aを連用形にして「ます」をaの活用形にあわせて付け加える

    num = len(genkei)
    for a in reversed(genkei):  # 後ろから原型をaに格納
        num = num - 1
        if a == "ます":
            num = num - 1
        if a == "です":
            num = num - 1

        if (genkei[num] != "ます") and (genkei[num] != "です"):  # 2重敬語の防止
            if genkei[num] in jodoshi:  # 「ます」の前の単語が助動詞なら活用形を連用形にする
                result = kensaku("動詞", a, "連用形")
                sentence[num] = result

                katuyokei = katuyo[num]
                katuyokei = katuyokei[:3]
                result = henkan("ます", "助動詞", katuyokei, num, sentence)  # keigo = ます 「ます」は助動詞の活用形を適用
                sentence.insert(num + 1, result)  # 最後に(num + 1)の位置に「ます」を活用したresultを追加
                break

            if hinshi[num] == "動詞":
                result = kensaku("動詞", a, "連用形")
                print(a)
                print("変換")
                print(result)
                sentence[num] = result

                katuyokei = katuyo[num]
                katuyokei = katuyokei[:3]
                result = henkan("ます", "助動詞", katuyokei, num, sentence)
                sentence.insert(num + 1, result)
                break

    return sentence


# ////////////////////  main  ////////////////////////////////////////////////////////////////////////////// #

def main(text, keigo, FtoH_flag):
    # 数字がある判断 0: なし 1: あり
    Num_flag = 0

    # 処理フラグ  0: 前処理 1:後処理
    proc = 0

    # 改行は？？？？？？？？？？？？
    text = text.replace('　', '')  # 全角空白を削除

    # ---------------------- 0: 半角➝全角 （半角の場合：形態素解析が通らないから ----------------------------- #

    if FtoH_flag == 0:
        text = Full_Half(FtoH_flag, text)

    # ---------------------- 数字がある処理1（半角数字➝漢数字)　!半角の場合：形態素解析が通らないから! --------- #
    # 漢数字はそのままで出力

    text_list = list(text)
    for key in text_list:
        if key in suji_han.keys():
            Num_flag = 1
            text = Num_con(proc, text_list)  # proc = 0

    # ---------------------- 形態素解析 ----------------------------------------------------------------------- #

    result = mecab(text)  # 文章を形態素解析
    sentence = result[0]
    genkei = result[1]
    katuyo = result[2]
    hinshi = result[3]

    print(sentence)
    print(genkei)
    print(katuyo)
    print(hinshi)

    # ---------------------- 補助記号を削除 (、。！？ 以外)-------------------------------------------------------------------- #

    sentence = delete(sentence, hinshi)

    # ---------------------「する」の原形verを変更 (初期のVerd.csvでは「する」の変換が古いため) ------------------- #

    genkei = do(genkei)

    # ----------------------- 文章中の単語 ➝ 敬語verの検索 & 変換 ---------------------------------------------- #

    # 謙譲語の処理
    if keigo == 0:
        num = -1
        for genkei_word in genkei:  # 全単語
            num = num + 1
            if genkei_word in kenjogo.keys():
                katuyokei = katuyo[num]
                keigo = kenjogo[genkei_word]
                hinsi = hinshi[num]

                katuyokei = katuyokei[:3]  # 「-一般」を消す
                result = henkan(keigo, hinsi, katuyokei, num, sentence)  # 原形の動詞を, 元の文章の活用形に変換 + タ活用,ウ活用に変換

                sentence[num] = result  # 変換した動詞を挿入

    # 尊敬語の処理
    if keigo == 1:
        num = -1
        for genkei_word in genkei:  # 全単語
            num = num + 1
            if genkei_word in sonkeigo.keys():
                katuyokei = katuyo[num]
                keigo = sonkeigo[genkei_word]
                hinsi = hinshi[num]

                katuyokei = katuyokei[:3]  # 「-一般」を消す
                result = henkan(keigo, hinsi, katuyokei, num, sentence)  # 原形の動詞を, 元の文章の活用形に変換 + タ活用,ウ活用に変換

                sentence[num] = result  # 変換した動詞を挿入

    # ---------------------------------------------------------------------------------------------------------- #

    semifinal = "".join(sentence)  # sentenceの単語を全て結合
    print("semifinal ↓")
    print(semifinal)

    # ---------------------- 丁寧語に直す処理 ------------------------------------------------------------------ #

    result = mecab(semifinal)  # 再び形態素解析

    sentences = result[0]
    genkeis = result[1]
    katuyos = result[2]
    hinshis = result[3]

    print(sentences)
    print(genkeis)
    print(katuyos)
    print(hinshis)

    # ---------------- する　の原形verを変更 ------------------------------ #

    genkeis = do(genkeis)

    # ------------------------------------------------------------------------------------------- #

    # 文の数
    e_num = 0
    first = 0
    end = 0
    check_flag = 0  # すでに添削済みか？　  0: 未　1: 済
    sentence = []  # sentence 初期化

    num = -1  # 0から始めるため
    for i, e in enumerate(sentences):  # 全単語
        if e == "。":  # 「。」ごとに処理区切る
            end = i +  1  # スライスのため +1

            semi_sentence = sentences[first:end]
            genkei = genkeis[first:end]
            katuyo = katuyos[first:end]
            hinshi = hinshis[first:end]

            e_num = e_num + 1
            first = end  # 前の文の終わりから

            check_flag, semi_sentence = check(semi_sentence, hinshi)

            if check_flag == 1:
                pass
            elif check_flag == 0:
                semi_sentence = desu(semi_sentence, genkei, hinshi, katuyo)  # 「だ」➝「です」
                semi_sentence = masu(semi_sentence, genkei, hinshi, katuyo)  # 「ます」
                semi_sentence = da(semi_sentence)  # 語尾「だ」➝「た」

            print(e_num)
            print(semi_sentence)

            sentence.extend(semi_sentence)  # 文章を結合
            print(sentence)

    # 後処理
    proc = 1

    # --------------------- 全角➝半角 ----------------------------------------------------------------------- #

    if FtoH_flag == 1:
        sentence = Full_Half(FtoH_flag, sentence)

    # ---------------------- 数字がある処理2 (漢数字➝半角数字) ----------------------------------------------- #

    if Num_flag == 1:
        sentence = Num_con(proc, sentence)

    # ---------------------- 否定のます「ない」➝「ん」 ------------------------------------------------------- #

    num = -1
    for key in sentence:
        num = num + 1
        if key == "ない" or "ん" or "ぬ":
            if sentence[num - 1] == "ませ":
                sentence[num] = "ん"

    # ---------------------------------------------------------------------- #

    final = "".join(sentence)

    return final


# ------------textに入っている複数の文章を「。」or「.」ごとに区切ってリストs_textに格納----------- 
def split_t(text):
    # textを。ごとに区切って分割　text.stripはtextの先頭と末尾にある空白を削除　splitは文章を。で区切る　文ごとのリストs_textが作成
    s_text = re.split(r"[。.]", text.strip())

    # 最後の要素が空文字列の場合、削除
    if s_text[-1] == '':
        s_text = s_text[:-1]
    return s_text


# ------------finalに入っている複数の文章を「。」or「.」ごとに区切ってリストs_finalに格納-----------
def split_f(final):
    # finalを。ごとに区切って分割　final.stripはfinalの先頭と末尾にある空白を削除　splitは文章を。で区切る　文ごとのリストs_finalが作成
    s_final = re.split(r"[。.]", final.strip())

    # 最後の要素が空文字列の場合、削除
    if s_final[-1] == '':
        s_final = s_final[:-1]
    return s_final


# -------------s_textに含まれている文章を1つずつ取り出して単語ごとに分割しlist_textに代入-------------
def tango_bunkatu_text(s_text):
    tagger = MeCab.Tagger("-Owakati")
    text_list = [s_text]
    list_text = []
    for text_item in text_list:
        tango_text = tagger.parse(text_item).strip()
        list_text = tango_text.split(' ')

    return list_text


# ------------s_finalに含まれている文章を1つずつ取り出して単語ごとに分割しlist_finalに代入------------
def tango_bunkatu_final(s_final):
    tagger = MeCab.Tagger("-Owakati")
    final_list = [s_final]
    list_final = []
    for text_item in final_list:
        tango_final = tagger.parse(text_item).strip()
        list_final = tango_final.split(' ')

    return list_final


# ------------単語で区切られたlist_text,list_finalの変更部分を抜き取る------------
def diff_word(list_text, list_final):
    differ = difflib.ndiff(list_text, list_final)
    diffwords = []
    # 差分の単語を取得
    for word in differ:
        # 差分の情報が削除された単語を取得
        if word.startswith('- '):
            # 差分の情報をdiffwordsリストに追加([2:]文字列の先頭の2文字(- )を抜いた位置)
            diffwords.append(word[2:])
            # 差分の情報が追加された単語を取得
        elif word.startswith('+ '):
            diffwords.append(word[2:])
    return diffwords


# ------------textのどの部分がfinalと違うのかを調べる(resultとtextを比較して一致する単語を出力)------------
def compare_text_diffwords(list_text, r):
    diffwords_in_text = []
    for text_list in list_text:
        listsetext = text_list.split(' ')
        for word in listsetext:
            if word in r:
                diffwords_in_text.append(word)
    return diffwords_in_text


# ------------finalのどの部分がtextと違うのかを調べる(resultとfinalを比較して一致する単語を出力)------------
def compare_final_diffwords(list_final, r):
    diffwords_in_final = []
    for final_list in list_final:
        listsefinal = final_list.split(' ')
        for word in listsefinal:
            if word in r:
                diffwords_in_final.append(word)
    return diffwords_in_final


def error(text, final):
    result = []
    for s_text, s_final in zip(split_t(text), split_f(final)):
        position = ""
        list_text = tango_bunkatu_text(s_text)
        list_final = tango_bunkatu_final(s_final)
        r = diff_word(list_text, list_final)
        text_i = 1
        final_i = 1
        if (r) and (r[0] != "です"):
            msg1 = text;
            dif1 = msg1.find(r[0])
            dif1 = dif1 + 1
            # 何行目か(1行20文字までしか入力できないとして)
            while dif1 > 0:
                if dif1 < 20:
                    print(text_i, "行", dif1, "文字目")
                    position = f"{text_i}行 {dif1}文字目"
                    dif1 = dif1 - 20
                else:
                    text_i = text_i + 1
                    dif1 = dif1 - 20

            # ------------list_textとresultを比較して位置した単語をsame_words1に------------
            same_words1 = compare_text_diffwords(list_text, r)
            same_text = "".join(same_words1)
            same_words2 = compare_final_diffwords(list_final, r)
            same_final = "".join(same_words2)
            print(same_text, "→", same_final)
            result.append({"change": f"{same_text} → {same_final}", "position": position})


        elif (r) and (r[0] == "です"):
            msg2 = final;
            dif2 = msg2.find("です")
            dif2 = dif2 + 1
            while dif2 > 0:
                if dif2 < 20:
                    print(final_i, "行", dif2, "文字目")
                    dif2 = dif2 - 20
                else:
                    final_i = final_i + 1
                    dif2 = dif2 - 20
            print("末尾に「です」を追加しました。")
            result.append({"message": "末尾に「です」を追加しました。"})

    return result


if __name__ == "__main__":
    # 添削する文章
    text_0 = "校長先生は食べた。"
    text = "校長先生は食べた。"

    # 0: 謙譲語　1: 尊敬語
    keigo = 0

    # 0: 半角➝全角　1: 全角➝半角
    FtoH_flag = 0

    final = main(text, keigo, FtoH_flag)
    print(text_0)
    print("↓")
    print(final)
    Error = error(text, final)

"""
半角から全角に変換
https://github.com/yaki-sa/ts-node-mecab

https://qiita.com/yaki-sa/items/c2bad44f3e94f71c093c

"""
