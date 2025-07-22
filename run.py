from thalia_webscrapper import UniversityScraper
from sqlite_code import *
import sqlite3

def add_univ(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname  # 'www.cam.ac.uk'
    if hostname.startswith("www."):
        hostname = hostname[4:]
    univ_name = hostname.split('.')[0]
    scrapper = UniversityScraper(url)
    undergrad_url, search_url, requirements_url, deadlines_url, scolarchips_url = scrapper.run()
    univ_values = (univ_name, url, undergrad_url, search_url, requirements_url, deadlines_url, scolarchips_url)
    add_university('univ_database.db', univ_values)  
    deadlines_info = scrapper.extract_deadlines_info()
    if deadlines_info:
        for deadline in deadlines_info:
            deadline_values = (univ_name, deadline[0],deadline[1],deadline[2])
            add_deadlines('univ_database.db', deadline_values)
    courses = scrapper.get_all_courses()
    if courses:
        for name, url in list(courses.items()):
            info = scrapper.course_scrapper(name, url)
            if info!={}:
                counter +=1
                cols = ['Name', 'Degree', 'Hons', 'URL', 'Offer level', 'UCAS code', 'Course length',
                        'Start date', 'Location','Deadline']
                course_values = (univ_name,) + tuple(info.get(i, None) for i in cols)
                add_courses('univ_database.db', course_values)
             
             
if __name__ == "__main__":

    uk_universities_urls = {
                            "University of Oxford": "https://www.ox.ac.uk",
                            "University of Cambridge": "https://www.cam.ac.uk",
                            "Imperial College London": "https://www.imperial.ac.uk",
                            "London School of Economics and Political Science": "https://www.lse.ac.uk",
                            "University College London": "https://www.ucl.ac.uk",
                            "University of Edinburgh": "https://www.ed.ac.uk",
                            "King’s College London": "https://www.kcl.ac.uk",
                            "University of Manchester": "https://www.manchester.ac.uk",
                            "University of Bristol": "https://www.bristol.ac.uk",
                            "University of Glasgow": "https://www.gla.ac.uk",
                            "University of Warwick": "https://warwick.ac.uk",
                            "University of Birmingham": "https://www.birmingham.ac.uk",
                            "University of Sheffield": "https://www.sheffield.ac.uk",
                            "University of Southampton": "https://www.southampton.ac.uk",
                            "University of Leeds": "https://www.leeds.ac.uk",
                            "University of Nottingham": "https://www.nottingham.ac.uk",
                            "University of York": "https://www.york.ac.uk",
                            "University of Exeter": "https://www.exeter.ac.uk",
                            "Durham University": "https://www.dur.ac.uk",
                            "University of Liverpool": "https://www.liverpool.ac.uk",
                            "Newcastle University": "https://www.ncl.ac.uk",
                            "Cardiff University": "https://www.cardiff.ac.uk",
                            "Queen Mary University of London": "https://www.qmul.ac.uk",
                            "University of Aberdeen": "https://www.abdn.ac.uk",
                            "University of Leicester": "https://le.ac.uk",
                            "University of Surrey": "https://www.surrey.ac.uk",
                            "University of East Anglia": "https://www.uea.ac.uk",
                            "Heriot-Watt University": "https://www.hw.ac.uk",
                            "Loughborough University": "https://www.lboro.ac.uk",
                            "University of Reading": "https://www.reading.ac.uk",
                            "University of Dundee": "https://www.dundee.ac.uk",
                            "Swansea University": "https://www.swansea.ac.uk",
                             "University of Strathclyde": "https://www.strath.ac.uk",
                            "University of Kent": "https://www.kent.ac.uk",
                            "University of Essex": "https://www.essex.ac.uk"
                        }

    counter = 0
    for univ_name, url in uk_universities_urls.items():
        print('doing ', univ_name)
        scrapper = UniversityScraper(url)
        undergrad_url, search_url, requirements_url, deadlines_url, scolarchips_url = scrapper.run()
        univ_values = (univ_name, url, undergrad_url, search_url, requirements_url, deadlines_url, scolarchips_url)
        add_university('univ_database.db', univ_values)  
        deadlines_info = scrapper.extract_deadlines_info()
        if deadlines_info:
            for deadline in deadlines_info:
                deadline_values = (univ_name, deadline[0],deadline[1],deadline[2])
                add_deadlines('univ_database.db', deadline_values)
        courses = scrapper.get_all_courses()
        if courses:
            for name, url in list(courses.items()):
                info = scrapper.course_scrapper(name, url)
                if info!={}:
                    counter +=1
                    cols = ['Name', 'Degree', 'Hons', 'URL', 'Offer level', 'UCAS code', 'Course length',
                            'Start date', 'Location','Deadline']
                    course_values = (univ_name,) + tuple(info.get(i, None) for i in cols)
                    add_courses('univ_database.db', course_values)
        
        print(counter)
        print('\n\n')
