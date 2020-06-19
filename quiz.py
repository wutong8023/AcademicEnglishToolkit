"""
Translating sentences into Chinese

Author: Tong
Time: 28-05-2020
"""
import json
import datetime
import random
import logging
import sys
from googletrans import Translator

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG,
                    datefmt='%m/%d/%Y %I:%M:%S')
# setup logger
log = logging.getLogger(__name__)

file_path = "./library/snippets"


class Snippet:
    def __init__(self, sentence, translation, time, tag):
        """
        snippet in En;
        snippet in Cn_zh;
        tag;
        time;
        """
        self.sentence = sentence
        self.translation = translation,
        self.time = time
        self.tag = tag


class Recorder:
    def __init__(self, file_name=file_path):
        """
        file_name;
        predefined_tag;
        """
        self.file_name = file_name
        self.tags = {
            "1": "Abstract",
            "2": "Introduction",
            "3": "Related_works",
            "4": "Method",
            "5": "Experiment",
            "6": "Discussion",
            "7": "Other"
        }
        self.translator = Translator()

    def __write(self, snippet_serialized):
        with open(self.file_name, "a") as database:
            database.writelines("\n")
            database.writelines(snippet_serialized)
        log.info("recorded successfully")

    def __record(self):
        log.info("______________________________________________________________________________")
        log.info("please input the snippet:")
        input_sentence = input()
        auto_translation = self.translator.translate(input_sentence, dest='zh-cn').text
        log.info("please check the suggested translation:")
        print(auto_translation)
        assert type(auto_translation) is str
        log.info("If correct -> \\Enter, otherwise - the manually modified translation:")
        input_translation = input()
        translation = auto_translation if input_translation is "y" or "Y" or "" else input_sentence
        log.info(self.tags)
        log.info("please input the tag id:")
        tag_id = input()
        tag = self.tags[tag_id] if tag_id in self.tags.keys() else "Other"
        time = str(datetime.date.today())

        snippet = Snippet(sentence=input_sentence, translation=translation, time=time, tag=tag)
        snippet_serialized = json.dumps(snippet.__dict__)
        if snippet.sentence is not "":
            self.__write(snippet_serialized)

    def record(self):
        log.info("Start recording:")
        flag = "="
        while flag is not "#":
            self.__record()
            log.info("______________________________________________________________________________")
            log.info("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            log.info("press any key except '#' to continue")
            flag = input()


class Quiz:
    def __init__(self, file_name=file_path, quiz_size=5, quiz_type="translate", sample_strategy="random",
                 metric_type="levenshtein"):
        self.file_name = file_name
        self.data = self.__load_data()
        self.quiz_size = quiz_size if quiz_size < len(self.data) else len(self.data)
        self.sample_strategies = {
            "random": self.__random_sampling
        }
        self.sample_strategy = self.sample_strategies[sample_strategy]

        self.quiz_types = {
            "translate": self.__translate_type
        }
        self.quiz_type = self.quiz_types[quiz_type]

        self.metric_types = {
            "levenshtein": self.__levenshtein_distance
        }
        self.metric_type = self.metric_types[metric_type]

    def __load_data(self) -> [Snippet]:
        data = []
        with open(self.file_name) as file_in:
            for line in file_in:
                data_point = json.loads(line)
                snippet = Snippet(
                    sentence=data_point["sentence"],
                    translation=data_point["translation"],
                    tag=data_point["tag"],
                    time=data_point["time"]
                )
                data.append(snippet)
        return data

    def __random_sampling(self) -> [Snippet]:
        # print(self.data)
        random.shuffle(self.data)
        temp_data = self.data[0: self.quiz_size]
        # print(type(temp_data))
        return temp_data

    def __translate_type(self, temp_data) -> [zip([str], [str])]:
        eng_li = []
        zh_li = []
        for snippet in temp_data:
            eng_li.append(snippet.sentence)
            zh_li.append(snippet.translation)
        return list(zip(eng_li, zh_li))

    def __generate_quiz(self):
        temp_data = self.sample_strategy()
        quiz_data = self.quiz_type(temp_data)
        temp_score = 0
        temp_num = 0

        for meta_question in quiz_data:
            # print(meta_question)
            log.info("______________________________________________________________________________")
            en = meta_question[0]
            zh = meta_question[1][0][0]
            temp_num += 1
            log.info(str(temp_num)+": "+zh)
            temp_score += self.__meta_test(en)

        log.info("Average Score: "+str(temp_score/temp_num))

    def start(self):
        log.info("______________________________________START________________________________________")
        self.__generate_quiz()
        log.info("_____________________________________FINISHED______________________________________")

    def __meta_test(self, en):
        log.info("your answer:")
        my_answer = input()
        score = self.__metric(my_answer, en)
        log.info("Score: "+str(score)+"\nExpected answer: "+en)
        return score

    def __metric(self, my_answer, expected_answer):
        score = self.metric_type(my_answer, expected_answer)
        # print(score)
        return score

    def __levenshtein_distance(self, my_answer, expected_answer) -> int:
        if not my_answer:
            return len(expected_answer or '') or 0
        if not expected_answer:
            return len(my_answer or '') or 0
        my_answer_size = len(my_answer)
        expected_answer_size = len(expected_answer)
        last = 0
        tmp = list(range(expected_answer_size + 1))
        levenshtein_distance = None
        for i in range(my_answer_size):
            tmp[0] = i + 1
            last = i
            # print word1[i], last, tmp
            for j in range(expected_answer_size):
                if my_answer[i] == expected_answer[j]:
                    levenshtein_distance = last
                else:
                    levenshtein_distance = 1 + min(last, tmp[j], tmp[j + 1])
                    # print(last, tmp[j], tmp[j + 1], value)
                last = tmp[j + 1]
                tmp[j + 1] = levenshtein_distance
            # print tmp
        return int(100 - levenshtein_distance / (my_answer_size + expected_answer_size) * 100)


if __name__ == '__main__':
    log.info("Press \\Enter to start record！")
    if input() is "":
        record = Recorder()
        record.record()
    log.info("Press \\Enter to start a quiz！")
    if input() is "":
        quiz = Quiz(quiz_size=3)
        quiz.start()


