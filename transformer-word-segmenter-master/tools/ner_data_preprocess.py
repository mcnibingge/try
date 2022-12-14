import os
import re
import argparse

def print_process(process):
    num_processed = int(30 * process)
    num_unprocessed = 30 - num_processed
    print(
        f"{''.join(['['] + ['='] * num_processed + ['>'] + [' '] * num_unprocessed + [']'])}, {(process * 100):.2f} %")


def convert_to_bis(source_dir, target_path, log=False, combine=False, single_line=True):
    print("Converting...")
    for root, dirs, files in os.walk(source_dir):
        total = len(files)
        tgt_dir = target_path + root[len(source_dir):]

        print(tgt_dir)
        for index, name in enumerate(files):
            file = os.path.join(root, name)
            bises = process_file(file)
            if combine:
                _save_bises(bises, target_path, write_mode='a', single_line=single_line)
            else:
                os.makedirs(tgt_dir, exist_ok=True)
                _save_bises(bises, os.path.join(tgt_dir, name), single_line=single_line)
            if log:
                print_process((index + 1) / total)
    print("All converted")


def _save_bises(bises, path, write_mode='w+', single_line=True):
    with open(path, mode=write_mode, encoding='UTF-8') as f:
        if single_line:
            for bis in bises:
                sent, tags = [], []
                for char, tag in bis:
                    sent.append(char)
                    tags.append(tag)
                sent = ' '.join(sent)
                tags = ' '.join(tags)
                f.write(sent + "\t" + tags)
                f.write('\n')
        else:
            for bis in bises:
                for char, tag in bis:
                    f.write(char + "\t" + tag + "\n")
                f.write("\n")


def process_file(file):
    with open(file, 'r', encoding='UTF-8') as f:
        text = f.readlines()
        bises = _parse_text(text)
    return bises


def _parse_text(text: list):
    bises = []
    for line in text:
        # remove POS tag
        line, _ = re.subn('\\n', '', line)
        if line == '' or line == '\n':
            continue
        words = re.split('\s+', line)

        if len(words) > MAX_LEN_SIZE:
            texts = re.split('[????????????.?!,]/w', line)
            if len(min(texts, key=len)) > MAX_LEN_SIZE:
                continue
            bises.extend(_parse_text(texts))
        else:
            bises.append(_tag(words))
    return bises


def _tag(words):
    """
    ??????????????????????????????BIS??????
    :param line: ?????????
    :return:
    """
    bis = []
    # words = list(map(list, words))
    pre_word = None
    for word in words:
        pos_t = None
        tokens = word.split('/')
        if len(tokens) == 2:
            word, pos = tokens
        elif len(tokens) == 3:
            word, pos_t, pos = tokens
        else:
            continue

        word = list(word)
        pos = pos.upper()

        if len(word) == 0:
            continue
        if word[0] == '[':
            pre_word = word
            continue
        if pre_word is not None:
            pre_word += word
            if pos_t is None:
                continue
            elif pos_t[-1] != ']':
                continue
            else:
                word = pre_word[1:]
                pre_word = None

        if len(word) == 1:
            bis.append((word[0], 'S-' + pos))
        else:
            for i, char in enumerate(word):
                if i == 0:
                    bis.append((char, 'B-' + pos))
                elif i == len(word) - 1:
                    bis.append((char, 'E-' + pos))
                else:
                    bis.append((char, 'I-' + pos))
    # bis.append(('\n', 'O'))
    return bis


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="??????????????????????????????????????????BIS????????????????????????")
    parser.add_argument("corups_dir", type=str, help="?????????????????????????????????????????????????????????????????????????????????")
    parser.add_argument("output_path", type=str, default='.', help="??????????????????????????????????????????")
    parser.add_argument("-c", "--combine", help="???????????????????????????", default=False, type=bool)
    parser.add_argument("-s", "--single_line", help="?????????????????????", default=False, type=bool)
    parser.add_argument("--log", help="?????????????????????", default=False, type=bool)
    parser.add_argument("--max_len", help="???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????",
                        default=150, type=int)
    args = parser.parse_args()
    MAX_LEN_SIZE = args.max_len

    convert_to_bis(args.corups_dir, args.output_path, args.log, args.combine, args.single_line)
