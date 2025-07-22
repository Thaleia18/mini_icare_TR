import requests, string, re, nltk
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse


class UniversityScraper:
    def __init__(self, base_url):
        self.base_url = base_url
    #    self.visited = set()
            
            
    def get_soup(self, some_url):
        #it doesnt block with status code 403
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'}
        try:
            response = requests.get(some_url, headers=headers, timeout=20)
            #print(response.status_code)
            #print('sending request to', some_url)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
        except:          
            return None
  
  
    def find_link_in_soup(self, url, soup, list_conditions):
        possible_matches = []
        if not soup:
            return possible_matches
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True).lower()
            full_url = urljoin(url, href).lower()
            if all(cond(full_url, text) for cond in list_conditions):
                possible_matches.append(full_url)
        return possible_matches  
        
        
    def find_undergrad_url(self):
        soup = self.get_soup(self.base_url)
        possible_matches = self.find_link_in_soup(self.base_url, soup,[
                                 lambda  url, text: ('undergrad' in url),
                                 lambda  url, text: ('opendays' not in url and 'clearing' not in url)])
        possible_matches2 = self.find_link_in_soup(self.base_url, soup,[
                                 lambda  url, text: ('study' in url),
                                 lambda  url, text: ('opendays' not in url and 'clearing' not in url)]) 
        if not possible_matches and not possible_matches2:
            self.undergrad_url = None
            return self.undergrad_url
        #select one with shortest path
        elif possible_matches:
            best = min(possible_matches, key=lambda x: len(urlparse(x).path))
        else:
            best = min(possible_matches2, key=lambda x: len(urlparse(x).path))
        self.undergrad_url = best
        return self.undergrad_url


    def find_course_search_url(self):
        if self.undergrad_url is None:
            self.search_url = None
            return self.search_url
        if 'course' in self.undergrad_url.lower() or 'programme' in self.undergrad_url.lower():
            self.search_url = self.undergrad_url
            return self.search_url
        soup = self.get_soup(self.undergrad_url)
        title = soup.title.string.lower() if soup.title and soup.title.string else ""
        if 'course' in title:
            self.search_url = self.undergrad_url
            return self.search_url
        #first option search for a page that includes search as keyword
        #second option search for page that only includes courses or programmes
        possible_matches = self.find_link_in_soup(self.undergrad_url, soup,[
                             lambda  url, text: 'course' in url or 'course' in text
                                                or 'programme' in url or  'programme' in url, 
                             lambda  url, text: 'search' in url or 'query' in url or 'find' in url or
                                                'search' in text or 'query' in text or 'find' in text,
                             lambda  url, text: 'research' not in url and 'research' not in text 
                             and 'short' not in text and 'short' not in url,
                             lambda url,text: ('international' not in url and 'research' not in url 
                                               and 'clearing' not in url and'postgraduate' not in url and 'english' not in url)])
        possible_matches2 = self.find_link_in_soup(self.undergrad_url, soup,[
                             lambda  url, text: 'course' in url or 'programme' in url, 
                             lambda  url, text: 'research' not in url and 'research' not in text
                             and 'short' not in text and 'short' not in url,
                             lambda url,text: ('international' not in url and 'research' not in url 
                                               and 'clearing' not in url and'postgraduate' not in url and 'english' not in url)])
        if not possible_matches and not possible_matches2:
            self.search_url = None
            return self.search_url
        if possible_matches:
            best = min(possible_matches, key=lambda x: len(urlparse(x).path))
            self.search_url = best
            return self.search_url
        else:
            best = min(possible_matches2, key=lambda x: len(urlparse(x).path))
            self.search_url = best
            return self.search_url


    def _extract_courses(self, soup):
        degree_pattern = re.compile(r'(BA|BSc|BEng|LLB|BBA|MBBS|BMus|CertHE|DipHE|FdA|FdSc|BVMS|BVMSci|MEng|MSci|MA)(?![a-zA-Z])',re.IGNORECASE)
        all_courses = {}
        for a in soup.find_all('a', href=True):
            name = a.get_text(strip=True)
            matched = bool(degree_pattern.search(name))
            if matched:
                link = urljoin(self.search_url, a['href'])
                if name and name not in all_courses:  #this check is important because when organizing by subjects courses are repeated
                    all_courses[name] = link
        if len(all_courses)>5:
            return all_courses
        else:
            all_courses = {}
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text(strip=True).lower()
                full_url = href.lower()
                if ('listing' in full_url and 'course'in full_url) or ('degree' in full_url and 'programmes' in full_url):
                    all_courses[text] = full_url
            if len(all_courses)>5:
                return all_courses 
            else:
                return {}
        


    def get_all_courses(self):
        all_courses = {}
        if self.search_url==None:
            return {}
        soup = self.get_soup(self.search_url)
        if soup:
            all_courses.update(self._extract_courses(soup))    
        if all_courses:
            return all_courses
        else:
            possible_matches = self.find_link_in_soup(self.search_url, soup,[
                     lambda  url, text: 'course' in url or 'course' in text
                                        or 'programme' in url or  'programme' in url, 
                     lambda  url, text: 'undergraduate' in url,
                     lambda  url, text: 'a-z' in url or '2026' in url or
                                        'a-z' in text or '2026' in text,
                     lambda  url, text: 'research' not in url and 'research' not in text 
                     and 'short' not in text and 'short' not in url,
                     lambda url,text: ('international' not in url and 'research' not in url 
                                       and 'clearing' not in url and'postgraduate' not in url and 'english' not in url)])
            if possible_matches:
                best = min(possible_matches, key=lambda x: len(urlparse(x).path))
                self.search_url = best
                soup = self.get_soup(self.search_url)
                if soup:
                    all_courses.update(self._extract_courses(soup))  
                    if all_courses:
                        return all_courses
                    else:
                        return {}
            else:
                return {}
                

                 
                 
    def find_requirements_url(self):
        if self.undergrad_url is None:
            self.requirements_url = None
            return self.requirements_url
        soup = self.get_soup(self.undergrad_url)
        #search for requirements page
        possible_matches = self.find_link_in_soup(self.undergrad_url, soup, [
                                 lambda url,text: ('requirements' in text or 'requirements' in url or 
                                        'qualifications' in url),
                                 lambda url,text: ('international' not in url and 'research' not in url 
                                                    and 'clearing' not in url and'postgraduate' not in url 
                                                    and 'english' not in url)])
        #search for undergrad apply page
        possible_matches2 = self.find_link_in_soup(self.undergrad_url, soup, [
                                 lambda url,text: ('apply' in text or 'apply' in url),
                                 lambda url,text: ('international' not in url and 'research' not in url 
                                                    and 'clearing' not in url and'postgraduate' not in url 
                                                    and 'english' not in url)]) 
        if not possible_matches and not possible_matches2:
            self.requirements_url = None
            return self.requirements_url
        #if we found requirements link in undergrad save it
        elif possible_matches:
            best = min(possible_matches, key=lambda x: len(urlparse(x).path))
            self.requirements_url = best
            return self.requirements_url
        #go to apply page and search for link to requirements there
        else:
            self.apply_page = min(possible_matches2, key=lambda x: len(urlparse(x).path))
            soup = self.get_soup(self.apply_page)
            possible_matches_apply = self.find_link_in_soup(self.apply_page, soup, [
                                 lambda url,text: ('requirements' in text or 'requirements' in url or 
                                        'qualifications' in url or 'before' in url),
                                 lambda url,text: ('international' not in url and 'research' not in url 
                                                    and 'clearing' not in url and'postgraduate' not in url 
                                                    and 'english' not in url)])
            if possible_matches_apply:
                best = min(possible_matches_apply, key=lambda x: len(urlparse(x).path))
                self.requirements_url = best
                return self.requirements_url
            if "requirements" in soup.get_text().lower() or "qualifications" in soup.get_text().lower(): 
                self.requirements_url = self.apply_page
                return self.requirements_url
            self.requirements_url = None
            return self.requirements_url       
      
      
    def find_deadlines_url(self):
        if self.undergrad_url is None:
            self.deadlines_url = None
            return self.deadlines_url
        #check in undergrad_url for link to deadlines
        soup = self.get_soup(self.undergrad_url)
        possible_matches = self.find_link_in_soup(self.undergrad_url, soup, [
                                 lambda url,text: ('undergrad' in url and 'apply' in url),
                                 lambda url,text:('dates' in url or 'deadlines' in url or 'timeline' in url)])
        if possible_matches:
            best = min(possible_matches, key=lambda x: len(urlparse(x).path))
            self.deadlines_url = best
            return self.deadlines_url
        #lets try searching in apply page
        #first check if we already have the search page, if not make it
        if not hasattr(self, 'apply_page'):
            possible_matches = self.find_link_in_soup(self.undergrad_url, soup, [
                                lambda url,text: ('apply' in text or 'apply' in url),
                                lambda url,text: ('international' not in url and 'research' not in url 
                                               and 'clearing' not in url and'postgraduate' not in url and 'english' not in url)]) 
            #if we found apply page save it and crawl, else apply and deadlines pages are null
            if possible_matches:
                self.apply_page = min(possible_matches, key=lambda x: len(urlparse(x).path))
            else:
                self.deadlines_url = None
                self.apply_page = None
                return self.deadlines_url
        #crawl in apply page and search for deadlines
  #      print('crawling in apply page')
        soup = self.get_soup(self.apply_page)
        possible_matches = self.find_link_in_soup(self.apply_page, soup, [
                                 lambda url,text: ('undergrad' in url or 'apply' in url),
                                 lambda url,text:('dates' in url or 'deadlines' in url  or 'timeline' in url)])                                
        if possible_matches:
            best = min(possible_matches, key=lambda x: len(urlparse(x).path))
            self.deadlines_url = best
            return self.deadlines_url
        self.deadlines_url = None
        return self.deadlines_url
   
     
    def find_scolarships_url(self):
        if self.undergrad_url is None:
            self.scolarchips_url = None
            return self.scolarchips_url
        #check in undergrad_url for link to scolarship
        soup = self.get_soup(self.undergrad_url)
        possible_matches = self.find_link_in_soup(self.undergrad_url, soup, [
                            lambda url,text:('fund' in url or 'scolarchip' in url 
                            or 'fees' in url or 'costs' in url),
                            lambda url,text:('postgraduate'not in url or 'research' not in url
                            and 'fundraising' not in url)])
        if possible_matches:
            best = min(possible_matches, key=lambda x: len(urlparse(x).path))
            self.scolarchips_url = best
            return self.scolarchips_url
        self.scolarchips_url = None
        return self.scolarchips_url
  
  
    def course_scrapper(self, name, url):
        degree_pattern = re.compile(r'(BA|BSc|BEng|LLB|BBA|MBBS|BMus|CertHE|DipHE|FdA|FdSc|BVMS|BVMSci|MEng|MSci|MA)(?![a-zA-Z])',re.IGNORECASE)
        match = degree_pattern.search(name)
        def find_degrees_in_headers(soup):
            matches = []
            for header_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                for tag in soup.find_all(header_tag):
                    text = tag.get_text()
                    match = degree_pattern.search(text)
                    if match and match.group(0) not in matches:
                        matches.append(match.group(0))
            return matches       
        if not match:
            if len(name)==0 or 'a-z' in name:
                return {}
            else:
                clean_name = ' '.join(word.capitalize() for word in name.split())
                #print(clean_name)
                soup = self.get_soup(url)
                hons = ''
                possible_degree = ''
                if soup:
                    possible_degree = find_degrees_in_headers(soup)
        else:
            possible_degree = match.group(0)
            clean_name = name.replace(possible_degree,'')
            if re.search(r'\(Hons\)', name, re.IGNORECASE):
                hons = 'With Hons'
                clean_name = clean_name.replace('(Hons)','')
            else:
                hons = ''
        info = self.course_scrapper_key_info(name, url)
        if info =={}:
            info = self.extract_course_info_from_paragraphs(name, url)
        info['Name'] = clean_name.split('(')[0].strip()
        info['Hons'] = hons
        info['Degree'] = possible_degree
        info['URL'] = url
        if info['Degree']=='':
            degree_pattern = re.compile(
                r'\(?\b(BA|BSc|BEng|LLB|BBA|MBBS|BMus|CertHE|DipHE|FdA|FdSc|BVMS|BVMSci|MEng|MSci|MA)\b\)?',
                re.IGNORECASE)
            for value in info.values():
                degree_match = degree_pattern.search(value)
                if degree_match:
                    info["Degree"] = degree_match.group(1).upper()
                    break
        if type(info['Degree'])==list:
            value = info['Degree']
            info['Degree'] = ','.join(value)
        if 'UCAS code' in info.keys():
            if bool(re.fullmatch(r'[A-Z0-9]{4}', info['UCAS code'].upper()))==False:
                match = re.search(r'UCAS code[:\s]*([A-Z0-9]{4})', clean_name, re.IGNORECASE)
                if match:
                    info['UCAS code'] = match.group(1).upper()
                else:
                    info['UCAS code']==''
        if len(info['Name'])<5 or info['Degree']=='':
            info ={}
        return info

    def course_scrapper0(self, name, url):
        degree_pattern = re.compile(r'(BA|BSc|BEng|LLB|BBA|MBBS|BMus|CertHE|DipHE|FdA|FdSc|BVMS|BVMSci|MEng|MSci|MA)(?![a-zA-Z])',re.IGNORECASE)
        match = degree_pattern.search(name)
        def find_degrees_in_headers(soup):
            matches = []
            for header_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                for tag in soup.find_all(header_tag):
                    text = tag.get_text()
                    match = degree_pattern.search(text)
                    if match and match.group(0) not in matches:
                        matches.append(match.group(0))
            return matches       
        if not match:
            clean_name = ' '.join(word.capitalize() for word in name.split())
            soup = self.get_soup(url)
            hons = ''
            if not soup:
                return{}
            possible_degree = find_degrees_in_headers(soup)
            if not possible_degree:
                return {}
        else:
            possible_degree = match.group(0)
            clean_name = name.replace(possible_degree,'')
            if re.search(r'\(Hons\)', name, re.IGNORECASE):
                hons = 'With Hons'
                clean_name = clean_name.replace('(Hons)','')
            else:
                hons = ''
        info = self.course_scrapper_key_info(name, url)
        info['Name'] = clean_name
        info['Hons'] = hons
        info['Degree'] = possible_degree
        info['URL'] = url
        return info
        
        
    def course_scrapper_key_info(self, name, url):
        output = {}
        soup = self.get_soup(url)
        if not soup:
            return {}
        key_word_pattern = re.compile(r'\b(key|info|information|glance|overview)\b', re.IGNORECASE)
        info_keywords_groups = [
            ["Offer level", "Typical offer", "Offer"],
            ["UCAS code"],
            ["Course length", "Duration of study", "duration"],
            ["Start date"],
            ["Location", "Study at"],
            ["Deadline", "Apply before"]]
        headings = soup.find_all(re.compile('^h[1-6]$'))      
        # Compile regex patterns for each keyword group
        info_patterns_groups = [
            [re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE) for keyword in group]
            for group in info_keywords_groups]       
        # First keyword is the dict key label
        labels = [group[0] for group in info_keywords_groups]
        def search_keywords_in_element(element):
            lines = element.get_text(separator="\n", strip=True).splitlines()
            found_any = False
            for i, line in enumerate(lines):
                for group_idx, patterns in enumerate(info_patterns_groups):
                    for pattern in patterns:
                        if pattern.search(line):
                            # Extract value after keyword if present
                            parts = re.split(pattern, line)
                            value = None
                            if len(parts) > 1 and parts[1].strip():
                                value = parts[1].strip()
                            else:
                                if i + 1 < len(lines):
                                    next_line = lines[i + 1].strip()
                                    if next_line and not any(pat.search(next_line) for pats in info_patterns_groups for pat in pats):
                                        value = next_line
                            key = labels[group_idx]  # Always use first keyword as key
                            if value:
                                if key in output:
                                    if value not in output[key]:
                                        output[key] += ' ' + value
                                else:
                                    output[key] = value
                            else:
                                if key in output:
                                    if line.strip() not in output[key]:
                                        output[key] += ' ' + line.strip()
                                else:
                                    output[key] = line.strip()
                            found_any = True
                            break
            return found_any
        for heading in headings:
            heading_text = heading.get_text(separator=" ", strip=True)
            if key_word_pattern.search(heading_text):
                container = heading.parent
                if container and len(container.get_text(strip=True)) < 20:
                    container = container.parent if container.parent else container
                found_in_container = search_keywords_in_element(container)
                if not found_in_container:
                    next_sibling = container.next_sibling
                    while next_sibling:
                        if hasattr(next_sibling, 'get_text'):
                            found_in_sibling = search_keywords_in_element(next_sibling)
                            if found_in_sibling:
                                break
                        next_sibling = next_sibling.next_sibling
        return output


    def extract_course_info_from_paragraphs(self, name, url):
        soup = self.get_soup('https:'+url)
        if not soup:
            return {}
        output = {}       
        info_keywords_groups = [
            ["Offer level", "Typical offer", "Offer", "Entrance requirements"],
            ["UCAS code"],
            ["Course length", "Duration of study", "Course duration", "duration"],
            ["Start date"],
            ["Location", "Study at"],
            ["Deadline", "Apply before"]]
        labels = [group[0] for group in info_keywords_groups]
        info_patterns_groups = [[re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE) for keyword in group]
            for group in info_keywords_groups]
        key_word_pattern = re.compile(r'\b(key|info|information|glance|overview)\b', re.IGNORECASE)
        for heading in soup.find_all(re.compile('^h[1-6]$')):
            heading_text = heading.get_text(strip=True)
            if key_word_pattern.search(heading_text):
                sibling = heading.find_next_sibling()
                while sibling:
                    if sibling.name and sibling.name.startswith('h'):
                        break
                    if sibling.name == "p":
                        text = sibling.get_text(separator="\n", strip=True)
                        lines = text.split("\n")
                        for line in lines:
                            split_line = re.split(r":\s*", line, maxsplit=1)
                            if len(split_line) == 2:
                                key_text, value = split_line
                                for group_idx, patterns in enumerate(info_patterns_groups):
                                    for pattern in patterns:
                                        if pattern.search(key_text):
                                            key = labels[group_idx]
                                            if key in output:
                                                if value not in output[key]:
                                                    output[key] += ' ' + value
                                            else:
                                                output[key] = value
                                            break
                    sibling = sibling.find_next_sibling()
        return output


    def run(self):
        undergrad_url = self.find_undergrad_url()
        search_url = self.find_course_search_url()
        requirements_url = self.find_requirements_url()
        deadlines_url = self.find_deadlines_url()
        scolarships_url = self.find_scolarships_url()
        return self.undergrad_url, self.search_url, self.requirements_url, self.deadlines_url, self.scolarchips_url


    def extract_deadlines_info(self):
        year = 'YYYY'
        soup = self.get_soup(self.deadlines_url)
        if not soup:
            return None
        deadline_table = self.extract_deadline_table(soup)
        if deadline_table:
            return deadline_table
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)  # Replace all whitespace (including non-breaking) with regular space
        match = re.search(r'\b20\d{2} entry\b', text, re.IGNORECASE)
        if match:
            year = match.group(0).replace(' entry', '').strip()
        matches = []
        results = []
        date_regex = re.compile(
                r'\b(?:\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)(?:\s+\d{4})?'  # day month or day month year
                r'|'
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b',  # month year
                re.IGNORECASE)
        # Check headers
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            header_text = tag.get_text(strip=True)
            if date_regex.search(header_text):
                following_text = self.get_following_text(tag)
                matches.append(('header', header_text, following_text))
        # Check li items
        for li in soup.find_all('li'):
            text = li.get_text(strip=True)
            if date_regex.search(text):
                matches.append(('li', text,None))
        for tag_type, text, following_text in matches:
            if tag_type == 'li':
                match = date_regex.search(text)
                if match:
                    results.append([year, match.group(), text])
            else:
                if any(keyword in following_text.lower() for keyword in  ['ucas', 'deadline', 'decision', 'attend', 'apply','open','close','welcome','week']):
                    results.append([year, text, following_text])
        return results
    
    def get_following_text(self,tag):
        content = []
        for sibling in tag.find_next_siblings():
            if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                break  # Stop at the next header
            content.append(sibling.get_text(strip=True))
        return ' '.join(content).strip()
    
    def extract_deadline_table(self, soup):
        tables = soup.find_all('table')
        extracted_tables = []
        for table in tables:
            title = None    
            # Try to find <caption>
            caption = table.find("caption")
            if caption:
                title = caption.get_text(strip=True)
            else:
                # Try to find preceding <p class="panel-title">
                prev = table.find_previous(lambda tag: tag.name == "p" and "panel-title" in tag.get("class", []))
                if prev:
                    title = prev.get_text(strip=True)
                else:
                    # Fallback: try heading tag
                    prev_heading = table.find_previous(lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if prev_heading:
                        title = prev_heading.get_text(strip=True)
            year_match = re.search(r'\b(20\d{2})\b', title or '')
            year = year_match.group(1) if year_match else 'YYYY'
            if year == 'YYYY':
                for tr in table.find_all('tr'):
                    row_text = ' '.join(cell.get_text(strip=True) for cell in tr.find_all(['td','th'])).lower()
                    if 'welcome week' in row_text:
                        # Try to extract year from this row text
                        welcome_year_match = re.search(r'\b(20\d{2})\b', row_text)
                        if welcome_year_match:
                            year = welcome_year_match.group(1)
                            break
            rows = []
            for tr in table.find_all('tr'):
                cells = tr.find_all(['td', 'th'])
                row = [cell.get_text(strip=True) for cell in cells]
                row = [year]+row              
                row_str = ''.join(row).lower()
                if any(keyword in row_str for keyword in 
                    ['ucas', 'deadline', 'decision', 'attend', 'apply','open','close','welcome','week']):
                    extracted_tables.append(row)           
        return extracted_tables
        
