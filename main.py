import requests
import bs4
from models import Entry
from fake_useragent import UserAgent

URL_WEBSITE_STOIC = r"https://stoic.ucoz.net/blog/"
POSTFIX_URL_WEBSITE_STOIC = r"?page"

def parsing_page(url) -> list[Entry]:
	headers = {
		"User-Agent": UserAgent().random
	}
	response = requests.get(url, headers=headers, timeout=3)
	data_html = response.text
	soup = bs4.BeautifulSoup(data_html, "html.parser")
	all_entries = select_entries(soup)
	entries = []

	for entry in all_entries:
		preview_message = select_preview_message(entry)
		if preview_message:
			preview_message = preview_message.replace("Читать дальше »", "")
		category = select_details_category(entry)
		link_read_more = select_link_read_more(entry)



		if link_read_more:
			full_message = select_full_message(link_read_more)
		else:
			full_message = preview_message

		if is_access_new_entry([preview_message, full_message, category, link_read_more]):
			entry = Entry(preview_message, full_message, category, link_read_more)
			entries.append(entry)
			print(entry)
		
	return entries

def build_url(url, postfix, number_page):
	return f"{url}{postfix}{number_page}"

def build_list_url(url, postfix):

	response = requests.get(url)
	data_html = response.text
	soup = bs4.BeautifulSoup(data_html, "html.parser")
	count_page = select_count_page(soup)

	list_url = []
	for i in range(1, count_page + 1):
		temp_url = build_url(url, postfix, i)
		list_url.append(temp_url)
	return list_url

def is_access_new_entry(list_data):
	max_None = len(list_data)
	count_None = 0
	for data in list_data:
		if data is None:
			count_None += 1
	if count_None == max_None:
		return False
	else:
		return True

def select_count_page(soup) -> int:
	# https://stoic.ucoz.net/blog/?page2
	block_pages_count = soup.find("div", id="pagesBlock1")
	count_page = block_pages_count.find_all("a")[-2].text
	return int(count_page)

def select_entries(soup):
	all_entries = soup.find("div", id="allEntries")
	if all_entries:
		return all_entries
	else:
		return None

def select_details_category(entry):
	details = entry.find("div", class_="eDetails")
	if details:
		return details.find("span", class_="e-category").find("span", class_="ed-value").find("a").text
	else:
		return None

def select_link_read_more(entry):
	details = entry.find("div", class_="eMessage")
	if details:
		for p in details.find_all("p"):
			if p.find("span", class_="entryReadAll"):
				return f"https://stoic.ucoz.net{p.find('a', class_="entryReadAllLink").get('href')}"
		if details.find('a', class_="entryReadAllLink"):
			return f"https://stoic.ucoz.net{details.find('a', class_="entryReadAllLink").get('href')}"
	else:
		return None

def select_preview_message(entry):
	message = entry.find("div", class_="eMessage")
	if message:
		if message.find("p"):
			return message.find("p").text
		else:
			return None
	else:
		return None

def select_full_message(link_read_more):
	response = requests.get(link_read_more)
	data_html = response.text
	soup = bs4.BeautifulSoup(data_html, "html.parser")
	full_message = soup.find("div", id="content")
	data = []
	if full_message:
		for p in full_message.find_all("p"):
			data.append(p.text)
		data = "\n".join(data)
		return data
	else:
		return None

def get_entries() -> list[Entry]:
	list_url = build_list_url(URL_WEBSITE_STOIC, POSTFIX_URL_WEBSITE_STOIC)
	entries = []
	for url in list_url:
		try:
			entries.extend(parsing_page(url))
		except requests.exceptions.Timeout:
			print(f"error: {e}")
			sleep(5)
			entries.extend(parsing_page(url))

	return entries

def save_to_txt(entries:list[Entry], namefile:str):
	entries = sorted(entries, key=lambda x: x.category)
	with open(namefile, "w", encoding="utf-8") as file:
		for entry in entries:
			file.write(f"{entry.full_message}\n{entry.category}\n\n")

def save_to_docx():pass

def main():
	entries = get_entries()
	save_to_txt(entries, "entries.txt")


if __name__ == "__main__":
	main()
