class Entry:
	def __init__(self, preview_message, full_message, category, link_read_more):
		self.preview_message = preview_message
		self.full_message = full_message
		self.category = category
		self.link_read_more = link_read_more

	def __str__(self):
		return f"Preview message: {self.preview_message}\nFull message: {self.full_message}\nCategory: {self.category}\nLink read more: {self.link_read_more}\n\n"

	def __repr__(self):
		return self.__str__()