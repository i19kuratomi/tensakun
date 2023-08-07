import difflib
import bs4


def compare(input_str: str, final: str):
    differ = difflib.HtmlDiff()
    table = differ.make_table(input_str.splitlines(), final.splitlines())
    soup = bs4.BeautifulSoup(table, "html.parser")
    # tbody = soup.find("tbody")
    return str(soup.tbody)


if __name__ == '__main__':
    input = """\
    僕は添削くんだ。貴社を希望するんだ。
    """
    final = """\
    僕は添削くんです。貴社を希望いたします。
    """
    print(compare(input, final))
