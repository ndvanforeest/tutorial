import os
import re

import numpy as np


def weighted_choice(weights, gen):
    """Select the index of an array of weights, proportional to
    the weights in the array weights."""
    rnd = gen.uniform() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i


def weighted_sample(a, w, k, gen):
    """Get k samples without replacement from a in which each element is selected
    according to the weights in w."""
    if len(a) != len(w):
        raise ValueError("The Lenghts of lists don't match.")

    w = list(w)  # make a copy of w
    r = []  # contains the random shuffle
    for i in range(k):
        j = weighted_choice(w, gen)
        r.append(a[j])
        w[j] = 0
    return r


def make_title_page(
    course,
    code,
    year,
    authors,
    lecture_week,
    date_of_test,
):
    return [
        r"\title{",
        rf"{course} {year}\\",
        rf"{code}\\",
        rf"Lecture week {lecture_week}\\",
        f"{date_of_test}",
        "}",
        r"\author{",  # finish tilte
        "\\\\\n".join(author for author in authors),
        "}",  # finish authors
        r"\date{}",
    ]


readme_page = [
    r"\begin{enumerate}",
    r"\item  Recall: If you think that: `Claim: 3 + 5 = 9' is True, choose $A$",
    r"on the answer form; if you think is it False choose $B$.",
    r"Otherwise, just leave it open, or fill in $C$.",
    r"\item True/False: Have you put your mobile, laptop, book, other printed material in your bag? Hopefully it's a YES!",
    r"\item You are allowed to discuss with your fellow students, but don't scream; keep the discussion decent.",
    r"\item You are responsible for your own answer.",
    r"\item You have three minutes per question.",
    r"\item In the second hour of the tutorial we'll discuss the answers.",
    r"\end{enumerate}",
]


def make_latex_footer():
    return [
        r"\end{document}",
    ]


def extract_truefalse_problems(filename, gen):
    problems = []
    with open(filename, "r") as fp:
        content = fp.read()

    # We want to skip commented true false questions. Hence, skip if \begin{truefalse}
    # does not appear at the start of a line.
    pattern = r"(?m)^\\begin{truefalse}(.*?)\\end{truefalse}"
    matches = re.findall(pattern, content, re.DOTALL)
    for exercise in matches:
        problem = "\\begin{truefalse}"
        # problem += "\\Large"
        """Force a random solution. I adapt the problem occordingly
        after the test is generated."""
        answer = "\nA (True).\n" if gen.uniform() > 0.5 else "\nB (False).\n"
        bg = "\\begin{solution}"
        problem += exercise.replace(bg, bg + answer)
        problem += "\\end{truefalse}\n\n"
        # problem += "\\clearpage\n"
        problems.append(problem)
    return problems


def make_tutorial_test(
    course,
    code,
    year,
    authors,
    lecture_week,
    date_of_test,
    preamble_file,
    private_seed,
    week_schedule,
    num_problems=10,
    overwrite=False,
):
    gen = np.random.default_rng(private_seed + lecture_week)

    all_problems = []
    weights = []
    """Select TF exercises from material of the weeks before the lecture week.
    So, up to, but not including the lecture week."""
    for week in range(1, lecture_week):
        for filename in week_schedule[week]:
            print(filename)
            problems = extract_truefalse_problems(filename, gen)
            all_problems += problems
            weights += [week] * len(problems)
    selected_problems = weighted_sample(
        all_problems, weights, num_problems, gen
    )

    questions_file = f"tf-{lecture_week}-questions.tex"
    # Protect myself from overwriting the file without knowing it.
    # Delete the existing file explicity if necessary.
    if os.path.exists(questions_file) and not overwrite:
        raise FileExistsError(f"{questions_file} already exists.")

    with open(questions_file, "w", encoding='utf-8') as fp:
        text = [
            rf"\documentclass[tf-{lecture_week}-answers]{{subfiles}}",
            r"\begin{document}",
        ]
        for i, problem in enumerate(selected_problems):
            text.append(f"% Problem {i+1}")
            text.append(problem)
        text.append(r"\end{document}")
        fp.write("\n".join(t for t in text))

    title_page = make_title_page(
        course,
        code,
        year,
        authors,
        lecture_week,
        date_of_test,
    )

    with open(f"tf-{lecture_week}-test.tex", "w", encoding='utf-8') as fp:
        text = [
            r"\documentclass{article}",
            r"\usepackage[nosolutions]{optional}",
            rf"\usepackage{{{preamble_file}}}",
            r"\usepackage[a5paper,landscape]{geometry}",
            r"\usepackage{anyfontsize}",
            r"\linespread{1.3}",
        ]
        text += title_page
        text += [
            r"\AtEndEnvironment{truefalse}{\clearpage}",
            r"\begin{document}",
            r"\maketitle",
            r"\clearpage",
            r"\fontsize{15}{15}",
            r"\selectfont",
        ]
        text += readme_page
        text += [
            r"\clearpage",
            r"\fontsize{25}{25}",
            r"\selectfont",
            rf"\subfile{{tf-{lecture_week}-questions.tex}}",
        ]
        text += make_latex_footer()
        fp.write("\n".join(t for t in text))

    with open(f"tf-{lecture_week}-answers.tex", "w", encoding='utf-8') as fp:
        text = [
            r"\documentclass[a4paper,12pt]{article}",
            r"\usepackage[check]{optional}",
            rf"\usepackage{{{preamble_file}}}",
            r"\usepackage{a4wide}",
        ]
        text += title_page
        text += [
            r"\begin{document}",
            r"\maketitle",
        ]
        text += readme_page
        text.append(rf"\subfile{{tf-{lecture_week}-questions.tex}}")
        text += make_latex_footer()
        fp.write("\n".join(t for t in text))
