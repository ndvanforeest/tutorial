import pandas as pd
from sigfig import round


class Tutorial:
    def __init__(self, answer_key, filename, date, name, course):
        self.answer_key = answer_key
        self.filename = filename
        self.name = name
        self.date = date
        self.course = course
        self.num_valid_questions = sum(
            1 for v in answer_key.values() if v != "-"
        )
        self.make_dataframe()

    def make_dataframe(self):
        # Make a dataframe with a Username, the points per question,
        # the score (= total number of points) and the grade
        df = pd.read_excel(self.filename)
        df['score'] = df[range(1, 11)].apply(
            lambda row: self.score(row), axis=1
        )
        df['grade'] = df["score"].apply(lambda row: self.grade(row))
        df['Username'] = df['student'].apply(lambda x: f's{x}')
        del df["student"]
        duplicate_rows = df[df.duplicated('Username', keep=False)]
        if not duplicate_rows.empty:
            print(duplicate_rows)
            quit()
        self.df = df

    def score(self, answers):
        tot = 0
        for i, answer in enumerate(answers, 1):
            tot += self.score_question(i, answer)
        return tot

    def score_question(self, index, answer):
        correct_answer = self.answer_key[index]
        if correct_answer == "-":
            return 0
        if answer == correct_answer:
            return 1
        if answer == 1 and correct_answer == 2:
            return -1
        if answer == 2 and correct_answer == 1:
            return -1
        return 0.1

    def grade(self, score):
        grade = max(1.0, 10 * score / self.num_valid_questions)
        return round(grade, sigfigs=2)

    def stats(self):
        for i in range(1, 11):
            res = self.df[i].apply(lambda row: self.score_question(i, row))
            correct = (res == 1).sum()
            wrong = (res == -1).sum()
            unsure = (res == 0.1).sum()
            print(f"{i=}: {correct=}, {wrong=}, {unsure=}")
