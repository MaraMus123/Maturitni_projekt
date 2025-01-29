def proccess_marks(marks: dict) -> dict:
    """Process the marks from the API.
    Args:
        marks (dict): The marks from the API.

    Returns:
        dict: The processed marks.
    """
    vysvedceni = {}
    weighted_mark = 0
    for subject in marks["Subjects"]:
        citatel = 0
        jmenovatel = 0
        if float(subject["AverageText"].strip().replace(",", ".")) >= 1.5:
            for mark in subject["Marks"]:
                weight = mark["Weight"]
                mark = mark["MarkText"]
                if "-" in mark:
                    mark = mark.replace("-", ".5")
                if mark == "N" or mark == "X":
                    continue
                mark = float(mark)
                jmenovatel += weight * mark
                citatel += weight
            weighted_mark = (jmenovatel, citatel)
        else:
            weighted_mark = 0
        vysvedceni[subject["Subject"]["Name"]] = (subject["AverageText"], weighted_mark)
    return vysvedceni

def calculate_what_do_I_need_to_improve(fraction: tuple):
    """Calculate what mark do I need to improve the subject.
    Args:
        fraction (tuple): A tuple containing the weighted mark and the weight.

    Returns:
        
    """
    current_mark = fraction[0] / fraction[1]
    marks = {}
    for i in range(round(current_mark) - 1):
        marks[i + 1] = []
        for j in range(i + 1):
            wanted_mark = i + 1 + 0.49       
            weight = (wanted_mark * fraction[1] - fraction[0]) / ((j + 1) - wanted_mark)
            marks[i + 1].append((j + 1, round(weight)))
    return marks

calculate_what_do_I_need_to_improve((24.3, 7))