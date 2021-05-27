from bs4 import BeautifulSoup as bs
import unidecode
import requests
import json
import re


def extract_course_name(soup):
    course = soup.find("meta", property="og:title")
    return course["content"]


def extract_prereq_info(soup):
    req_list = {}
    # Add back in when restriction parsing is figured out
    # subs = ["Prerequisite", "Corequisite", "Restriction"]
    subs = ["Prerequisite", "Corequisite"]
    for tag in soup.findAll("li"):
        tag = tag.get_text()
        for sub in subs:
            if sub in tag:
                # TODO: add identification of substitutes (i.e COMP 251 or ECSE 223)
                tag = tag.strip().replace(" ", "")
                req_list[sub] = re.findall(r"[A-Z]{4}\d{3}", tag)

    return req_list


def extract_course_instructors(soup):
    try:
        instructor_lst = (
            soup.find("p", class_="catalog-instructors")
            .get_text()
            .strip()
            .split(None, 1)[1]
        ).split(")")
    except:
        return None

    inst_dict = {}
    for inst in instructor_lst:
        a = inst.strip().split("(")
        if len(a) == 2:
            inst_dict[a[1].strip()] = unidecode.unidecode(a[0].strip())

    return inst_dict


def get_class_averages(averages_filename, course_name):
    with open(averages_filename, "r") as in_file:
        in_file = json.load(in_file)

    return in_file[course_name]


def group_info(soup):
    course_name = extract_course_name(soup)
    reqs_json = extract_prereq_info(soup)
    inst_json = extract_course_instructors(soup)
    avgs_json = get_class_averages("avgdata.json", course_name.replace(" ", ""))
    out_format = {
        "Course": course_name,
        "Instructors": inst_json,
        "Dependencies": reqs_json,
        "Grade Info": avgs_json,
    }

    return json.dumps(out_format, indent=4)


def export_json(group_info, out_file):
    with open(out_file, "w") as out:
        out.write(group_info)


def main():

    # lazy testing various functionalities

    flag = True

    if flag:
        with open("comp_251.txt", "r") as page_html:
            soup = bs(page_html, "html.parser")

    else:
        course_url = "https://www.mcgill.ca/study/2021-2022/courses/comp-360"
        out_name = "comp_202.txt"
        page_html = requests.get(course_url)
        soup = bs(page_html.text, "html.parser")

        with open(out_name, "a") as out_file:
            out_file.write(str(soup))

    info = group_info(soup)
    print(info)
    export_json(info, "comp202.json")


if __name__ == "__main__":
    main()
